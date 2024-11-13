import os
import time
import serial

# GPIO 핀 번호
BUZZER_PIN = 89
TRIG_PIN = 117
ECHO_PIN = 118
M_IN1 = 120
M_IN2 = 121

PWM_NUM = 2  # PWM2 사용

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
    gpio_setup_output(M_IN1)
    gpio_setup_output(M_IN2)
    gpio_setup_output(BUZZER_PIN)
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
    gpio_cleanup(M_IN1)
    gpio_cleanup(M_IN2)
    gpio_cleanup(BUZZER_PIN)
    gpio_cleanup(TRIG_PIN)
    gpio_cleanup(ECHO_PIN)

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

    if distance >= 1000:
        distance = 1000

    print("Distance => ", distance, "cm")
    ser.write(f"Distance: {distance} cm\r\n".encode())

    return distance

try:
    cleanup_all_pins()
    setup_all_pins()

    gpio_write(M_IN1, 1)
    gpio_write(M_IN2, 0)

    # PWM 초기 설정
    pwm_unexport(PWM_NUM)
    pwm_export(PWM_NUM)
    pwm_set_period(PWM_NUM, 100)

    duty_cycle_ms = 100  # 초기 duty cycle을 100%로 설정
    pwm_set_duty_cycle(PWM_NUM, duty_cycle_ms)
    pwm_enable(PWM_NUM, True)

    while True:

        value = distance_measure()

        if value < 10:
            duty_cycle_ms = 35  # 초기 duty cycle을 50%로 설정
            pwm_set_duty_cycle(PWM_NUM, duty_cycle_ms)

            gpio_write(BUZZER_PIN, 1)
            ser.write(f"거리 10cm 이내!! 주의!!!\r\n".encode())
            print(f"DC-Motor Duty cycle: {duty_cycle_ms}")
        else:
            duty_cycle_ms = 100  # 초기 duty cycle을 100%로 설정
            pwm_set_duty_cycle(PWM_NUM, duty_cycle_ms)
            
            gpio_write(BUZZER_PIN, 0)
        time.sleep(0.3)

except KeyboardInterrupt:
    gpio_write(BUZZER_PIN, 0)
    gpio_write(TRIG_PIN, 0)
    gpio_write(M_IN1, 0)
    gpio_write(M_IN2, 0)
    pwm_set_duty_cycle(PWM_NUM, 0)
    print("프로그램 종료")

finally:
    pwm_enable(PWM_NUM, False)
    pwm_unexport(PWM_NUM)
    cleanup_all_pins()
    ser.close()
