import os
import time

# GPIO 핀 번호
SWITCH_UP_PIN = 65
SWITCH_DOWN_PIN = 66
PWM_NUM = 0  # PWM0 사용

switch_up_state_cur = 0
switch_up_state_pre = 0
switch_up_event_flag = 0

switch_down_state_cur = 0
switch_down_state_pre = 0
switch_down_event_flag = 0

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
    gpio_setup_input(SWITCH_UP_PIN)
    gpio_setup_input(SWITCH_DOWN_PIN)
        
# GPIO 해제 함수
# GPIO 핀이 이미 export되어 있는지 확인하고, 그렇다면 unexport
def gpio_cleanup(pin):
    if os.path.exists(f"/sys/class/gpio/gpio{pin}"):
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(pin))

# 모든 GPIO 해제
def cleanup_all_pins():
    gpio_cleanup(SWITCH_UP_PIN)
    gpio_cleanup(SWITCH_DOWN_PIN)

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
    print("Press button 1 to increase brightness by 10%, button 2 to decrease.")

    # PWM 초기 설정
    pwm_unexport(PWM_NUM)
    pwm_export(PWM_NUM)
    pwm_set_period(PWM_NUM, 100)

    duty_cycle_ms = 50  # 초기 duty cycle을 50%로 설정 (50ms)
    pwm_set_duty_cycle(PWM_NUM, duty_cycle_ms)
    pwm_enable(PWM_NUM, True)

    while True:
        switch_up_state_cur = gpio_read(SWITCH_UP_PIN)
        switch_down_state_cur = gpio_read(SWITCH_DOWN_PIN)

        if switch_up_state_cur == 0:
            if switch_up_state_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                switch_up_event_flag = 1

        switch_up_state_pre = switch_up_state_cur

        if switch_down_state_cur == 0:
            if switch_down_state_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                switch_down_event_flag = 1

        switch_down_state_pre = switch_down_state_cur

        if switch_up_event_flag == 1:
            switch_up_event_flag = 0

            duty_cycle_ms += 10  # 10% 증가
            if duty_cycle_ms > 100:
                duty_cycle_ms = 100

            pwm_set_duty_cycle(PWM_NUM, duty_cycle_ms)
            print(f"Duty cycle increased: {duty_cycle_ms}")

        if switch_down_event_flag == 1:
            switch_down_event_flag = 0

            duty_cycle_ms -= 10  # 10% 감소
            if duty_cycle_ms < 0:
                duty_cycle_ms = 0

            pwm_set_duty_cycle(PWM_NUM, duty_cycle_ms)
            print(f"Duty cycle decreased: {duty_cycle_ms}")

except KeyboardInterrupt:
    pwm_set_duty_cycle(PWM_NUM, 0)
    print("프로그램 종료")

finally:
    pwm_enable(PWM_NUM, False)
    pwm_unexport(PWM_NUM)
    cleanup_all_pins()
