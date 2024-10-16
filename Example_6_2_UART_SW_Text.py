import os
import termios
import time
from enum import IntEnum

# GPIO 핀 번호
SWITCH_PIN = 65

switch_state_cur = 0
switch_state_pre = 0
switch_event_flag = 0

# UART and SPI settings
UART_DEV = "/dev/ttyAMA2"

def gpio_setup_input(pin):
    # GPIO 핀을 내보내기 (export)
    with open("/sys/class/gpio/export", "w") as f:
        f.write(str(pin))
    
    # 핀 모드 설정 (출력)
    with open(f"/sys/class/gpio/gpio{pin}/direction", "w") as f:
        f.write("in")

def gpio_read(pin):
    if os.path.exists(f'/sys/class/gpio/gpio{pin}'):
        with open(f'/sys/class/gpio/gpio{pin}/value', 'r') as f:
            return int(f.read().strip())

# GPIO 초기화 및 모든 핀 설정
def setup_all_pins():
    gpio_setup_input(SWITCH_PIN)

# GPIO 해제 함수
# GPIO 핀이 이미 export되어 있는지 확인하고, 그렇다면 unexport
def gpio_cleanup(pin):
    if os.path.exists(f"/sys/class/gpio/gpio{pin}"):
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(pin))

# 모든 GPIO 해제
def cleanup_all_pins():
    gpio_cleanup(SWITCH_PIN)

class TCATTRS(IntEnum):
    IFLAG = 0
    OFLAG = 1
    CFLAG = 2
    LFLAG = 3
    ISPEED = 4
    OSPEED = 5

def uart_set_speed(fd:int, speed:int):
    baudrates = {
        115200: termios.B115200,
        57600: termios.B57600,
        38400: termios.B38400,
        19200: termios.B19200,
        9600: termios.B9600,
        4800: termios.B4800,
        2400: termios.B2400,
        1200: termios.B1200,
    }

    attrs = termios.tcgetattr(fd)
    attrs[TCATTRS.IFLAG] &= ~(termios.INPCK | termios.ISTRIP | termios.INLCR | termios.IGNCR | termios.ICRNL | termios.IXON)
    attrs[TCATTRS.ISPEED] = baudrates[speed]
    attrs[TCATTRS.OSPEED] = baudrates[speed]
    attrs[TCATTRS.CFLAG] &= ~termios.CSIZE
    attrs[TCATTRS.CFLAG] |= termios.CS8 | termios.CLOCAL | termios.CREAD
    attrs[TCATTRS.LFLAG] &= ~(termios.ICANON | termios.ECHO | termios.ECHOE | termios.ISIG)
    attrs[TCATTRS.OFLAG] &= ~termios.OPOST
    termios.tcsetattr(fd, termios.TCSANOW, attrs)

def uart_write_str(fd:int, data:str):
    os.write(fd, data.encode('utf-8'))

def uart_read_str(fd:int):
    return os.read(fd, 1024).decode('utf-8')

try:
    cleanup_all_pins()
    setup_all_pins()

    # UART setup
    fd = os.open(UART_DEV, os.O_RDWR | os.O_NOCTTY)
    uart_set_speed(fd, 115200)

    uart_write_str(fd, "Hello UART\n\r")
    
    while True:
        switch_state_cur = gpio_read(SWITCH_PIN)

        if switch_state_cur != switch_state_pre:
            if switch_state_cur == 0:
                data = "Pushed"
            elif switch_state_cur == 1:
                data = "wait"

            # Send data over UART
            uart_write_str(fd, "Switch State : ")
            uart_write_str(fd, data)
     #TODO

        switch_state_pre = switch_state_cur

except KeyboardInterrupt:
    print("프로그램 종료")
finally:
    os.close(fd)  # Close the UART connection
    