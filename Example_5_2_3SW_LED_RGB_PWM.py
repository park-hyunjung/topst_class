import os
import time

# GPIO 핀 번호
SWITCH_RED_PIN = 65
SWITCH_GREEN_PIN = 66
SWITCH_BLUE_PIN = 85
SWITCH_OFF_PIN = 86
PWM_NUM = [0, 1, 2]  # PWM0, 1, 2 사용

duty_cycle_ms_red = 0
duty_cycle_ms_green = 0
duty_cycle_ms_blue = 0

switch_red_state_cur = 0
switch_red_state_pre = 0
switch_red_event_flag = 0

switch_green_state_cur = 0
switch_green_state_pre = 0
switch_green_event_flag = 0

switch_blue_state_cur = 0
switch_blue_state_pre = 0
switch_blue_event_flag = 0

switch_off_state_cur = 0
switch_off_state_pre = 0
switch_off_event_flag = 0

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
    gpio_setup_input(SWITCH_RED_PIN)
    gpio_setup_input(SWITCH_GREEN_PIN)
    gpio_setup_input(SWITCH_BLUE_PIN)
    gpio_setup_input(SWITCH_OFF_PIN)
        
# GPIO 해제 함수
# GPIO 핀이 이미 export되어 있는지 확인하고, 그렇다면 unexport
def gpio_cleanup(pin):
    if os.path.exists(f"/sys/class/gpio/gpio{pin}"):
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(pin))

# 모든 GPIO 해제
def cleanup_all_pins():
    gpio_cleanup(SWITCH_RED_PIN)
    gpio_cleanup(SWITCH_GREEN_PIN)
    gpio_cleanup(SWITCH_BLUE_PIN)
    gpio_cleanup(SWITCH_OFF_PIN)

# PWM 관련 함수들
def pwm_exists(num):
    return os.path.exists(f'/sys/class/pwm/pwmchip0/pwm{num}')

def pwm_export(num):
    if not pwm_exists(num):
        with open('/sys/class/pwm/pwmchip0/export', 'wt') as f:
            f.write(str(num))

def pwm_unexport(num):
    if pwm_exists(num):
        with open('/sys/class/pwm/pwmchip0/unexport', 'wt') as f:
            f.write(str(num))

def pwm_enable(num, enable):
    with open(f'/sys/class/pwm/pwmchip0/pwm{num}/enable', 'wt') as f:
        f.write('1' if enable else '0')

def pwm_set_duty_cycle(num, duty_cycle_ms):
    with open(f'/sys/class/pwm/pwmchip0/pwm{num}/duty_cycle', 'wt') as f:
        f.write(str(duty_cycle_ms * 1000))

def pwm_set_period(num, period_ms):
    with open(f'/sys/class/pwm/pwmchip0/pwm{num}/period', 'wt') as f:
        f.write(str(period_ms * 1000))

try:
    cleanup_all_pins()
    setup_all_pins()

    # 초기화 메시지 출력
    print("Press button to increase brightness. Each LED is controlled by separate buttons.")

    # PWM 초기 설정
    for pwm_pin in PWM_NUM:
        pwm_unexport(pwm_pin)
        pwm_export(pwm_pin)
        pwm_set_period(pwm_pin, 100)
        pwm_set_duty_cycle(pwm_pin, 0)
        pwm_enable(pwm_pin, True)

    while True:
        switch_red_state_cur = gpio_read(SWITCH_RED_PIN)
        switch_green_state_cur = gpio_read(SWITCH_GREEN_PIN)
        switch_blue_state_cur = gpio_read(SWITCH_BLUE_PIN)
        switch_off_state_cur = gpio_read(SWITCH_OFF_PIN)

        if switch_red_state_cur == 0:
            if switch_red_state_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                switch_red_event_flag = 1

        switch_red_state_pre = switch_red_state_cur

        if switch_green_state_cur == 0:
            if switch_green_state_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                switch_green_event_flag = 1

        switch_green_state_pre = switch_green_state_cur

        if switch_blue_state_cur == 0:
            if switch_blue_state_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                switch_blue_event_flag = 1

        switch_blue_state_pre = switch_blue_state_cur

        if switch_off_state_cur == 0:
            if switch_off_state_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                switch_off_event_flag = 1

        switch_off_state_pre = switch_off_state_cur

        if switch_red_event_flag == 1:
            switch_red_event_flag = 0

            duty_cycle_ms_red += 10  # 10% 증가
            if duty_cycle_ms_red > 100:
                duty_cycle_ms_red = 100

            pwm_set_duty_cycle(PWM_NUM[2], duty_cycle_ms_red)
            print(f"Red Duty cycle increased: {duty_cycle_ms_red}")

        if switch_green_event_flag == 1:
            switch_green_event_flag = 0

            duty_cycle_ms_green += 10  # 10% 감소
            if duty_cycle_ms_green > 100:
                duty_cycle_ms_green = 100

            pwm_set_duty_cycle(PWM_NUM[1], duty_cycle_ms_green)
            print(f"Green Duty cycle increased: {duty_cycle_ms_green}")
        
        if switch_blue_event_flag == 1:
            switch_blue_event_flag = 0

            duty_cycle_ms_blue += 10  # 10% 감소
            if duty_cycle_ms_blue > 100:
                duty_cycle_ms_blue = 100

            pwm_set_duty_cycle(PWM_NUM[0], duty_cycle_ms_blue)
            print(f"Blue Duty cycle increased: {duty_cycle_ms_blue}")

        if switch_off_event_flag == 1:
            switch_off_event_flag = 0
            
            duty_cycle_ms_red = 0
            duty_cycle_ms_green = 0
            duty_cycle_ms_blue = 0

            for pwm_pin in PWM_NUM:
                pwm_set_duty_cycle(pwm_pin, 0)
            print(f"LED All Off")

except KeyboardInterrupt:
    for pwm_pin in PWM_NUM:
        pwm_set_duty_cycle(pwm_pin, 0)
    print("프로그램 종료")

finally:
    for pwm_pin in PWM_NUM:
        pwm_enable(pwm_pin, False)
        pwm_unexport(pwm_pin)
    cleanup_all_pins()
