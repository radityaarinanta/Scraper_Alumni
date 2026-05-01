import pandas as pd

class DataProcessor:
    @staticmethod
    def parse_identity(full_name):
        if pd.isna(full_name) or str(full_name).strip().lower() in ["", "nan"]:
            return "", ""
        
        parts = str(full_name).strip().split()
        if not parts: return "", ""
        if len(parts) == 1: return parts[0], ""
        if len(parts) == 2: return parts[0], parts[1]
        
        return " ".join(parts[:2]), " ".join(parts[2:])

    @staticmethod
    def identify_sector(headline, company, position):
        text = f"{headline} {company} {position}".lower()
        
        mapping = {
            "Academic / Education": ['guru', 'dosen', 'teacher', 'lecturer', 'sekolah', 'universitas', 'institute', 'politeknik', 'yayasan'],
            "Government / Civil Service": ['kementerian', 'dinas', 'pemerintah', 'pemkot', 'pemkab', 'pemprov', 'asn', 'cpns', 'puskesmas', 'rsud', 'polri', 'tni'],
            "State-Owned (BUMN)": ['bumn', 'telkom', 'pertamina', 'pln', 'pt kai', 'pelindo', 'angkasa pura', 'mandiri', 'bri', 'bni'],
            "Entrepreneur / Freelance": ['owner', 'founder', 'ceo', 'wirausaha', 'entrepreneur', 'self-employed', 'freelance'],
            "Internship / Student": ['intern', 'magang', 'asisten', 'student', 'mahasiswa']
        }
        
        for sector, keys in mapping.items():
            if any(k in text for k in keys):
                return sector
        
        if company == "Tidak dicantumkan" and position == "Tidak dicantumkan":
            return "N/A (No Work Data)"
            
        return "Private Sector (Swasta)"
