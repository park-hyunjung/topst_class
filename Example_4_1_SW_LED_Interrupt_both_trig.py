import os
import time
import select

# GPIO 핀 번호
GPIO_PINS = 83
SWITCH_PIN_1 = 65

switch1_value_pre = 0
switch1_value_cur = 0
switch1_event_flag = 0
switch1_event_falling_flag = 0

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

try:
    gpio_setup_output(GPIO_PINS)
    gpio_setup_input(SWITCH_PIN_1)

    print("Switch 1 Push 대기 상태...")
    while True:
        switch1_value_cur = gpio_read(SWITCH_PIN_1)

        if switch1_event_falling_flag == 0:
            if switch1_value_cur == 0:
                if switch1_value_pre == 1:  # falling edge detect
                    time.sleep(0.02)  # 바운스 방지

                    print("Switch 1 눌림")
                    gpio_write(GPIO_PINS, 1)
                    time.sleep(0.5)
                    gpio_write(GPIO_PINS, 0)
                    time.sleep(0.5)

                    switch1_event_falling_flag = 1
            switch1_value_pre = switch1_value_cur

        if switch1_event_falling_flag == 1:
            if switch1_value_cur == 1:
                if switch1_value_pre == 0:  # rising edge detect
                    time.sleep(0.02)  # 바운스 방지

                    print("Switch 1 떨어짐")
                    gpio_write(GPIO_PINS, 1)
                    time.sleep(0.5)
                    gpio_write(GPIO_PINS, 0)
                    time.sleep(0.5)

                    switch1_event_falling_flag = 0
            switch1_value_pre = switch1_value_cur
        print("Switch 1 Push 대기 상태...")

        time.sleep(0.3)

except KeyboardInterrupt:
    gpio_write(GPIO_PINS, 0)
    print("프로그램 종료")

finally:
    gpio_cleanup(GPIO_PINS)
    gpio_cleanup(SWITCH_PIN_1)
