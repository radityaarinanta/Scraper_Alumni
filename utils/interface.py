import os
import shutil

class CLI:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    @staticmethod
    def get_width():
        return shutil.get_terminal_size().columns

    @staticmethod
    def center_text(text, color=""):
        width = CLI.get_width()
        return f"{color}{text:^{width}}{CLI.RESET}"

    @staticmethod
    def header():
        os.system('cls' if os.name == 'nt' else 'clear')
        width = CLI.get_width()
        print(f"{CLI.BLUE}{'='*width}{CLI.RESET}")
        print(CLI.center_text("scraper alumni", CLI.BOLD + CLI.BLUE))
        print(f"{CLI.BLUE}{'='*width}{CLI.RESET}")

    @staticmethod
    def log_info(msg):
        print(CLI.center_text(f"[INFO] {msg}", CLI.BLUE))

    @staticmethod
    def log_success(msg):
        print(CLI.center_text(f"[✓] {msg}", CLI.GREEN))

    @staticmethod
    def log_warning(msg):
        print(CLI.center_text(f"[!] {msg}", CLI.YELLOW))

    @staticmethod
    def log_error(msg):
        print(CLI.center_text(f"[✕] {msg}", CLI.RED))

    @staticmethod
    def print_profile_card(name, category, company, location):
        width = CLI.get_width()
        card_w = 52
        pad = (width - card_w) // 2
        p = " " * pad
        
        print(f"{p}{CLI.BLUE}┌──────────────────────────────────────────────────┐{CLI.RESET}")
        print(f"{p}│ {CLI.BOLD}Alumni  :{CLI.RESET} {name[:36]:<36} │")
        print(f"{p}│ {CLI.BOLD}Status  :{CLI.RESET} {CLI.YELLOW}{category[:36]:<36}{CLI.RESET} │")
        print(f"{p}│ {CLI.BOLD}Kantor  :{CLI.RESET} {company[:36]:<36} │")
        print(f"{p}│ {CLI.BOLD}Lokasi  :{CLI.RESET} {location[:36]:<36} │")
        print(f"{p}{CLI.BLUE}└──────────────────────────────────────────────────┘{CLI.RESET}")
