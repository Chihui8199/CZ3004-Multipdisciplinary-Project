from Robot import Robot

def init():
    try:
        conn = Robot()
        conn.connect()
        conn.write("f0501000150".encode())
        conn.read()
        conn.write("f0101000100".encode())

    except Exception:
        conn.disconnect()

if __name__ == '__main__':
    init()
