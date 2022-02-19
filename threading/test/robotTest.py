from Robot import Robot

def init():
    try:
        conn = Robot()
        conn.connect()
        conn.write("b0501000150".encode())
        while True:
            conn.read()

    except Exception:
        conn.disconnect()

if __name__ == '__main__':
    init()
