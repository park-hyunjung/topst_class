import os
import time

# GPIO 핀 번호
SWITCH_Normal_PIN = 65
SWITCH_Twinkle_PIN = 66
PWM_NUM = 0  # PWM0 사용

# Twinkle
scale = [2093, 1976, 1760, 1568, 1397, 1319, 1165, 1025]
twinkle = [1, 1, 5, 5, 6, 6, 5, 4, 4, 3, 3, 2, 2, 1, \
           5, 5, 4, 4, 3, 3, 2, 5, 5, 4, 4, 3, 3, 2, \
           1, 1, 5, 5, 6, 6, 5, 4, 4, 3, 3, 2, 2, 1]

switch_Normal_state_cur = 0
switch_Normal_state_pre = 0
switch_Normal_event_flag = 0

switch_Twinkle_state_cur = 0
switch_Twinkle_state_pre = 0
switch_Twinkle_event_flag = 0

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
    gpio_setup_input(SWITCH_Normal_PIN)
    gpio_setup_input(SWITCH_Twinkle_PIN)

# GPIO 해제 함수
# GPIO 핀이 이미 export되어 있는지 확인하고, 그렇다면 unexport
def gpio_cleanup(pin):
    if os.path.exists(f"/sys/class/gpio/gpio{pin}"):
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(pin))

# 모든 GPIO 해제
def cleanup_all_pins():
    gpio_cleanup(SWITCH_Normal_PIN)
    gpio_cleanup(SWITCH_Twinkle_PIN)

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
    print("======================================")
    print("버튼 1 과 버튼 2로 Melody를 Play 하세요.")
    print("버튼 1 : 음계 Melody")
    print("버튼 2 : 작은별 Melody")
    print("======================================")

    # PWM 초기 설정
    pwm_unexport(PWM_NUM)
    pwm_export(PWM_NUM)
    pwm_set_duty_cycle(PWM_NUM, 0)
    pwm_enable(PWM_NUM, True)

    while True:
        switch_Normal_state_cur = gpio_read(SWITCH_Normal_PIN)
        switch_Twinkle_state_cur = gpio_read(SWITCH_Twinkle_PIN)

        if switch_Normal_state_cur == 0:
            if switch_Normal_state_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                switch_Normal_event_flag = 1

        switch_Normal_state_pre = switch_Normal_state_cur

        if switch_Twinkle_state_cur == 0:
            if switch_Twinkle_state_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                switch_Twinkle_event_flag = 1

        switch_Twinkle_state_pre = switch_Twinkle_state_cur

        if switch_Normal_event_flag == 1:
            switch_Normal_event_flag = 0

            print("SW 1 - 도레미파솔라시도")

            pwm_set_duty_cycle(PWM_NUM, 100)

            pwm_set_period(PWM_NUM, 2093)
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1976)
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1760)
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1568)
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1397)
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1319)
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1165)
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1025)
            time.sleep(0.5)

            pwm_set_duty_cycle(PWM_NUM, 0)

        if switch_Twinkle_event_flag == 1:
            switch_Twinkle_event_flag = 0

            print("SW 2 - 작은 별")

            pwm_set_duty_cycle(PWM_NUM, 100)

            for i in range(0, 42):
                pwm_set_period(PWM_NUM, scale[twinkle[i]])
                if i==6 or i==13 or i==20 or i==27 or i==34 or i==41:
                    time.sleep(1)
                else:
                    time.sleep(0.5)

            pwm_set_duty_cycle(PWM_NUM, 0)

except KeyboardInterrupt:
    pwm_set_period(PWM_NUM, 100)
    pwm_set_duty_cycle(PWM_NUM, 0)
    print("프로그램 종료")

finally:
    pwm_enable(PWM_NUM, False)
    pwm_unexport(PWM_NUM)
    cleanup_all_pins()
