import os

from Android import Android

def init():
    os.system("sudo hciconfig hci0 piscan")

    try:
        conn = Android()
        conn.connect()
        conn.write("Hello from Rpi")
        while True:
            conn.read()

    except Exception:
        conn.disconnect()

if __name__ == '__main__':
    init()
