import os
import time

# GPIO 핀 번호
GPIO_PINS = 83
SWITCH_PIN_1 = 65

sw_flag = 0

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

    # Set pull-up or pull-down resistor
    with open(f"/sys/class/gpio/gpio{pin}/active_low", "w") as f:
        f.write("1")  # 0 for pull-down, 1 for pull-up
      
# GPIO 상태 쓰기 함수
def gpio_write(pin, value):
    with open(f"/sys/class/gpio/gpio{pin}/value", "w") as f:
        f.write(str(value))

def gpio_read(pin):
    with open(f"/sys/class/gpio/gpio{pin}/value", "r") as f:
        return int(f.read().strip())
        
# GPIO 해제 함수
# GPIO 핀이 이미 export되어 있는지 확인하고, 그렇다면 unexport
def gpio_cleanup(pin):
    if os.path.exists(f"/sys/class/gpio/gpio{pin}"):
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(pin))

try:
    # GPIO 해제
    gpio_cleanup(GPIO_PINS)
    gpio_cleanup(SWITCH_PIN_1)
    # GPIO 초기화 및 핀 설정
    gpio_setup_output(GPIO_PINS)
    gpio_setup_input(SWITCH_PIN_1)

    while True:
        # Switch 누르고 있을 때 켜고 떼고 있을 때 끄기
        switch1_state = gpio_read(SWITCH_PIN_1)

        if switch1_state:  # Switch 1 pressed
            sw_flag = 1

        if sw_flag:
            sw_flag = 0
            
            gpio_write(GPIO_PINS, 1)
            time.sleep(0.5)
            gpio_write(GPIO_PINS, 0)
            time.sleep(0.5)

except KeyboardInterrupt:
    gpio_write(GPIO_PINS, 0)
    print("프로그램 종료")

finally:
    gpio_cleanup(GPIO_PINS)
    gpio_cleanup(SWITCH_PIN_1)
