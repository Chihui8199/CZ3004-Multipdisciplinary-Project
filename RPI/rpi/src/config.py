LOCALE = 'UTF-8'

# Android BT connection settings
RFCOMM_CHANNEL = 9
RPI_MAC_ADDR = 'B8:27:EB:99:A8:38' # TO BE CHANGED
UUID = '443559ba-b80f-4fb6-99d9-ddbcd6138fbd'
ANDROID_SOCKET_BUFFER_SIZE = 512

# Algorithm Wifi connection settings
WIFI_IP = '192.168.16.16'
WIFI_PORT = 8080
ALGORITHM_SOCKET_BUFFER_SIZE = 512

# Arduino USB connection settings
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

# Image Recognition Settings
STOPPING_IMAGE = 'stop_image_processing.png'

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
IMAGE_FORMAT = 'bgr'

BASE_IP = 'tcp://192.168.16.'
PORT = ':5555'

IMAGE_PROCESSING_SERVER_URLS = {
    'zakkii': BASE_IP + '54' + PORT,
    'wanyao': BASE_IP + '00' + PORT,
}
