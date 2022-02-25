# CZ3004 MDP RPi

Raspberry Pi Codebase for CZ3004 MDP

## Set Up on Raspberry Pi

- Working on Raspbian Jessie (2016-02-26), with Python version 3.4.2. Ensure that OpenCV 3.3.0 is installed as well.
- Ensure that `picamera` version is at 1.1.0 (`sudo pip3 install "picamera[array]" == 1.1.0`)  
- Ensure that `at-spi2-core` is installed (`sudo apt-get install at-spi2-core`)  

## To run RPi

- Change directory: `cd rpi`  
- Main Program: `python3 main.py`

Begins a multithread session that will establish communications with N7 Tablet, Robot and PC.

## Connecting a new bluetooth device

- `sudo hciconfig hci0 piscan`

## Miscellaneous

- to shut down RPi: [`sudo shutdown -h now`](https://raspberrypi.stackexchange.com/a/383)
- [additional reference for installing OpenCV](https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/)
- bluetooth [`sudo systemctl enable rfcomm`]
