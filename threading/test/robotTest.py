from Robot import Robot

def init():
    try:
        conn = Robot()
        conn.connect()
        conn.write("b0501000150".encode())
        conn.read()
        conn.write("f0501000150".encode())
        conn.read()
        conn.write("f0501000150".encode())
        conn.read()


    except Exception:
        conn.disconnect()

if __name__ == '__main__':
    init()
