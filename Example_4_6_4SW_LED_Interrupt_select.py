import os
import time
import select

# GPIO 핀 번호 리스트
GPIO_PINS = [83, 84, 112, 113, 117, 118, 120, 121]
GPIO_PINS_1 = [83, 112, 117, 120]
GPIO_PINS_2 = [84, 113, 118, 121]
SWITCH_PIN_1 = 65
SWITCH_PIN_2 = 66
SWITCH_PIN_3 = 85
SWITCH_PIN_4 = 86

switch1_value_pre = 0
switch1_value_cur = 0
switch1_event_flag = 0

switch2_value_pre = 0
switch2_value_cur = 0
switch2_event_flag = 0

switch3_value_pre = 0
switch3_value_cur = 0
switch3_event_flag = 0

switch4_value_pre = 0
switch4_value_cur = 0
switch4_event_flag = 0

index_1 = 0
index_2 = 7

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
    gpio_setup_input(SWITCH_PIN_3)
    gpio_setup_input(SWITCH_PIN_4)
        
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
    gpio_cleanup(SWITCH_PIN_3)
    gpio_cleanup(SWITCH_PIN_4)

try:
    cleanup_all_pins()
    setup_all_pins()

    print("Switch Push 대기 상태...")
    while True:
        switch1_value_cur = gpio_read(SWITCH_PIN_1)
        switch2_value_cur = gpio_read(SWITCH_PIN_2)
        switch3_value_cur = gpio_read(SWITCH_PIN_3)
        switch4_value_cur = gpio_read(SWITCH_PIN_4)

        if switch1_value_cur == 0:
            if switch1_value_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                print("Switch 1 눌림")
                if switch1_event_flag == 0:
                    switch1_event_flag = 1
                    switch2_event_flag = 0
                    switch3_event_flag = 0
                    switch4_event_flag = 0
                    print("LED Mode 1 동작 Start")
                index = 0

                for pin in GPIO_PINS:
                    gpio_write(pin, 0)
        switch1_value_pre = switch1_value_cur

        if switch2_value_cur == 0:
            if switch2_value_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                print("Switch 2 눌림")
                if switch2_event_flag == 0:
                    switch1_event_flag = 0
                    switch2_event_flag = 1
                    switch3_event_flag = 0
                    switch4_event_flag = 0
                    print("LED Mode 2 동작 Start")
                index = 7

                for pin in GPIO_PINS:
                    gpio_write(pin, 0)
        switch2_value_pre = switch2_value_cur

        if switch3_value_cur == 0:
            if switch3_value_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                print("Switch 3 눌림")
                if switch3_event_flag == 0:
                    switch1_event_flag = 0
                    switch2_event_flag = 0
                    switch3_event_flag = 1
                    switch4_event_flag = 0
                    print("LED Mode 3 동작 Start")

                for pin in GPIO_PINS:
                    gpio_write(pin, 0)
        switch3_value_pre = switch3_value_cur

        if switch4_value_cur == 0:
            if switch4_value_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                print("Switch 4 눌림")
                if switch4_event_flag == 0:
                    switch1_event_flag = 0
                    switch2_event_flag = 0
                    switch3_event_flag = 0
                    switch4_event_flag = 1
                    print("LED Mode 4 동작 Start")g
                index = 0

                for pin in GPIO_PINS:
                    gpio_write(pin, 0)
        switch4_value_pre = switch4_value_cur

        if switch1_event_flag == 1:
            gpio_write(GPIO_PINS[index], 1)
            time.sleep(0.5)
            pre_pin = GPIO_PINS[index]
            gpio_write(pre_pin, 0)

            index = index +1
            if index == 8:
                index = 0
        
        if switch2_event_flag == 1:
            gpio_write(GPIO_PINS[index], 1)
            time.sleep(0.5)
            pre_pin = GPIO_PINS[index]
            gpio_write(pre_pin, 0)

            index = index -1
            if index == -1:
                index = 7

        if switch3_event_flag == 1:
            for pin in GPIO_PINS_1:
                gpio_write(pin, 1)
            for pin in GPIO_PINS_2:
                gpio_write(pin, 0)

            time.sleep(0.5)

            for pin in GPIO_PINS_2:
                gpio_write(pin, 1)
            for pin in GPIO_PINS_1:
                gpio_write(pin, 0)

            time.sleep(0.5)
        
        if switch4_event_flag == 1:
            gpio_write(GPIO_PINS[index], 1)
            time.sleep(0.5)
            pre_pin = GPIO_PINS[index]
            gpio_write(pre_pin, 0)

            index = index +2
            if index == 8:
                index = 1
            elif index == 9:
                index = 0

        print("Switch Push 대기 상태...")

except KeyboardInterrupt:
    for pin in GPIO_PINS:
        gpio_write(pin, 0)
    print("프로그램 종료")

finally:
    cleanup_all_pins()
