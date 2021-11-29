import ctypes
import subprocess
import re

# Wallpapers And Their Paths
Image1 = r"C:\Users\user\Documents\People\Farzanul Chowdhury\Python\Automatic Wallpaper\Images\1.png"
Image2 = r"C:\Users\user\Documents\People\Farzanul Chowdhury\Python\Automatic Wallpaper\Images\2.png"

# Get The Name of The Montiors Active
proc = subprocess.Popen(['powershell', 'Get-WmiObject win32_desktopmonitor;'], stdout=subprocess.PIPE)
res = proc.communicate()
monitor = res[0].decode('utf-8')
print(monitor)
AvailableMonitor = f"z{monitor}z"


# Set The Wallpaper
if AvailableMonitor == "z['Generic PnP Monitor']z":
    ctypes.windll.user32.SystemParametersInfoW(20, 0 , Image1, 0)
else:
    ctypes.windll.user32.SystemParametersInfoW(20, 0 , Image2, 0)