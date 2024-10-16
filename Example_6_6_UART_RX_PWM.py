import os
import time
import serial

PWM_NUM = 1  # PWM1 사용

SERIAL_PORT = '/dev/ttyAMA2'
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

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
    # PWM 초기 설정
    #TODO

    duty_cycle_ms = 50  # 초기 duty cycle을 50%로 설정 (50ms)
    #TODO

    while True:
        ser.write("아래 문자 중 하나의 문자를 입력하세요.\r\n".encode())
        ser.write("U : Duty +10%\r\n".encode())
        ser.write("D : Duty -10%\r\n".encode())
        
        if ser.readable():
            msg = ser.read(1).decode('utf-8')

            ser.write(f"Recived : {msg}\r\n".encode())
            print(f"Recived : {msg}".encode())

        if msg == 'U':
            ser.write(f"LED 1 On\r\n".encode())
            print("LED 1 On")

            duty_cycle_ms += 10  # 10% 증가
            if duty_cycle_ms > 100:
                duty_cycle_ms = 100

            pwm_set_duty_cycle(PWM_NUM, duty_cycle_ms)
            ser.write(f"Duty cycle increased: {duty_cycle_ms}\r\n".encode())
            print(f"Duty cycle increased: {duty_cycle_ms}")

        elif msg == 'D':
            ser.write(f"LED 1 Off\r\n".encode())
            print("LED 1 Off")

            duty_cycle_ms -= 10  # 10% 감소
            if duty_cycle_ms < 0:
                duty_cycle_ms = 0

            pwm_set_duty_cycle(PWM_NUM, duty_cycle_ms)
            ser.write(f"Duty cycle decreased: {duty_cycle_ms}\r\n".encode())
            print(f"Duty cycle decreased: {duty_cycle_ms}")
            
        ser.write(f"\r\n".encode())
        msg = 'Z'

except KeyboardInterrupt:
    pwm_set_duty_cycle(PWM_NUM, 0)
    print("프로그램 종료")

finally:
    pwm_enable(PWM_NUM, False)
    pwm_unexport(PWM_NUM)
    ser.close()
