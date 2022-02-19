import os
from MultiProcessComms import MultiProcessComms


def init():
    os.system("sudo chmod o+rw /var/run/sdp")
    os.system("sudo hciconfig hci0 piscan")

    try:
        multiprocess_communications = MultiProcessComms()
        multiprocess_communications.start()
    except Exception:
        multiprocess_communications.end()

if __name__ == '__main__':
    init()