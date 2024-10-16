import os
import termios
import time
from enum import IntEnum

# GPIO 핀 번호 리스트
GPIO_PINS = [83, 84, 112, 113, 117, 118, 120, 121]
SWITCH_PIN_1 = 65
SWITCH_PIN_2 = 66

switch1_value_pre = 0
switch1_value_cur = 0
switch1_event_flag = 0

switch2_value_pre = 0
switch2_value_cur = 0
switch2_event_flag = 0

index = 0

# GPIO 초기화 함수
def gpio_setup_output(pin):
    # GPIO 핀을 내보내기 (export)
    with open("/sys/class/gpio/export", "w") as f:
        f.write(str(pin))
    
    # 핀 모드 설정 (출력)
    with open(f"/sys/class/gpio/gpio{pin}/direction", "w") as f:
        f.write("out")

def gpio_setup_input(pin):
    # GPIO 핀을 내보내기 (export)
    with open("/sys/class/gpio/export", "w") as f:
        f.write(str(pin))
    
    # 핀 모드 설정 (출력)
    with open(f"/sys/class/gpio/gpio{pin}/direction", "w") as f:
        f.write("in")

# GPIO 상태 쓰기 함수
def gpio_write(pin, value):
    with open(f"/sys/class/gpio/gpio{pin}/value", "w") as f:
        f.write(str(value))

def gpio_read(pin):
    if os.path.exists(f'/sys/class/gpio/gpio{pin}'):
        with open(f'/sys/class/gpio/gpio{pin}/value', 'r') as f:
            return int(f.read().strip())

# GPIO 초기화 및 모든 핀 설정
def setup_all_pins():
    for pin in GPIO_PINS:
        gpio_setup_output(pin)

    gpio_setup_input(SWITCH_PIN_1)
    gpio_setup_input(SWITCH_PIN_2)

# GPIO 해제 함수
# GPIO 핀이 이미 export되어 있는지 확인하고, 그렇다면 unexport
def gpio_cleanup(pin):
    if os.path.exists(f"/sys/class/gpio/gpio{pin}"):
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(pin))

# 모든 GPIO 해제
def cleanup_all_pins():
    for pin in GPIO_PINS:
        gpio_cleanup(pin)

    gpio_cleanup(SWITCH_PIN_1)
    gpio_cleanup(SWITCH_PIN_2)

# UART and SPI settings
UART_DEV = "/dev/ttyAMA2"

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

    uart_write_str(fd, "UART Example based Example 4-5\n\r")
    
    while True:
        switch1_value_cur = gpio_read(SWITCH_PIN_1)
        switch2_value_cur = gpio_read(SWITCH_PIN_2)

        if switch1_value_cur == 0:
            if switch1_value_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                if switch1_event_flag == 0:
                    switch1_event_flag = 1
                    switch2_event_flag = 0

            # Send data over UART
            uart_write_str(fd, "Switch 1 Pushed\n\r")
            uart_write_str(fd, "LED Pattern 1 Start\n\r")
            uart_write_str(fd, "(LED Pattern 2 Stop)\n\r")
        switch1_value_pre = switch1_value_cur

        if switch2_value_cur == 0:
            if switch2_value_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                if switch2_event_flag == 0:
                    switch2_event_flag = 1
                    switch1_event_flag = 0

            # Send data over UART
            uart_write_str(fd, "Switch 2 Pushed\n\r")
            uart_write_str(fd, "LED Pattern 2 Start\n\r")
            uart_write_str(fd, "(LED Pattern 1 Stop)\n\r")
        switch2_value_pre = switch2_value_cur

        if switch1_event_flag == 1:
            gpio_write(GPIO_PINS[index], 1)
            time.sleep(0.5)
            pre_pin = GPIO_PINS[index]
            gpio_write(pre_pin, 0)

            index = index +1
            if index == 8:
                index = 0
        
        if switch2_event_flag == 1:
            gpio_write(GPIO_PINS[index-1], 1)
            time.sleep(0.5)
            pre_pin = GPIO_PINS[index-1]
            gpio_write(pre_pin, 0)

            index = index -1
            if index == -1:
                index = 7

except KeyboardInterrupt:
    for pin in GPIO_PINS:
        gpio_write(pin, 0)
    print("프로그램 종료")
finally:
    cleanup_all_pins()
    os.close(fd)  # Close the UART connection

    