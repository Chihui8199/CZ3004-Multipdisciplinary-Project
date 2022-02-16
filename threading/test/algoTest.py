from Algorithm import Algorithm

def init():
    try:
        conn = Algorithm()
        conn.connect()
        ## testing send streaming
        conn.write("Hello from Rpi")
        ## testing receive streaming
        # while True:
        #     conn.read()


    except Exception:
        conn.disconnect()

if __name__ == '__main__':
    init()
