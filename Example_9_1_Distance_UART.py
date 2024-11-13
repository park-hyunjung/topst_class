import os
import time
import serial

# GPIO 핀 번호 리스트
TRIG_PIN = 117
ECHO_PIN = 118

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
    gpio_setup_output(TRIG_PIN)
    gpio_setup_input(ECHO_PIN)
        
# GPIO 해제 함수
# GPIO 핀이 이미 export되어 있는지 확인하고, 그렇다면 unexport
def gpio_cleanup(pin):
    if os.path.exists(f"/sys/class/gpio/gpio{pin}"):
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(pin))

# 모든 GPIO 해제
def cleanup_all_pins():
    gpio_cleanup(TRIG_PIN)
    gpio_cleanup(ECHO_PIN)

# 거리측정 함수
def distance_measure():
    gpio_write(TRIG_PIN, 1)
    time.sleep(0.00001)
    gpio_write(TRIG_PIN, 0)

    # Echo가 OFF 되는 시점을 시작시간으로 설정
    while gpio_read(ECHO_PIN) == 0:
        start = time.time()

    # Echo가 ON 되는 시점을 반사파 수신시간으로 설정
    while gpio_read(ECHO_PIN) == 1:
        stop = time.time()
    
    # 초음파가 되돌아오는 시간차로 거리를 계산
    time_interval = stop - start
    distance = time_interval * 17150        # 34300 /2
    distance = round(distance)
    # 소숫점 없이 사용 (round(ditance, 2) = 소숫점 두째자리까지 표현)

    print("Distance => ", distance, "cm")
    ser.write(f"Distance: {distance} cm\r\n".encode())

try:
    cleanup_all_pins()
    setup_all_pins()

    while True:

        distance_measure()

        time.sleep(0.3)

except KeyboardInterrupt:
    gpio_write(TRIG_PIN, 0)
    print("프로그램 종료")

finally:
    cleanup_all_pins()
    ser.close()
