import os
import time

# GPIO 핀 번호 리스트 - 1
GPIO_PINS_1 = [83, 84, 112, 113, 117, 118, 120, 121]

# GPIO 핀 번호 리스트 - 2
GPIO_PINS_2 = [121, 120, 118, 117, 113, 112, 84, 83]

SWITCH_PIN_1 = 65

sw_flag = 0
Oper_flag = 0

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

# GPIO 초기화 및 모든 핀 설정
def setup_all_pins():
    for pin in GPIO_PINS_1:
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
    for pin in GPIO_PINS_1:
        gpio_cleanup(pin)

    gpio_cleanup(SWITCH_PIN_1)

try:
    cleanup_all_pins()
    setup_all_pins()

    while True:
        switch1_state = gpio_read(SWITCH_PIN_1)

        if switch1_state:  # Switch 1 pressed
            sw_flag = sw_flag + 1
            Oper_flag = 1

        if Oper_flag:
            Oper_flag = 0
            
            if sw_flag == 1:
                for pin in GPIO_PINS_1:
                    gpio_write(pin, 1)
                    time.sleep(0.5)
            
                    pre_pin = pin
                    gpio_write(pre_pin, 0)
            elif sw_flag == 2:
                sw_flag = 0
            
                for pin in GPIO_PINS_2:
                    gpio_write(pin, 1)
                    time.sleep(0.5)
            
                    pre_pin = pin
                    gpio_write(pre_pin, 0)

except KeyboardInterrupt:
    for pin in GPIO_PINS_1:
        gpio_write(pin, 0)
    print("프로그램 종료")

finally:
    cleanup_all_pins()
