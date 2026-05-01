import pandas as pd
import os
import time
import logging
from core.engine import ScraperEngine
from core.processor import DataProcessor
from utils.interface import CLI

logging.getLogger('apify_client').setLevel(logging.CRITICAL)

class MainApp:
    def __init__(self):
        self.source_path = 'data/source/alumni_data.xlsx'
        self.output_dir = 'data/results/'
        self.target_uni = "muhammadiyah malang"
        self.engine = None

    def start(self):
        CLI.header()
        
        token = input(f"{CLI.BLUE}Enter Access Token: {CLI.RESET}").strip()
        if not token: return
        
        self.engine = ScraperEngine(token)
        
        if not os.path.exists(self.source_path):
            CLI.log_error(f"Database tidak ditemukan di {self.source_path}")
            return

        df = pd.read_excel(self.source_path)
        CLI.log_info(f"Berhasil memuat {CLI.BOLD}{len(df)}{CLI.RESET} data alumni.")

        try:
            p1 = "Mulai dari baris ke- (1-{}): ".format(len(df))
            p2 = "Jumlah data yang diproses: "
            
            start_row = int(input(p1).strip())
            count = int(input(p2).strip())
        except ValueError:
            CLI.log_error("Input harus berupa angka dan tidak boleh kosong!")
            return
        
        chunk = df.iloc[start_row-1 : start_row-1+count]
        filename = f"{self.output_dir}Hasil_Profiling_Alumni_Baris_{start_row}_ke_{start_row+count-1}.csv"

        CLI.log_info(f"Proses dimulai... Output: {CLI.YELLOW}{os.path.basename(filename)}{CLI.RESET}\n")

        for i, (idx, row) in enumerate(chunk.iterrows(), 1):
            name = str(row.get('Nama Lulusan', ''))
            CLI.log_info(f"Searching [{i}/{len(chunk)}]: {CLI.BOLD}{name}{CLI.RESET}")

            fname, lname = DataProcessor.parse_identity(name)
            if not fname: continue

            results = self.engine.search_by_name(fname, lname)
            
            if isinstance(results, str):
                CLI.log_warning("API Limit tercapai atau Token salah.")
                new_t = input("Masukkan Token Baru (atau 'q' untuk berhenti): ")
                if new_t.lower() == 'q': break
                self.engine.refresh_client(new_t)
                results = self.engine.search_by_name(fname, lname)

            if not results or not isinstance(results, list):
                CLI.log_warning("Profil tidak ditemukan.")
                continue

            match_found = False
            for profile in results[:10]:
                edu_text = (str(profile.get('school', '')) + str(profile.get('education', '')) + str(profile.get('description', ''))).lower()
                
                if self.target_uni in edu_text:
                    data = self._extract_profile_details(profile, row)
                    
                    out_df = pd.DataFrame([data])
                    is_new = not os.path.exists(filename)
                    out_df.to_csv(filename, index=False, mode='a' if not is_new else 'w', header=is_new, encoding='utf-8')
                    
                    CLI.print_profile_card(
                        name=name,
                        category=data['Status Pekerjaan (Present)'],
                        company=data['Tempat Bekerja (Present)'],
                        location=data['Alamat Bekerja']
                    )
                    match_found = True
                    break
            
            if not match_found:
                print(CLI.center_text("× Bukan Alumni UMM.", CLI.RED))

        width = CLI.get_width()
        print(f"\n{CLI.GREEN}{'='*width}{CLI.RESET}")
        CLI.log_success(f"Pekerjaan Selesai! Data tersimpan di folder {CLI.YELLOW}data/results/{CLI.RESET}")
        print(f"{CLI.GREEN}{'='*width}{CLI.RESET}")

    def _extract_profile_details(self, item, row):
        headline = str(item.get('headline') or "Tidak dicantumkan")
        url = item.get('url') or item.get('linkedinUrl') or "Tidak dicantumkan"
        loc_data = item.get('location')
        loc_str = loc_data.get('linkedinText', "Tidak dicantumkan") if isinstance(loc_data, dict) else (str(loc_data) if loc_data else "Tidak dicantumkan")
        
        now = {"c": "Tidak dicantumkan", "p": "Tidak dicantumkan", "s": "Tidak Ada Pekerjaan Aktif", "u": "Tidak dicantumkan"}
        past = {"c": "Tidak dicantumkan", "p": "Tidak dicantumkan", "s": "Belum Pernah Bekerja", "u": "Tidak dicantumkan"}
        
        exp = item.get('experience') or []
        if exp and isinstance(exp, list):
            j1 = exp[0]
            c1 = j1.get('companyName', "Tidak dicantumkan")
            p1 = j1.get('position', "Tidak dicantumkan")
            u1 = j1.get('companyLinkedinUrl', "Tidak dicantumkan")
            
            end = j1.get('endDate')
            if end and 'year' in end and end['year'] < 2026:
                past.update({"c": f"{c1} (Resign {end['year']})", "p": p1, "s": DataProcessor.identify_sector(headline, c1, p1), "u": u1})
            else:
                now.update({"c": c1, "p": p1, "s": DataProcessor.identify_sector(headline, c1, p1), "u": u1})
                if len(exp) > 1:
                    j2 = exp[1]
                    c2 = j2.get('companyName', "Tidak dicantumkan")
                    p2 = j2.get('position', "Tidak dicantumkan")
                    if j2.get('endDate') and 'year' in j2.get('endDate'): c2 = f"{c2} (Resign {j2['endDate']['year']})"
                    past.update({"c": c2, "p": p2, "s": DataProcessor.identify_sector("", c2, p2), "u": j2.get('companyLinkedinUrl', "Tidak dicantumkan")})

        return {
            'Nama Lulusan': row.get('Nama Lulusan'), 'NIM': row.get('NIM'), 'Tahun Masuk': row.get('Tahun Masuk'),
            'Tanggal Lulus': row.get('Tanggal Lulus'), 'Fakultas': row.get('Fakultas'), 'Program Studi': row.get('Program Studi'),
            'Linkedin': url, 'Email': item.get('email') or "Tidak publik", 
            'Alamat Bekerja': loc_str,
            'Tempat Bekerja (Present)': now['c'], 'Posisi Jabatan (Present)': now['p'], 
            'Status Pekerjaan (Present)': now['s'], 'Sosmed Kantor (Present)': now['u'],
            'Tempat Bekerja (Terakhir)': past['c'], 'Posisi Jabatan (Terakhir)': past['p'], 
            'Status Pekerjaan (Terakhir)': past['s'], 'Sosmed Kantor (Terakhir)': past['u'],
            'Instagram': 'Tidak publik', 'TikTok': 'Tidak publik', 'Facebook': 'Tidak publik', 'Nomor HP': 'Tidak publik'
        }

if __name__ == "__main__":
    app = MainApp()
    app.start()
