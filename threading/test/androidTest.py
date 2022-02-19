import os

from Android import Android

def init():
    os.system("sudo chmod o+rw /var/run/sdp")
    os.system("sudo hciconfig hci0 piscan")

    try:
        conn = Android()
        conn.connect()
        conn.write("Hello from Rpi by Group16")
        while True:
            conn.read()

    except Exception:
        conn.disconnect()

if __name__ == '__main__':
    init()
