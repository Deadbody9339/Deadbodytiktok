#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
from typing import List, Dict, Optional

class TikTokMassReporter:
    def __init__(self, cookies: Dict[str, str]):
        """
        Initialize the TikTok reporter with cookies for authentication.
        
        :param cookies: Dictionary of cookies from your browser session
        """
        self.session = requests.Session()
        self.session.cookies.update(cookies)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_banner(self):
        """Print banner"""
        banner = r"""
  _______ _ _  _____ _______       _     _ _             
 |__   __(_) |/ ____|__   __|/\   | |   | (_)            
    | |   _| | | (___   | |  /  \  | | __| |_ _ __   ___ 
    | |  | | |  \___ \  | | / /\ \ | |/ _` | | '_ \ / _ \
    | |  | | | ____) | | |/ ____ \| | (_| | | | | |  __/
    |_|  |_|_|_____/  |_/_/    \_\_|\__,_|_|_| |_|\___|
        """
        print("\033[1;36m" + banner + "\033[0m")
        print("\033[1;33mTikTok Multiple Accounts Auto Reporter\033[0m")
        print("\033[1;32m----------------------------------------\033[0m\n")
    
    def check_cookies_valid(self) -> bool:
        """Check if cookies are still valid"""
        try:
            response = self.session.get("https://www.tiktok.com/api/user/detail/?uniqueId=tiktok")
            return response.status_code == 200
        except:
            return False
        
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Get user information by username.
        
        :param username: TikTok username without @
        :return: Dictionary with user info or None if not found
        """
        url = f"https://www.tiktok.com/api/user/detail/?uniqueId={username}"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"\033[1;31m[!] Error getting user info: {e}\033[0m")
        return None
    
    def report_account(self, user_id: str, reason: int = 1004) -> bool:
        """
        Report a TikTok account.
        
        :param user_id: The user ID to report
        :param reason: Reason code for reporting
        :return: True if report was successful, False otherwise
        """
        report_url = "https://www.tiktok.com/api/report/user/"
        
        payload = {
            "object_id": user_id,
            "owner_id": user_id,
            "reason": reason,
            "report_type": "user"
        }
        
        try:
            response = self.session.post(report_url, data=payload)
            if response.status_code == 200:
                result = response.json()
                return result.get('status_code', 0) == 0
        except Exception as e:
            print(f"\033[1;31m[!] Error reporting account: {e}\033[0m")
        return False
    
    def process_accounts(self, usernames: List[str], reason: int, delay: float = 10.0):
        """
        Process multiple accounts for reporting.
        
        :param usernames: List of TikTok usernames
        :param reason: Reason code for reporting
        :param delay: Delay between reports in seconds
        """
        success_count = 0
        fail_count = 0
        total = len(usernames)
        
        print(f"\033[1;34m[+] Starting to process {total} accounts\033[0m")
        print(f"\033[1;35m[~] Using delay: {delay} seconds between reports\033[0m\n")
        
        for i, username in enumerate(usernames, 1):
            username = username.strip().replace('@', '')
            if not username:
                continue
                
            print(f"\n\033[1;36m[+] Processing account {i}/{total}: @{username}\033[0m")
            
            # Get user info
            user_info = self.get_user_info(username)
            if not user_info or not user_info.get('userInfo'):
                print(f"\033[1;31m[!] Could not find user @{username}\033[0m")
                fail_count += 1
                continue
                
            user_id = user_info['userInfo']['user']['id']
            print(f"\033[1;32m[+] Found user ID: {user_id}\033[0m")
            
            # Report account
            if self.report_account(user_id, reason):
                print(f"\033[1;32m[✓] Successfully reported @{username}\033[0m")
                success_count += 1
            else:
                print(f"\033[1;31m[!] Failed to report @{username}\033[0m")
                fail_count += 1
                
            # Delay between requests
            if i < total:
                print(f"\033[1;35m[~] Waiting {delay} seconds...\033[0m")
                time.sleep(delay)
        
        print(f"\n\033[1;32m[+] Report summary:\033[0m")
        print(f"\033[1;32m    Successful reports: {success_count}\033[0m")
        print(f"\033[1;31m    Failed reports: {fail_count}\033[0m")
        print(f"\033[1;33m    Total processed: {total}\033[0m")

def load_cookies(file_path: str = "tiktok_cookies.json") -> Dict[str, str]:
    """Load cookies from JSON file"""
    try:
        with open(file_path, 'r') as f:
            cookies = json.load(f)
            if not isinstance(cookies, dict):
                raise ValueError("Cookies file should contain a JSON object")
            return cookies
    except FileNotFoundError:
        print("\033[1;31m[!] Error: cookies file not found!\033[0m")
        print("\033[1;33m[!] Please create a 'tiktok_cookies.json' file with your TikTok cookies.\033[0m")
        sys.exit(1)
    except Exception as e:
        print(f"\033[1;31m[!] Error loading cookies: {e}\033[0m")
        sys.exit(1)

def load_usernames(file_path: str = "usernames.txt") -> List[str]:
    """Load usernames from text file"""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("\033[1;31m[!] Error: usernames file not found!\033[0m")
        print("\033[1;33m[!] Please create a 'usernames.txt' file with one username per line.\033[0m")
        sys.exit(1)
    except Exception as e:
        print(f"\033[1;31m[!] Error loading usernames: {e}\033[0m")
        sys.exit(1)

def get_report_reason() -> int:
    """Get report reason from user input"""
    reasons = {
        '1': 1001,  # Illegal activities
        '2': 1002,  # Child abuse
        '3': 1003,  # Hate speech
        '4': 1004,  # Other
        '5': 1005,  # Suicide or self-harm
        '6': 1006,  # Fake account
        '7': 1007,  # Harassment or bullying
        '8': 1008   # Violent extremism
    }
    
    print("\n\033[1;35mSelect report reason:\033[0m")
    print("1. Illegal activities")
    print("2. Child abuse")
    print("3. Hate speech")
    print("4. Other (default)")
    print("5. Suicide or self-harm")
    print("6. Fake account")
    print("7. Harassment or bullying")
    print("8. Violent extremism")
    
    while True:
        choice = input("\n\033[1;34mEnter choice (1-8, default 4): \033[0m").strip() or '4'
        if choice in reasons:
            return reasons[choice]
        print("\033[1;31m[!] Invalid choice. Please try again.\033[0m")

def main():
    """Main function"""
    reporter = TikTokMassReporter(load_cookies())
    reporter.clear_screen()
    reporter.print_banner()
    
    # Check if cookies are valid
    if not reporter.check_cookies_valid():
        print("\033[1;31m[!] Invalid or expired cookies. Please update your cookies file.\033[0m")
        sys.exit(1)
    
    # Load usernames
    usernames = load_usernames()
    if not usernames:
        print("\033[1;31m[!] No usernames found in the file.\033[0m")
        sys.exit(1)
    
    # Get report reason
    reason = get_report_reason()
    
    # Get delay between reports
    try:
        delay = float(input("\n\033[1;34mEnter delay between reports in seconds (recommended 10+): \033[0m") or "10")
    except ValueError:
        print("\033[1;31m[!] Invalid delay. Using default 10 seconds.\033[0m")
        delay = 10.0
    
    # Confirm before starting
    print(f"\n\033[1;33m[!] About to report {len(usernames)} accounts with reason code {reason}")
    confirm = input("\033[1;31mAre you sure you want to continue? (y/n): \033[0m").lower()
    if confirm != 'y':
        print("\033[1;33m[!] Operation cancelled.\033[0m")
        sys.exit(0)
    
    # Start reporting
    reporter.process_accounts(usernames, reason, delay)

if __name__ == "__main__":
    main()
