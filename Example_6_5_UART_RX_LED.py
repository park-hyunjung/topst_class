import os
import time
import select
import serial

# GPIO 핀 번호 리스트
GPIO_PINS = [83, 84, 112, 113]

SERIAL_PORT = '/dev/ttyAMA2'
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

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

try:
    cleanup_all_pins()
    setup_all_pins()

    while True:
        ser.write("아래 문자 중 하나의 문자를 입력하세요.\r\n".encode())
        ser.write("A : LED 1 On\r\n".encode())
        ser.write("a : LED 1 Off\r\n".encode())
        ser.write("B : LED 2 On\r\n".encode())
        ser.write("b : LED 2 Off\r\n".encode())
        ser.write("C : LED 3 On\r\n".encode())
        ser.write("c : LED 3 Off\r\n".encode())
        ser.write("D : LED 4 On\r\n".encode())
        ser.write("d : LED 4 Off\r\n".encode())

        if ser.readable():
            msg = ser.read(1).decode('utf-8')

            ser.write(f"Recived : {msg}\r\n".encode())
            print(f"Recived : {msg}".encode())

        if msg == 'A':
            ser.write(f"LED 1 On\r\n".encode())
            print("LED 1 On")
            gpio_write(GPIO_PINS[0], 1)
        elif msg == 'a':
            ser.write(f"LED 1 Off\r\n".encode())
            print("LED 1 Off")
            gpio_write(GPIO_PINS[0], 0)
        elif msg == 'B':
            ser.write(f"LED 2 On\r\n".encode())
            print("LED 2 On")
            gpio_write(GPIO_PINS[1], 1)
        elif msg == 'b':
            ser.write(f"LED 2 Off\r\n".encode())
            print("LED 2 Off")
            gpio_write(GPIO_PINS[1], 0)
        elif msg == 'C':
            ser.write(f"LED 3 On\r\n".encode())
            print("LED 3 On")
            gpio_write(GPIO_PINS[2], 1)
        elif msg == 'c':
            ser.write(f"LED 3 Off\r\n".encode())
            print("LED 3 Off")
            gpio_write(GPIO_PINS[2], 0)
        elif msg == 'D':
            ser.write(f"LED 4 On\r\n".encode())
            print("LED 4 On")
            gpio_write(GPIO_PINS[3], 1)
        elif msg == 'd':
            ser.write(f"LED 4 Off\r\n".encode())
            print("LED 4 Off")
            gpio_write(GPIO_PINS[3], 0)
        ser.write(f"\r\n".encode())
        msg = 'Z'

except KeyboardInterrupt:
    for pin in GPIO_PINS:
        gpio_write(pin, 0)
    print("프로그램 종료")

finally:
    cleanup_all_pins()
    ser.close()
