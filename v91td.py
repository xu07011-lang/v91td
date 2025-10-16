import threading
import base64
import os
import time
import re
import requests
import socket
import sys
from time import sleep
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
from collections import deque, defaultdict, Counter
import random
import hashlib
import platform
import subprocess
import string
import urllib.parse
import itertools # Thêm thư viện này để dùng trong bộ logic mới
import statistics # Thêm thư viện này để dùng trong bộ logic mới


# Check và cài đặt các thư viện cần thiết
try:
    from colorama import init
    init(autoreset=True) # Vẫn giữ colorama init cho phần xác thực key
    import pytz
    from faker import Faker
    from requests import session
    # Thư viện Rich cho giao diện
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.align import Align
except ImportError:
    print('__Đang cài đặt thư viện nâng cấp, vui lòng chờ...__')
    os.system("pip install requests colorama pytz faker pystyle bs4 rich statistics")
    print('__Cài đặt hoàn tất, vui lòng chạy lại Tool__')
    sys.exit()

# =====================================================================================
# PHẦN 1: MÃ NGUỒN TỪ KEYV8.PY (LOGIC XÁC THỰC - GIỮ NGUYÊN)
# =====================================================================================

# CONFIGURATION FOR VIP KEY
VIP_KEY_URL = "https://raw.githubusercontent.com/DUONGKP2401/KEY-VIP.txt/main/KEY-VIP.txt"
VIP_CACHE_FILE = 'vip_cache.json'

# Encrypt and decrypt data using base64
def encrypt_data(data):
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data):
    return base64.b64decode(encrypted_data.encode()).decode()

# Colors for display (từ keyv8.py)
xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;39m"
end = '\033[0m'

# Đổi tên hàm banner của file banner.py để tránh xung đột
def authentication_banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner_text = f"""
{luc}████████╗ ██████╗░░ ██╗░░██╗░
{luc}╚══██╔══╝ ██╔══██╗░ ██║██╔╝░░
{luc}░░░██║░░░ ██║░░██║░ █████╔╝░░
{luc}░░░██║░░░ ██║░░██║░ ██╔═██╗░░
{luc}░░░██║░░░ ██║░░██║░ ██║░╚██╗░
{luc}░░░╚═╝░░░ ╚█████╔╝░ ╚═╝░░╚═╝░
{trang}══════════════════════════

{vang}Tool VIP V9
{trang}══════════════════════════
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        sleep(0.0001)

# DEVICE ID AND IP ADDRESS FUNCTIONS
def get_device_id():
    """Generates a stable device ID based on CPU information."""
    system = platform.system()
    try:
        if system == "Windows":
            cpu_info = subprocess.check_output('wmic cpu get ProcessorId', shell=True, text=True, stderr=subprocess.DEVNULL)
            cpu_info = ''.join(line.strip() for line in cpu_info.splitlines() if line.strip() and "ProcessorId" not in line)
        else:
            try:
                cpu_info = subprocess.check_output("cat /proc/cpuinfo", shell=True, text=True)
            except:
                cpu_info = platform.processor()
        if not cpu_info:
            cpu_info = platform.processor()
    except Exception:
        cpu_info = "Unknown"

    hash_hex = hashlib.sha256(cpu_info.encode()).hexdigest()
    only_digits = re.sub(r'\D', '', hash_hex)
    if len(only_digits) < 16:
        only_digits = (only_digits * 3)[:16]

    return f"DEVICE-{only_digits[:16]}"

def get_ip_address():
    """Gets the user's public IP address."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip_data = response.json()
        return ip_data.get('ip')
    except Exception as e:
        print(f"{do}Lỗi khi lấy địa chỉ IP: {e}{trang}")
        return None

def display_machine_info(ip_address, device_id):
    """Displays the banner, IP address, and Device ID."""
    authentication_banner() # Gọi hàm banner đã đổi tên
    if ip_address:
        print(f"{trang}[{do}<>{trang}] {do}Địa chỉ IP: {vang}{ip_address}{trang}")
    else:
        print(f"{do}Không thể lấy địa chỉ IP của thiết bị.{trang}")

    if device_id:
        print(f"{trang}[{do}<>{trang}] {do}Mã Máy: {vang}{device_id}{trang}")
    else:
        print(f"{do}Không thể lấy Mã Máy của thiết bị.{trang}")


# FREE KEY HANDLING FUNCTIONS
def luu_thong_tin_ip(ip, key, expiration_date):
    """Saves free key information to a json file."""
    data = {ip: {'key': key, 'expiration_date': expiration_date.isoformat()}}
    encrypted_data = encrypt_data(json.dumps(data))
    with open('ip_key.json', 'w') as file:
        file.write(encrypted_data)

def tai_thong_tin_ip():
    """Loads free key information from the json file."""
    try:
        with open('ip_key.json', 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def kiem_tra_ip(ip):
    """Checks for a saved free key for the current IP."""
    data = tai_thong_tin_ip()
    if data and ip in data:
        try:
            expiration_date = datetime.fromisoformat(data[ip]['expiration_date'])
            if expiration_date > datetime.now():
                return data[ip]['key']
        except (ValueError, KeyError):
            return None
    return None

def generate_key_and_url(ip_address):
    """Creates a free key and a URL to bypass the link."""
    ngay = int(datetime.now().day)
    key1 = str(ngay * 27 + 27)
    ip_numbers = ''.join(filter(str.isdigit, ip_address))
    key = f'TDK{key1}{ip_numbers}'
    expiration_date = datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)
    url = f'https://buffttfbinta.blogspot.com/2025/10/t.html?m={key}' # Link này có thể giữ nguyên hoặc thay đổi tùy admin
    return url, key, expiration_date

def get_shortened_link_phu(url):
    """Shortens the link to get the free key."""
    try:
        token = "6725c7b50c661e3428736919"
        api_url = f"https://link4m.co/api-shorten/v2?api={token}&url={url}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": "Không thể kết nối đến dịch vụ rút gọn URL."}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi rút gọn URL: {e}"}

def process_free_key(ip_address):
    """Handles the entire process of obtaining a free key."""
    url, key, expiration_date = generate_key_and_url(ip_address)

    with ThreadPoolExecutor(max_workers=1) as executor:
        yeumoney_future = executor.submit(get_shortened_link_phu, url)
        yeumoney_data = yeumoney_future.result()

    if yeumoney_data and yeumoney_data.get('status') == "error":
        print(yeumoney_data.get('message'))
        return False

    link_key_yeumoney = yeumoney_data.get('shortenedUrl')
    print(f'{trang}[{do}<>{trang}] {hong}Link Để Vượt Key Là {xnhac}: {link_key_yeumoney}{trang}')

    while True:
        keynhap = input(f'{trang}[{do}<>{trang}] {vang}Key Đã Vượt Là: {luc}')
        if keynhap == key:
            print(f'{luc}Key Đúng! Mời Bạn Dùng Tool{trang}')
            sleep(2)
            luu_thong_tin_ip(ip_address, keynhap, expiration_date)
            return True
        else:
            print(f'{trang}[{do}<>{trang}] {hong}Key Sai! Vui Lòng Vượt Lại Link {xnhac}: {link_key_yeumoney}{trang}')


# VIP KEY HANDLING FUNCTIONS
def save_vip_key_info(device_id, key, expiration_date_str):
    """Saves VIP key information to a local cache file."""
    data = {'device_id': device_id, 'key': key, 'expiration_date': expiration_date_str}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(VIP_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)
    print(f"{luc}Đã lưu thông tin Key VIP cho lần đăng nhập sau.{trang}")

def load_vip_key_info():
    """Loads VIP key information from the local cache file."""
    try:
        with open(VIP_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return None

def display_remaining_time(expiry_date_str):
    """Calculates and displays the remaining time for a VIP key."""
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%d/%m/%Y').replace(hour=23, minute=59, second=59)
        now = datetime.now()

        if expiry_date > now:
            delta = expiry_date - now
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            print(f"{xnhac}Key VIP của bạn còn lại: {luc}{days} ngày, {hours} giờ, {minutes} phút.{trang}")
        else:
            print(f"{do}Key VIP của bạn đã hết hạn.{trang}")
    except ValueError:
        print(f"{vang}Không thể xác định ngày hết hạn của key.{trang}")

def check_vip_key(machine_id, user_key):
    """Checks the VIP key from the URL on GitHub."""
    print(f"{vang}Đang kiểm tra Key VIP...{trang}")
    try:
        response = requests.get(VIP_KEY_URL, timeout=10)
        if response.status_code != 200:
            print(f"{do}Lỗi: Không thể tải danh sách key (Status code: {response.status_code}).{trang}")
            return 'error', None

        key_list = response.text.strip().split('\n')
        for line in key_list:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                key_ma_may, key_value, _, key_ngay_het_han = parts

                if key_ma_may == machine_id and key_value == user_key:
                    try:
                        expiry_date = datetime.strptime(key_ngay_het_han, '%d/%m/%Y')
                        if expiry_date.date() >= datetime.now().date():
                            return 'valid', key_ngay_het_han
                        else:
                            return 'expired', None
                    except ValueError:
                        continue
        return 'not_found', None
    except requests.exceptions.RequestException as e:
        print(f"{do}Lỗi kết nối đến server key: {e}{trang}")
        return 'error', None

# MAIN AUTHENTICATION FLOW
def main_authentication():
    ip_address = get_ip_address()
    device_id = get_device_id()
    display_machine_info(ip_address, device_id)
    key_info = {}

    if not ip_address or not device_id:
        print(f"{do}Không thể lấy thông tin thiết bị cần thiết. Vui lòng kiểm tra kết nối mạng.{trang}")
        return False, None, None

    cached_vip_info = load_vip_key_info()
    if cached_vip_info and cached_vip_info.get('device_id') == device_id:
        try:
            expiry_date = datetime.strptime(cached_vip_info['expiration_date'], '%d/%m/%Y')
            if expiry_date.date() >= datetime.now().date():
                print(f"{luc}Đã tìm thấy Key VIP hợp lệ, tự động đăng nhập...{trang}")
                display_remaining_time(cached_vip_info['expiration_date'])
                key_info = {'type': 'VIP', 'key': cached_vip_info['key'], 'expiry': cached_vip_info['expiration_date']}
                sleep(3)
                return True, device_id, key_info
            else:
                print(f"{vang}Key VIP đã lưu đã hết hạn. Vui lòng lấy hoặc nhập key mới.{trang}")
        except (ValueError, KeyError):
            print(f"{do}Lỗi file lưu key. Vui lòng nhập lại key.{trang}")

    if kiem_tra_ip(ip_address):
        print(f"{trang}[{do}<>{trang}] {hong}Key free hôm nay vẫn còn hạn. Mời bạn dùng tool...{trang}")
        key_info = {'type': 'Free', 'key': 'Free Daily', 'expiry': datetime.now().strftime('%d/%m/%Y')}
        time.sleep(2)
        return True, device_id, key_info

    while True:
        print(f"{trang}========== {vang}MENU LỰA CHỌN{trang} ==========")
        print(f"{trang}[{luc}1{trang}] {xduong}Nhập Key VIP{trang}")
        print(f"{trang}[{luc}2{trang}] {xduong}Lấy Key Free (Dùng trong ngày){trang}")
        print(f"{trang}======================================")

        try:
            choice = input(f"{trang}[{do}<>{trang}] {xduong}Nhập lựa chọn của bạn: {trang}")
            print(f"{trang}═══════════════════════════════════")

            if choice == '1':
                vip_key_input = input(f'{trang}[{do}<>{trang}] {vang}Vui lòng nhập Key VIP: {luc}')
                status, expiry_date_str = check_vip_key(device_id, vip_key_input)

                if status == 'valid':
                    print(f"{luc}Xác thực Key VIP thành công!{trang}")
                    save_vip_key_info(device_id, vip_key_input, expiry_date_str)
                    display_remaining_time(expiry_date_str)
                    key_info = {'type': 'VIP', 'key': vip_key_input, 'expiry': expiry_date_str}
                    sleep(3)
                    return True, device_id, key_info
                elif status == 'expired':
                    print(f"{do}Key VIP của bạn đã hết hạn. Vui lòng liên hệ admin.{trang}")
                elif status == 'not_found':
                    print(f"{do}Key VIP không hợp lệ hoặc không tồn tại cho mã máy này.{trang}")
                else:
                    print(f"{do}Đã xảy ra lỗi trong quá trình xác thực. Vui lòng thử lại.{trang}")
                sleep(2)

            elif choice == '2':
                if process_free_key(ip_address):
                    key_info = {'type': 'Free', 'key': 'Free Daily', 'expiry': datetime.now().strftime('%d/%m/%Y')}
                    return True, device_id, key_info
                else:
                    return False, None, None

            else:
                print(f"{vang}Lựa chọn không hợp lệ, vui lòng nhập 1 hoặc 2.{trang}")

        except (KeyboardInterrupt):
            print(f"\n{trang}[{do}<>{trang}] {do}Cảm ơn bạn đã dùng Tool !!!{trang}")
            sys.exit()


# =====================================================================================
# PHẦN 2: MÃ NGUỒN TOOL CHÍNH (NÂNG CẤP LÊN V13)
# =====================================================================================

console = Console()

NV = {
    1: 'Bậc thầy tấn công', 2: 'Quyền sắt', 3: 'Thợ lặn sâu',
    4: 'Cơn lốc sân cỏ', 5: 'Hiệp sĩ phi nhanh', 6: 'Vua home run'
}
ALL_NV_IDS = list(NV.keys())

# Lớp quản lý trạng thái chung (dùng cho việc tránh cược trùng)
class SharedStateManager:
    def __init__(self, api_endpoint, user_id):
        self.api_endpoint = api_endpoint
        self.user_id = user_id
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def get_shared_bets(self, issue_id):
        try:
            response = requests.get(f"{self.api_endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get(str(issue_id), {})
            return {}
        except (requests.RequestException, json.JSONDecodeError):
            return {}

    def claim_bet(self, issue_id, bet_on_char):
        try:
            response = requests.get(f"{self.api_endpoint}", timeout=5)
            data = {}
            if response.status_code == 200:
                try:
                    data = response.json()
                    if not isinstance(data, dict): data = {}
                except json.JSONDecodeError: data = {}
            
            current_issue_num = int(issue_id)
            keys_to_delete = [key for key in data.keys() if not key.isdigit() or int(key) < current_issue_num - 5]
            for key in keys_to_delete:
                del data[key]

            issue_key = str(issue_id)
            if issue_key not in data: data[issue_key] = {}
            
            data[issue_key][str(bet_on_char)] = self.user_id
            requests.put(f"{self.api_endpoint}", data=json.dumps(data), headers=self.headers, timeout=5)
            return True
        except Exception:
            return False

# =====================================================================================
# >> BỘ NÃO LOGIC V13 - NÂNG CẤP QUẢN LÝ RỦI RO <<
# =====================================================================================
class LogicEngineV13:
    def __init__(self, state_manager, history_min_size=20):
        self.history = deque(maxlen=200)
        self.state_manager = state_manager
        self.history_min_size = history_min_size
        self.logics = self._get_all_logics()
        self.rand = random.Random()
        
        # --- CƠ CHẾ CHỐNG CHUỖI THUA MỚI ---
        self.consecutive_losses = 0
        self.last_losing_char = None # Nhân vật gây ra trận thua gần nhất
        
        # Bộ logic cốt lõi dùng để phân tích đa luồng khi ở chế độ phòng thủ
        self.analysis_logics = [
            self.logic_001, # Tần suất toàn bộ
            self.logic_005, # Tần suất 20 ván gần nhất
            self.logic_011, # Lặp lại con vừa về
            self.logic_015, # Con số đã lặp lại gần đây
            self.logic_019, # Mode của 5 ván gần nhất
            self.logic_021, # Chuỗi Markov (con hay về sau con X nhất)
            self.logic_023, # Chuỗi Markov cặp
            self.logic_028, # Con hay về sau con có tần suất cao nhất
            self.logic_039, # Tổng 2 con cuối
            self.logic_051, # Con chẵn nhiều nhất
            self.logic_052, # Con lẻ nhiều nhất
            self.logic_082, # Con có chuỗi lặp dài nhất
        ]
        # --- KẾT THÚC CƠ CHẾ MỚI ---

    def add_result(self, winner_id):
        if winner_id in NV:
            self.history.append(winner_id)
            
    def update_with_result(self, bet_on_char, actual_winner):
        """Cập nhật trạng thái thua/thắng để kích hoạt chế độ phòng thủ."""
        if bet_on_char == actual_winner: # THUA (vì cược né mà lại trùng)
            self.consecutive_losses += 1
            self.last_losing_char = actual_winner # Lưu lại nhân vật gây thua
        else: # THẮNG
            self.consecutive_losses = 0
            self.last_losing_char = None # Reset khi thắng

    def _get_all_logics(self):
        return [getattr(self, f"logic_{i:03}") for i in range(1, 101)]

    # === BỘ 100 LOGICS (GIỮ NGUYÊN KHÔNG THAY ĐỔI) ===
    def safe_choice(self): return self.rand.choice(ALL_NV_IDS)
    def logic_001(self): return Counter(self.history).most_common(1)[0][0] if len(self.history) > 0 else self.safe_choice()
    def logic_002(self): return Counter(self.history).most_common()[-1][0] if len(self.history) > 0 else self.safe_choice()
    def logic_003(self): return Counter(list(self.history)[-10:]).most_common(1)[0][0] if len(self.history) >= 10 else self.logic_001()
    def logic_004(self): return Counter(list(self.history)[-10:]).most_common()[-1][0] if len(self.history) >= 10 else self.logic_002()
    def logic_005(self): return Counter(list(self.history)[-20:]).most_common(1)[0][0] if len(self.history) >= 20 else self.logic_003()
    def logic_006(self):
        seen = set(self.history)
        unseen = [c for c in ALL_NV_IDS if c not in seen]
        return self.rand.choice(unseen) if unseen else self.logic_002()
    def logic_007(self):
        if len(self.history) < 2: return self.safe_choice()
        c = Counter(self.history)
        second_most_common = c.most_common(2)
        return second_most_common[1][0] if len(second_most_common) > 1 else second_most_common[0][0]
    def logic_008(self):
        if len(self.history) < 2: return self.safe_choice()
        c = Counter(self.history)
        second_least_common = c.most_common()[-2] if len(c) > 1 else c.most_common()[-1]
        return second_least_common[0]
    def logic_009(self): return Counter(list(self.history)[-5:]).most_common(1)[0][0] if len(self.history) >= 5 else self.logic_001()
    def logic_010(self): return Counter(list(self.history)[-5:]).most_common()[-1][0] if len(self.history) >= 5 else self.logic_002()
    def logic_011(self): return self.history[-1] if len(self.history) > 0 else self.safe_choice()
    def logic_012(self): return self.history[-2] if len(self.history) > 1 else self.logic_011()
    def logic_013(self): return self.history[-3] if len(self.history) > 2 else self.logic_012()
    def logic_014(self): return self.history[0] if len(self.history) > 0 else self.safe_choice()
    def logic_015(self): return self.history[-1] if len(self.history) > 2 and self.history[-1] == self.history[-2] else self.logic_001()
    def logic_016(self): return 7 - self.history[-1] if len(self.history) > 0 else self.safe_choice() # Đối xứng
    def logic_017(self): return self.history[-1] if len(self.history) > 3 and self.history[-1] == self.history[-3] else self.logic_002()
    def logic_018(self):
        if len(self.history) < 6: return self.logic_011()
        return self.history[-6] # Lặp lại theo chu kỳ 6
    def logic_019(self):
        if len(self.history) < 5: return self.safe_choice()
        try: return statistics.mode(list(self.history)[-5:])
        except statistics.StatisticsError: return self.logic_011()
    def logic_020(self):
        if len(self.history) < 10: return self.safe_choice()
        try: return statistics.mode(list(self.history)[-10:])
        except statistics.StatisticsError: return self.logic_005()
    def logic_021(self): # Chuyển đổi đơn giản: cái gì hay theo sau X?
        if len(self.history) < 2: return self.safe_choice()
        last = self.history[-1]
        followers = [self.history[i+1] for i, v in enumerate(self.history) if i < len(self.history)-1 and v == last]
        return Counter(followers).most_common(1)[0][0] if followers else self.logic_011()
    def logic_022(self): # Chuyển đổi ngược: cái gì hay đứng trước X?
        if len(self.history) < 2: return self.safe_choice()
        last = self.history[-1]
        predecessors = [self.history[i] for i, v in enumerate(self.history) if i > 0 and v == last]
        return Counter(predecessors).most_common(1)[0][0] if predecessors else self.logic_012()
    def logic_023(self): # Chuyển đổi cặp: cái gì hay theo sau cặp X-Y?
        if len(self.history) < 3: return self.logic_021()
        last_pair = (self.history[-2], self.history[-1])
        followers = [self.history[i+2] for i in range(len(self.history) - 2) if (self.history[i], self.history[i+1]) == last_pair]
        return Counter(followers).most_common(1)[0][0] if followers else self.logic_021()
    def logic_024(self): return self.logic_021() # Alias for diversity
    def logic_025(self):
        if len(self.history) < 2: return self.safe_choice()
        last = self.history[-1]
        followers = [self.history[i+1] for i, v in enumerate(self.history) if i < len(self.history)-1 and v == last]
        return Counter(followers).most_common()[-1][0] if followers else self.logic_016() # Ít theo sau nhất
    def logic_026(self):
        if len(self.history) < 2: return self.safe_choice()
        c = Counter(zip(self.history, self.history[1:]))
        most_common_pair = c.most_common(1)[0][0]
        return most_common_pair[1] if c else self.logic_001()
    def logic_027(self):
        if len(self.history) < 10: return self.logic_021()
        last = self.history[-1]
        followers = [self.history[i+1] for i, v in enumerate(list(self.history)[-10:]) if i < 9 and v == last]
        return Counter(followers).most_common(1)[0][0] if followers else self.logic_021()
    def logic_028(self): # Cái gì hay theo sau số nhiều nhất
        if len(self.history) < 2: return self.safe_choice()
        most_common = self.logic_001()
        followers = [self.history[i+1] for i, v in enumerate(self.history) if i < len(self.history)-1 and v == most_common]
        return Counter(followers).most_common(1)[0][0] if followers else most_common
    def logic_029(self): # Cái gì hay theo sau số ít nhất
        if len(self.history) < 2: return self.safe_choice()
        least_common = self.logic_002()
        followers = [self.history[i+1] for i, v in enumerate(self.history) if i < len(self.history)-1 and v == least_common]
        return Counter(followers).most_common(1)[0][0] if followers else least_common
    def logic_030(self): return self.logic_023() # Alias for diversity
    def logic_031(self): return (self.history[-1] + 1 - 1) % 6 + 1 if len(self.history) > 0 else 1
    def logic_032(self): return (self.history[-1] + 2 - 1) % 6 + 1 if len(self.history) > 0 else 2
    def logic_033(self): return (self.history[-1] + 3 - 1) % 6 + 1 if len(self.history) > 0 else 3
    def logic_034(self): return (self.history[-1] - 2) % 6 + 1 if len(self.history) > 0 else 6
    def logic_035(self): return (self.history[-1] - 3) % 6 + 1 if len(self.history) > 0 else 5
    def logic_036(self): return (self.history[-1] * 2 -1) % 6 + 1 if len(self.history) > 0 else 4
    def logic_037(self): return (self.history[-1] * 3 -1) % 6 + 1 if len(self.history) > 0 else 3
    def logic_038(self): return abs(self.history[-1] - self.history[-2]) if len(self.history) > 1 and self.history[-1] != self.history[-2] else self.safe_choice()
    def logic_039(self): return (self.history[-1] + self.history[-2] - 1) % 6 + 1 if len(self.history) > 1 else self.logic_031()
    def logic_040(self): return (self.history[-1] + self.history[-2] + self.history[-3] - 1) % 6 + 1 if len(self.history) > 2 else self.logic_039()
    def logic_041(self): return (sum(self.history) -1) % 6 + 1 if self.history else 1
    def logic_042(self): return (self.history[-1] * self.history[-2] - 1) % 6 + 1 if len(self.history) > 1 else self.logic_036()
    def logic_043(self): return (self.history[-1] + self.history[0] - 1) % 6 + 1 if len(self.history) > 1 else self.logic_011()
    def logic_044(self): return (int(statistics.mean(self.history)) - 1) % 6 + 1 if len(self.history) > 2 else self.logic_041()
    def logic_045(self): return (int(statistics.median(self.history)) - 1) % 6 + 1 if len(self.history) > 2 else self.logic_044()
    def logic_046(self):
        if len(self.history) < 2: return self.safe_choice()
        return max(self.history[-1], self.history[-2]) - min(self.history[-1], self.history[-2]) or 6
    def logic_047(self): return (self.logic_001() + self.logic_002() - 1) % 6 + 1
    def logic_048(self): return (len(self.history) - 1) % 6 + 1
    def logic_049(self): return (self.history[-1]**2 - 1) % 6 + 1 if self.history else 1
    def logic_050(self): return (self.history[-1] + len(list(self.history)[-5:]) - 1) % 6 + 1 if self.history else 5
    def logic_051(self): # Con chẵn nhiều nhất
        evens = [h for h in self.history if h % 2 == 0]
        return Counter(evens).most_common(1)[0][0] if evens else 2
    def logic_052(self): # Con lẻ nhiều nhất
        odds = [h for h in self.history if h % 2 != 0]
        return Counter(odds).most_common(1)[0][0] if odds else 1
    def logic_053(self): # Con chẵn ít nhất
        evens = [h for h in self.history if h % 2 == 0]
        return Counter(evens).most_common()[-1][0] if evens else 4
    def logic_054(self): # Con lẻ ít nhất
        odds = [h for h in self.history if h % 2 != 0]
        return Counter(odds).most_common()[-1][0] if odds else 5
    def logic_055(self): # Nếu cuối là lẻ, chọn con chẵn nhiều nhất
        if not self.history: return self.safe_choice()
        return self.logic_051() if self.history[-1] % 2 != 0 else self.logic_052()
    def logic_056(self): # Nếu cuối là chẵn, chọn con lẻ nhiều nhất
        if not self.history: return self.safe_choice()
        return self.logic_052() if self.history[-1] % 2 == 0 else self.logic_051()
    def logic_057(self): # Số nhỏ (1,2,3) nhiều nhất
        smalls = [h for h in self.history if h <= 3]
        return Counter(smalls).most_common(1)[0][0] if smalls else 3
    def logic_058(self): # Số lớn (4,5,6) nhiều nhất
        bigs = [h for h in self.history if h > 3]
        return Counter(bigs).most_common(1)[0][0] if bigs else 4
    def logic_059(self): # Nếu cuối là số nhỏ, chọn số lớn nhiều nhất
        if not self.history: return self.safe_choice()
        return self.logic_058() if self.history[-1] <= 3 else self.logic_057()
    def logic_060(self): # Đảo ngược: nếu cuối là số nhỏ, chọn số nhỏ nhiều nhất
        if not self.history: return self.safe_choice()
        return self.logic_057() if self.history[-1] <= 3 else self.logic_058()
    def logic_061(self): # Vị trí cuối cùng của số 1 là ở đâu, lấy số tiếp theo
        if 1 not in self.history: return 1
        last_pos = len(self.history) - 1 - list(reversed(self.history)).index(1)
        return self.history[last_pos + 1] if last_pos < len(self.history) - 1 else self.logic_011()
    def logic_062(self): # Tương tự cho số 6
        if 6 not in self.history: return 6
        last_pos = len(self.history) - 1 - list(reversed(self.history)).index(6)
        return self.history[last_pos + 1] if last_pos < len(self.history) - 1 else self.logic_016()
    def logic_063(self): # Số ở vị trí đối xứng từ đầu
        if not self.history: return self.safe_choice()
        return self.history[-(len(self.history))]
    def logic_064(self): # Lấy số ở vị trí của con số cuối cùng
        if not self.history: return self.safe_choice()
        idx = self.history[-1] - 1
        return self.history[idx] if len(self.history) > idx else self.logic_011()
    def logic_065(self): # Vị trí đầu tiên của con số cuối cùng
        if not self.history: return self.safe_choice()
        first_pos = list(self.history).index(self.history[-1])
        return self.history[first_pos + 1] if first_pos < len(self.history) - 1 else self.logic_011()
    def logic_066(self):
        if len(self.history) < 10: return self.safe_choice()
        # Lấy con số ở vị trí median
        return sorted(list(self.history)[-10:])[4]
    def logic_067(self):
        # Số lần con số cuối cùng xuất hiện
        if not self.history: return self.safe_choice()
        count = self.history.count(self.history[-1])
        return count if count in ALL_NV_IDS else self.logic_011()
    def logic_068(self): # Trả về số lượng các số duy nhất đã xuất hiện
        unique_count = len(set(self.history))
        return unique_count if unique_count in ALL_NV_IDS else self.logic_006()
    def logic_069(self): # Lấy con số ở giữa lịch sử
        if not self.history: return self.safe_choice()
        mid_idx = len(self.history) // 2
        return self.history[mid_idx]
    def logic_070(self):
        if len(self.history) < 7: return self.safe_choice()
        return self.history[-7] # Chu kỳ 7
    def logic_071(self): return (self.logic_001() + self.logic_011() - 1) % 6 + 1
    def logic_072(self): return (self.logic_002() + self.logic_011() - 1) % 6 + 1
    def logic_073(self): return (self.logic_051() + self.logic_052() - 1) % 6 + 1
    def logic_074(self): return self.logic_021() if self.history and self.history[-1] % 2 == 0 else self.logic_022()
    def logic_075(self): return abs(self.logic_001() - self.logic_002()) or 6
    def logic_076(self): # Mode của 3 con cuối + 3 con đầu
        if len(self.history) < 6: return self.logic_019()
        sample = list(self.history)[:3] + list(self.history)[-3:]
        try: return statistics.mode(sample)
        except statistics.StatisticsError: return self.logic_001()
    def logic_077(self): return (self.logic_011() + self.logic_012() - 1) % 6 + 1
    def logic_078(self): # Lặp lại con số đã lặp lại gần nhất
        if len(self.history) < 2: return self.safe_choice()
        rev = list(reversed(self.history))
        for i in range(len(rev) - 1):
            if rev[i] == rev[i+1]: return rev[i]
        return self.logic_015()
    def logic_079(self): # Con số có khoảng cách xa nhất so với lần xuất hiện trước
        if len(self.history) < 10: return self.safe_choice()
        last_seen = {i: -1 for i in ALL_NV_IDS}
        max_gap, num_with_max_gap = -1, -1
        for i, num in enumerate(self.history):
            if last_seen[num] != -1:
                gap = i - last_seen[num]
                if gap > max_gap:
                    max_gap = gap
                    num_with_max_gap = num
            last_seen[num] = i
        return num_with_max_gap if num_with_max_gap != -1 else self.logic_006()
    def logic_080(self): return (self.logic_079() - 1) % 6 + 1
    def logic_081(self): # Trung bình của 3 con số cuối
        if len(self.history) < 3: return self.safe_choice()
        avg = sum(list(self.history)[-3:]) / 3
        return round(avg)
    def logic_082(self):
        # Tìm con số có chuỗi lặp dài nhất
        if not self.history: return self.safe_choice()
        longest_run, num_in_run = 0, -1
        for num, group in itertools.groupby(self.history):
            run_len = len(list(group))
            if run_len > longest_run:
                longest_run = run_len
                num_in_run = num
        return num_in_run if num_in_run != -1 else self.logic_011()
    def logic_083(self): return 7 - self.logic_082()
    def logic_084(self): return (self.logic_001() * self.history[-1] - 1) % 6 + 1 if self.history else self.safe_choice()
    def logic_085(self): return (self.logic_002() * self.history[-1] - 1) % 6 + 1 if self.history else self.safe_choice()
    def logic_086(self): return self.rand.choice([1,2,3])
    def logic_087(self): return self.rand.choice([4,5,6])
    def logic_088(self): return self.rand.choice([1,3,5])
    def logic_089(self): return self.rand.choice([2,4,6])
    def logic_090(self): return self.rand.choice([c for c in ALL_NV_IDS if c != self.history[-1]]) if self.history else self.safe_choice()
    def logic_091(self): return self.rand.choice([c for c in ALL_NV_IDS if c not in list(self.history)[-2:]]) if len(self.history)>1 else self.logic_090()
    def logic_092(self): return self.rand.choice([c for c in ALL_NV_IDS if c not in list(self.history)[-3:]]) if len(self.history)>2 else self.logic_091()
    def logic_093(self): # Ngẫu nhiên trong top 3 nhiều nhất
        if len(self.history) < 3: return self.safe_choice()
        top3 = [item[0] for item in Counter(self.history).most_common(3)]
        return self.rand.choice(top3)
    def logic_094(self): # Ngẫu nhiên trong top 3 ít nhất
        if len(self.history) < 3: return self.safe_choice()
        bottom3 = [item[0] for item in Counter(self.history).most_common()[-3:]]
        return self.rand.choice(bottom3)
    def logic_095(self): return self.rand.choice(ALL_NV_IDS)
    def logic_096(self): return self.logic_001()
    def logic_097(self): return self.logic_011()
    def logic_098(self): return self.logic_016()
    def logic_099(self): return self.logic_021()
    def logic_100(self): return self.logic_039()

    # =================== PHẦN NÂNG CẤP LOGIC V13 ===================
    def analyze_and_select(self, issue_id):
        candidate = None
        
        # --- Lấy thông tin cơ bản về tần suất ---
        least_frequent_char = self.logic_002() if len(self.history) > self.history_min_size else None
        
        # --- CHỌN LOGIC DỰA TRÊN TRẠNG THÁI THUA/THẮNG ---

        # TRẠNG THÁI 1: DEFENSE MODE (Vừa thua, cần gỡ, ưu tiên an toàn tuyệt đối)
        if self.consecutive_losses > 0:
            # Bước 1: Phân tích đa luồng để tìm ra các mối đe dọa (dự đoán con sẽ về)
            predictions = [logic() for logic in self.analysis_logics]
            threat_counts = Counter(predictions)
            
            # Sắp xếp các mối đe dọa từ cao đến thấp
            sorted_threats = [threat[0] for threat in threat_counts.most_common()]

            # Bước 2: Chọn ứng viên cược né dựa trên các quy tắc an toàn
            for threat in sorted_threats:
                # *** QUY TẮC #1: KHÔNG BAO GIỜ CƯỢC LẠI CON VỪA GÂY THUA ***
                if threat == self.last_losing_char:
                    continue # Bỏ qua mối đe dọa này, tìm con khác
                
                # *** QUY TẮC #2 (QUY TẮC KIM CƯƠNG): KHÔNG CƯỢC CON ÍT VỀ NHẤT ***
                if threat == least_frequent_char:
                    continue # Bỏ qua nếu nó là con có tần suất thấp nhất
                
                # Nếu vượt qua các quy tắc, đây là ứng viên tốt
                candidate = threat
                break

            # Fallback: Nếu tất cả các mối đe dọa đều vi phạm quy tắc (rất hiếm)
            if candidate is None:
                # Lấy tất cả các con, trừ con vừa gây thua và con ít về nhất
                safe_options = [c for c in ALL_NV_IDS if c != self.last_losing_char and c != least_frequent_char]
                if not safe_options: # Nếu chỉ còn 1-2 lựa chọn
                    safe_options = [c for c in ALL_NV_IDS if c != self.last_losing_char]
                
                candidate = self.rand.choice(safe_options if safe_options else ALL_NV_IDS)

        # TRẠNG THÁI 2: NORMAL MODE (Đang thắng, dùng logic xoay vòng để khó bị bắt bài)
        else:
            primary_logic = self.logics[issue_id % len(self.logics)]
            candidate = primary_logic()
            
            # Vẫn áp dụng quy tắc kim cương ở chế độ thường
            if candidate == least_frequent_char:
                candidate = self.logic_001() # Nếu logic chọn phải con yếu nhất, đổi sang con mạnh nhất
        
        # --- Xử lý cược trùng server và trả về kết quả cuối cùng ---
        shared_bets = self.state_manager.get_shared_bets(issue_id)
        claimed_chars = [int(k) for k in shared_bets.keys()]

        if candidate not in claimed_chars:
            self.state_manager.claim_bet(issue_id, candidate)
            return candidate
        else:
            # Lựa chọn chính đã bị người khác cược, tìm phương án thay thế
            available_options = [c for c in ALL_NV_IDS if c not in claimed_chars]
            if not available_options:
                final_choice = self.rand.choice(ALL_NV_IDS)
                self.state_manager.claim_bet(issue_id, final_choice)
                return final_choice

            # Ưu tiên các lựa chọn thay thế không phải là con yếu nhất
            preferred_options = [opt for opt in available_options if opt != least_frequent_char]
            
            final_choice = self.rand.choice(preferred_options if preferred_options else available_options)
            self.state_manager.claim_bet(issue_id, final_choice)
            return final_choice


# =====================================================================================
# PHẦN GIAO DIỆN VÀ HIỂN THỊ
# =====================================================================================
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def format_time(seconds):
    if seconds < 0: return "0 ngày 0 giờ 0 phút"
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days} ngày {hours} giờ {minutes} phút"

def add_log(logs_deque, message):
    hanoi_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    timestamp = datetime.now(hanoi_tz).strftime('%H:%M:%S')
    logs_deque.append(f"[grey70]{timestamp}[/grey70] {message}")

def generate_dashboard(config, stats, wallet_asset, logs, coin_type, status_message, key_info) -> Panel:
    total_games = stats['win'] + stats['lose']
    win_rate = (stats['win'] / total_games * 100) if total_games > 0 else 0
    profit = wallet_asset.get(coin_type, 0) - stats['asset_0']
    profit_str = f"[bold green]+{profit:,.4f}[/bold green]" if profit >= 0 else f"[bold red]{profit:,.4f}[/bold red]"

    stats_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    stats_table.add_column(style="cyan"); stats_table.add_column(style="white")
    stats_table.add_row("Phiên Bản", "[bold yellow]LOGIC V9[/bold yellow]") # <<<< ĐÃ NÂNG CẤP
    stats_table.add_row("Lợi Nhuận", f"{profit_str} {coin_type}")
    stats_table.add_row("Tổng Trận", str(total_games))
    stats_table.add_row("Thắng / Thua", f"[green]{stats['win']}[/green] / [red]{stats['lose']}[/red] ({win_rate:.2f}%)")
    stats_table.add_row("Chuỗi Thắng", f"[green]{stats['streak']}[/green] (Max: {stats['max_streak']})")
    stats_table.add_row("Chuỗi Thua", f"[red]{stats['lose_streak']}[/red]")
    lt_stats = stats['consecutive_loss_counts']
    stats_table.add_row("Tổng Thua L.Tiếp (1/2/3/4)", f"{lt_stats[1]} / {lt_stats[2]} / {lt_stats[3]} / {lt_stats[4]}")

    config_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    config_table.add_column(style="cyan"); config_table.add_column(style="yellow")
    config_table.add_row("Cược Cơ Bản", f"{config['bet_amount0']} {coin_type}")
    config_table.add_row("Hệ Số Gấp", str(config['heso']))
    config_table.add_row("Chế Độ Nghỉ", f"Chơi {config['delay1']} nghỉ {config['delay2']}")
    profit_target_str = f"{config['profit_target']}" if config['profit_target'] > 0 else "Không đặt"
    loss_limit_str = f"-[red]{abs(config['loss_limit'])}[/red]" if config['loss_limit'] > 0 else "Không đặt"
    config_table.add_row("Chốt Lãi", profit_target_str)
    config_table.add_row("Cắt Lỗ", loss_limit_str)
    
    balance_table = Table(title="Số Dư", show_header=True, header_style="bold magenta", box=None)
    balance_table.add_column("Loại Tiền", style="cyan", justify="left")
    balance_table.add_column("Số Lượng", style="white", justify="right")
    balance_table.add_row("BUILD", f"{wallet_asset.get('BUILD', 0.0):,.4f}")
    balance_table.add_row("WORLD", f"{wallet_asset.get('WORLD', 0.0):,.4f}")
    balance_table.add_row("USDT", f"{wallet_asset.get('USDT', 0.0):,.4f}")
    
    key_table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    key_table.add_column(style="cyan"); key_table.add_column(style="white")
    
    if key_info.get('type') == 'VIP':
        key_table.add_row("Loại Key", "[bold gold1]VIP[/bold gold1]")
        key_table.add_row("Key", f"[gold1]{key_info.get('key', 'N/A')}[/gold1]")
        key_table.add_row("Hạn Dùng", f"[yellow]{key_info.get('expiry', 'N/A')}[/yellow]")
    elif key_info.get('type') == 'Free':
        hcm_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(hcm_tz)
        midnight = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        delta = midnight - now
        
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        countdown = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        key_table.add_row("Loại Key", "[bold green]Free[/bold green]")
        key_table.add_row("Hết hạn vào", "[green]00:00:00 hàng ngày[/green]")
        key_table.add_row("Thời gian còn", f"[yellow]{countdown}[/yellow]")
    
    key_panel = Panel(key_table, title="[bold]Thông Tin Key[/bold]", border_style="blue")

    info_layout = Table.grid(expand=True)
    info_layout.add_column(ratio=1); info_layout.add_column(ratio=1)
    info_layout.add_row(Panel(stats_table, title="[bold]Thống Kê[/bold]", border_style="blue"), Panel(config_table, title="[bold]Cấu Hình[/bold]", border_style="blue"))
    info_layout.add_row(Panel(balance_table, border_style="blue"), key_panel)

    log_panel = Panel("\n".join(reversed(logs)), title="[bold]Nhật Ký Hoạt Động[/bold]", border_style="green", height=12)
    status_panel = Panel(Align.center(Text(status_message, justify="center")), title="[bold]Trạng Thái[/bold]", border_style="yellow", height=3)
    
    main_grid = Table.grid(expand=True)
    main_grid.add_row(status_panel)
    main_grid.add_row(info_layout)
    main_grid.add_row(log_panel)
    
    dashboard = Panel(
        main_grid,
        title=f"[bold gold1]TOOL VIP V9[/bold gold1] - Thời gian chạy: {format_time(time.time() - config['start_time'])}",
        border_style="bold magenta"
    )
    return dashboard

# =====================================================================================
# CÁC HÀM LOGIC VÀ API
# =====================================================================================
def load_data_cdtd():
    if os.path.exists('data-xw-cdtd.txt'):
        console.print(f"[cyan]Tìm thấy file dữ liệu đã lưu. Bạn có muốn sử dụng không? (y/n): [/cyan]", end='')
        if input().lower() == 'y':
            with open('data-xw-cdtd.txt', 'r', encoding='utf-8') as f: return json.load(f)
    console.print(f"\n[yellow]Hướng dẫn lấy link:\n1. Truy cập xworld.io và đăng nhập\n2. Vào game 'Chạy đua tốc độ'\n3. Copy link của trang game và dán vào đây[/yellow]")
    console.print(f"[cyan]📋 Vui lòng nhập link của bạn: [/cyan]", end=''); link = input()
    user_id = re.search(r'userId=(\d+)', link).group(1)
    secret_key = re.search(r'secretKey=([a-zA-Z0-9]+)', link).group(1)
    console.print(f"[green]    ✓ Lấy thông tin thành công! User ID: {user_id}[/green]")
    json_data = {'user-id': user_id, 'user-secret-key': secret_key}
    with open('data-xw-cdtd.txt', 'w+', encoding='utf-8') as f: json.dump(json_data, f, indent=4, ensure_ascii=False)
    return json_data

def populate_initial_history(s, headers, logic_engine):
    console.print(f"\n[green]Đang lấy dữ liệu lịch sử ban đầu (tối đa 100 ván)...[/green]")
    try:
        log_data = None
        recent_data = None

        log_req = s.get('https://api.sprintrun.win/sprint/lottery_log?page=1&limit=100', headers=headers, timeout=10)
        if log_req.status_code == 200:
            log_data = log_req.json()

        recent_req = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers, timeout=5)
        if recent_req.status_code == 200:
            recent_data = recent_req.json()
        else:
            console.print(f"[yellow]⚠️ API 'recent_10_issues' trả về mã lỗi: {recent_req.status_code}.[/yellow]")

        all_issues = {}

        if log_data and log_data.get('data', {}).get('list'):
            for issue_data in log_data['data']['list']:
                issue_id = int(issue_data['issue_id'])
                all_issues[issue_id] = issue_data['result'][0]

        if recent_data and recent_data.get('data', {}).get('recent_10'):
            for issue_data in recent_data['data']['recent_10']:
                issue_id = int(issue_data['issue_id'])
                if 'result' in issue_data and issue_data['result']:
                    all_issues[issue_id] = issue_data['result'][0]
        
        if not all_issues:
            console.print(f"[red]Không thể lấy được dữ liệu lịch sử từ bất kỳ API nào.[/red]")
            return False

        sorted_issue_ids = sorted(all_issues.keys())
        final_ids_to_load = sorted_issue_ids[-100:]

        for issue_id in final_ids_to_load:
            logic_engine.add_result(all_issues[issue_id])
        
        console.print(f"[green]✓ Nạp thành công lịch sử {len(final_ids_to_load)} ván gần nhất.[/green]")
        return True
        
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        console.print(f"[red]Lỗi khi nạp lịch sử: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Lỗi không xác định khi nạp lịch sử: {e}[/red]")
    return False

def fetch_latest_issue_info(s, headers):
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers, timeout=5).json()
        if response and response['data']['recent_10']:
            latest_issue = response['data']['recent_10'][0]; return latest_issue['issue_id'], latest_issue
    except Exception: return None, None
    return None, None

def check_issue_result(s, headers, kq, ki):
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers, timeout=5).json()
        for issue in response['data']['recent_10']:
            if int(issue['issue_id']) == int(ki):
                actual_winner = issue['result'][0]; return actual_winner != kq, actual_winner
    except Exception: return None, None
    return None, None

def user_asset(s, headers):
    try:
        json_data = {'user_id': int(headers['user-id']), 'source': 'home'}
        return s.post('https://wallet.3games.io/api/wallet/user_asset', headers=headers, json=json_data, timeout=5).json()['data']['user_asset']
    except Exception as e:
        console.print(f"[red]Lỗi khi lấy số dư: {e}. Thử lại...[/red]"); time.sleep(2); return user_asset(s, headers)

def bet_cdtd(s, headers, ki, kq, Coin, bet_amount, logs):
    try:
        bet_amount_randomized = round(bet_amount * random.uniform(0.995, 1.005), 8)
        json_data = {'issue_id': int(ki), 'bet_group': 'not_winner', 'asset_type': Coin, 'athlete_id': kq, 'bet_amount': bet_amount_randomized}
        response = s.post('https://api.sprintrun.win/sprint/bet', headers=headers, json=json_data, timeout=10).json()
        
        return response
    except requests.exceptions.RequestException as e:
        add_log(logs, f"[red]Lỗi mạng khi đặt cược:[/red] [white]{e}[/white]")
        return None

def get_user_input(prompt, input_type=float):
    while True:
        try:
            console.print(prompt, end="")
            value = input_type(input())
            return value
        except ValueError:
            console.print("[bold red]Định dạng không hợp lệ, vui lòng nhập lại một số.[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Đã xảy ra lỗi: {e}. Vui lòng thử lại.[/bold red]")

# Vòng lặp chính của tool
def main_cdtd(device_id, key_info):
    s = requests.Session()
    data = load_data_cdtd()
    headers = {'user-id': data['user-id'], 'user-secret-key': data['user-secret-key'], 'user-agent': 'Mozilla/5.0'}

    clear_screen()
    
    asset = user_asset(s, headers)
    console.print(f"[cyan]Chọn loại tiền bạn muốn chơi:[/cyan]\n  1. USDT\n  2. BUILD\n  3. WORLD")
    while True:
        console.print(f'[cyan]Nhập lựa chọn (1/2/3): [/cyan]', end="")
        x = input()
        if x in ['1', '2', '3']: Coin = ['USDT', 'BUILD', 'WORLD'][int(x)-1]; break
        else: console.print(f"[red]Lựa chọn không hợp lệ, vui lòng nhập lại...[/red]")

    bet_amount0 = get_user_input(f'[cyan]Nhập số {Coin} muốn đặt ban đầu: [/cyan]', float)
    heso = get_user_input(f'[cyan]Nhập hệ số cược sau khi thua: [/cyan]', int)
    delay1 = get_user_input(f'[cyan]Chơi bao nhiêu ván thì nghỉ (999 nếu không nghỉ): [/cyan]', int)
    delay2 = get_user_input(f'[cyan]Nghỉ trong bao nhiêu ván: [/cyan]', int)
    profit_target = get_user_input(f'[cyan]Chốt lãi tại bao nhiêu {Coin} (nhập 0 để bỏ qua): [/cyan]', float)
    loss_limit = get_user_input(f'[cyan]Cắt lỗ tại bao nhiêu {Coin} (nhập số dương, ví dụ 50. Nhập 0 để bỏ qua): [/cyan]', float)

    
    SHARED_API_ENDPOINT = "https://api.jsonblob.com/api/jsonBlob/1286918519102373888"
    user_unique_id = hashlib.sha256(device_id.encode()).hexdigest()[:8]
    state_manager = SharedStateManager(SHARED_API_ENDPOINT, user_unique_id)
    logic_engine = LogicEngineV13(state_manager) # <<< SỬ DỤNG BỘ LOGIC MỚI

    stats = {
        'win': 0, 'lose': 0, 'streak': 0, 'max_streak': 0, 'lose_streak': 0, 
        'asset_0': asset.get(Coin, 0), 'consecutive_loss_counts': defaultdict(int)
    }
    config = {
        'bet_amount0': bet_amount0, 'heso': heso, 'delay1': delay1, 'delay2': delay2, 
        'start_time': time.time(), 'profit_target': profit_target, 'loss_limit': loss_limit
    }
    logs = deque(maxlen=10); tong_van = 0; post_loss_rest_counter = 0
    attempted_bets = deque(maxlen=100)

    populate_initial_history(s, headers, logic_engine); time.sleep(2)
    last_known_id, _ = fetch_latest_issue_info(s, headers)
    if not last_known_id:
        console.print(f"[red]Không thể lấy ID ván đầu tiên. Vui lòng kiểm tra lại mạng và API.[/red]")
        sys.exit()

    with Live(generate_dashboard(config, stats, asset, logs, Coin, "", key_info), console=console, screen=True, auto_refresh=False) as live:
        while True:
            try:
                current_asset = user_asset(s, headers)
                
                # === KIỂM TRA CHỐT LÃI/CẮT LỖ ===
                profit = current_asset.get(Coin, 0) - stats['asset_0']
                if profit_target > 0 and profit >= profit_target:
                    live.stop()
                    console.print(f"\n[bold green]✓✓✓ ĐÃ ĐẠT MỤC TIÊU CHỐT LÃI! Lợi nhuận: +{profit:,.4f} {Coin}. Tool tự động dừng.[/bold green]")
                    sys.exit()
                if loss_limit > 0 and profit <= -abs(loss_limit):
                    live.stop()
                    console.print(f"\n[bold red]XXX ĐÃ CHẠM MỨC CẮT LỖ! Lỗ: {profit:,.4f} {Coin}. Tool tự động dừng.[/bold red]")
                    sys.exit()

                status_msg = f"Đang chờ ván #{last_known_id + 1} bắt đầu..."
                live.update(generate_dashboard(config, stats, current_asset, logs, Coin, status_msg, key_info), refresh=True)

                newly_completed_id = last_known_id
                while newly_completed_id == last_known_id:
                    time.sleep(1)
                    newly_completed_id, newly_completed_issue_data = fetch_latest_issue_info(s, headers)
                    if newly_completed_id is None: newly_completed_id = last_known_id

                last_known_id = newly_completed_id
                if newly_completed_issue_data and 'result' in newly_completed_issue_data:
                    logic_engine.add_result(newly_completed_issue_data['result'][0])
                
                # === CƠ CHẾ NGHỈ 3 VÁN SAU KHI THUA ===
                if post_loss_rest_counter > 0:
                    rest_msg = f"[yellow]💤 Nghỉ ngơi sau thua. Còn lại {post_loss_rest_counter} ván. Đang theo dõi KQ...[/yellow]"
                    add_log(logs, rest_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, rest_msg, key_info), refresh=True)
                    post_loss_rest_counter -= 1
                    time.sleep(30) # Chờ khoảng thời gian của 1 ván
                    continue

                tong_van += 1
                bet_amount = bet_amount0 * (heso ** stats['lose_streak'])

                cycle = delay1 + delay2
                pos = (tong_van - 1) % cycle if cycle > 0 else 0
                is_resting = pos >= delay1
                
                if not is_resting and random.random() < 0.05:
                    rest_msg = f"[yellow]💤 Bỏ qua ván này ngẫu nhiên để thay đổi hành vi.[/yellow]"
                    add_log(logs, rest_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, rest_msg, key_info), refresh=True)
                    time.sleep(30); continue

                if is_resting:
                    rest_msg = f"[yellow]💤 Tạm nghỉ. Tiếp tục sau {cycle - pos} ván nữa.[/yellow]"
                    add_log(logs, rest_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, rest_msg, key_info), refresh=True)
                    time.sleep(30); continue

                pre_bet_delay = random.uniform(2, 5)
                time.sleep(pre_bet_delay)

                final_check_id, _ = fetch_latest_issue_info(s, headers)
                if final_check_id is None:
                    add_log(logs, "[yellow]⚠️ Lỗi API, bỏ qua ván này[/yellow]")
                    time.sleep(5)
                    continue
                
                current_betting_issue_id = final_check_id + 1

                if current_betting_issue_id in attempted_bets:
                    log_msg = f"[yellow]⚠️ Đã thử cược ván #{current_betting_issue_id}. Bỏ qua cược lặp.[/yellow]"
                    add_log(logs, log_msg)
                    live.update(generate_dashboard(config, stats, current_asset, logs, Coin, log_msg, key_info), refresh=True)
                    time.sleep(10)
                    continue

                attempted_bets.append(current_betting_issue_id)
                
                if logic_engine.consecutive_losses > 0:
                    status_prefix = f"[bold red]PHÒNG THỦ (Cấm cược {logic_engine.last_losing_char})[/bold red] "
                else:
                    status_prefix = "[bold green]BÌNH THƯỜNG[/bold green] "
                add_log(logs, status_prefix + f"Phân tích ván cược #{current_betting_issue_id}...")

                kq = logic_engine.analyze_and_select(current_betting_issue_id)
                response = bet_cdtd(s, headers, current_betting_issue_id, kq, Coin, bet_amount, logs)
                
                if response and response.get('code') == 0:
                    start_wait_time = time.time()
                    while True:
                        result, actual_winner = check_issue_result(s, headers, kq, current_betting_issue_id)
                        if result is not None: break
                        elapsed = int(time.time() - start_wait_time)
                        wait_message = f"⏳ Đợi KQ kì #{current_betting_issue_id}: {elapsed}s '{NV.get(kq, kq)}'.      với [yellow]{bet_amount:,.4f} {Coin}[/yellow]"
                        live.update(generate_dashboard(config, stats, current_asset, logs, Coin, wait_message, key_info), refresh=True)
                        time.sleep(1)

                    if result: # THẮNG
                        stats['win'] += 1; stats['streak'] += 1; stats['lose_streak'] = 0
                        stats['max_streak'] = max(stats['max_streak'], stats['streak'])
                        log_msg = (f"[bold green]THẮNG[/bold green] - Cược né [white]'{NV.get(kq, kq)}'[/white], KQ về '[cyan]{NV.get(actual_winner, actual_winner)}[/cyan]'")
                    else: # THUA
                        stats['lose'] += 1; stats['lose_streak'] += 1; stats['streak'] = 0
                        stats['consecutive_loss_counts'][stats['lose_streak']] += 1
                        post_loss_rest_counter = 3 # <<< KÍCH HOẠT NGHỈ 3 VÁN
                        log_msg = (f"[bold red]THUA[/bold red] - Cược né [white]'{NV.get(kq, kq)}'[/white], KQ về '[red]{NV.get(actual_winner, actual_winner)}[/red]' (Trùng)")
                    
                    logic_engine.update_with_result(kq, actual_winner)
                    
                    add_log(logs, log_msg)
                
                else:
                    if response:
                        log_msg = f"[red]Lỗi cược ván #{current_betting_issue_id}:[/red] [white]{response.get('msg', 'Không rõ lỗi')}[/white]"
                        add_log(logs, log_msg)
                
                final_asset = user_asset(s, headers)
                live.update(generate_dashboard(config, stats, final_asset, logs, Coin, "", key_info), refresh=True)
                time.sleep(random.uniform(5, 10))

            except Exception as e:
                import traceback; error_message = traceback.format_exc()
                add_log(logs, f"[bold red]Lỗi nghiêm trọng. Sẽ thử lại sau 10s[/bold red]")
                time.sleep(10)

def show_banner():
    clear_screen()
    banner_text = Text.from_markup(f"""
[bold cyan]
 ████████╗██████╗ ██╗  ██╗
 ╚══██╔══╝██╔══██╗██║ ██╔╝
    ██║   ██║  ██║█████╔╝
    ██║   ██║  ██║██╔═██╗
    ██║   ██████╔╝██║  ██╗
    ╚═╝   ╚═════╝ ╚═╝  ╚═╝
[/bold cyan]
    """, justify="center")
    console.print(Panel(banner_text, border_style="magenta"))
    console.print(Align.center("[bold gold1]Tool VIP V9 - Khởi tạo thành công![/bold gold1]\n"))
    time.sleep(3)


if __name__ == "__main__":
    authentication_successful, device_id, key_info = main_authentication()

    if authentication_successful:
        show_banner()
        main_cdtd(device_id, key_info)
    else:
        print(f"\n{do}Xác thực không thành công. Vui lòng chạy lại tool.{end}")
        sys.exit()