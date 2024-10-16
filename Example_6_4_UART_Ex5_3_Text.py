import os
import termios
import time
from enum import IntEnum

# GPIO 핀 번호
SWITCH_Normal_PIN = 65
SWITCH_Twinkle_PIN = 66
PWM_NUM = 0   # PWM0 사용

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

# UART and SPI settings
UART_DEV = "/dev/ttyAMA2"

class TCATTRS(IntEnum):
    IFLAG = 0
    OFLAG = 1
    CFLAG = 2
    LFLAG = 3
    ISPEED = 4
    OSPEED = 5

def uart_set_speed(fd:int, speed:int):
    baudrates = {
        115200: termios.B115200,
        57600: termios.B57600,
        38400: termios.B38400,
        19200: termios.B19200,
        9600: termios.B9600,
        4800: termios.B4800,
        2400: termios.B2400,
        1200: termios.B1200,
    }

    attrs = termios.tcgetattr(fd)
    attrs[TCATTRS.IFLAG] &= ~(termios.INPCK | termios.ISTRIP | termios.INLCR | termios.IGNCR | termios.ICRNL | termios.IXON)
    attrs[TCATTRS.ISPEED] = baudrates[speed]
    attrs[TCATTRS.OSPEED] = baudrates[speed]
    attrs[TCATTRS.CFLAG] &= ~termios.CSIZE
    attrs[TCATTRS.CFLAG] |= termios.CS8 | termios.CLOCAL | termios.CREAD
    attrs[TCATTRS.LFLAG] &= ~(termios.ICANON | termios.ECHO | termios.ECHOE | termios.ISIG)
    attrs[TCATTRS.OFLAG] &= ~termios.OPOST
    termios.tcsetattr(fd, termios.TCSANOW, attrs)

def uart_write_str(fd:int, data:str):
    os.write(fd, data.encode('utf-8'))

def uart_read_str(fd:int):
    return os.read(fd, 1024).decode('utf-8')

try:
    cleanup_all_pins()
    setup_all_pins()

    # PWM 초기 설정
    pwm_unexport(PWM_NUM)
    pwm_export(PWM_NUM)
    pwm_set_duty_cycle(PWM_NUM, 0)
    pwm_enable(PWM_NUM, True)

    # UART setup
    fd = os.open(UART_DEV, os.O_RDWR | os.O_NOCTTY)
    uart_set_speed(fd, 115200)

    uart_write_str(fd, "UART Example based Example 5-3\n\r")
    
    while True:
        switch_Normal_state_cur = gpio_read(SWITCH_Normal_PIN)
        switch_Twinkle_state_cur = gpio_read(SWITCH_Twinkle_PIN)

        if switch_Normal_state_cur == 0:
            if switch_Normal_state_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                switch_Normal_event_flag = 1

                # Send data over UART
                uart_write_str(fd, "Switch 1 Pushed\n\r")
                uart_write_str(fd, "음계 Start\n\r")

        switch_Normal_state_pre = switch_Normal_state_cur

        if switch_Twinkle_state_cur == 0:
            if switch_Twinkle_state_pre == 1:  # falling edge detect
                time.sleep(0.02)  # 바운스 방지

                switch_Twinkle_event_flag = 1

                # Send data over UART
                uart_write_str(fd, "Switch 2 Pushed\n\r")
                uart_write_str(fd, "작은 별 Start\n\r")

        switch_Twinkle_state_pre = switch_Twinkle_state_cur

        if switch_Normal_event_flag == 1:
            switch_Normal_event_flag = 0

            print("SW 1 - 도레미파솔라시도")
            
            pwm_set_duty_cycle(PWM_NUM, 100)

            pwm_set_period(PWM_NUM, 2093)
            uart_write_str(fd, "도 ")
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1976)
            uart_write_str(fd, "레 ")
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1760)
            uart_write_str(fd, "미 ")
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1568)
            uart_write_str(fd, "파 ")
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1397)
            uart_write_str(fd, "솔 ")
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1319)
            uart_write_str(fd, "라 ")
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1165)
            uart_write_str(fd, "시 ")
            time.sleep(0.3)
            pwm_set_period(PWM_NUM, 1025)
            uart_write_str(fd, "도\n\r")
            time.sleep(0.5)

            pwm_set_duty_cycle(PWM_NUM, 0)

        if switch_Twinkle_event_flag == 1:
            switch_Twinkle_event_flag = 0

            print("SW 2 - 작은 별")

            pwm_set_duty_cycle(PWM_NUM, 100)

            for i in range(0, 42):
                pwm_set_period(PWM_NUM, scale[twinkle[i]])

                if twinkle[i] == 1:
                    uart_write_str(fd, "도 ")
                elif twinkle[i] == 2:
                    uart_write_str(fd, "레 ")
                elif twinkle[i] == 3:
                    uart_write_str(fd, "미 ")
                elif twinkle[i] == 4:
                    uart_write_str(fd, "파 ")
                elif twinkle[i] == 5:
                    uart_write_str(fd, "솔 ")
                elif twinkle[i] == 6:
                    uart_write_str(fd, "라 ")
                elif twinkle[i] == 7:
                    uart_write_str(fd, "시 ")
                elif twinkle[i] == 8:
                    uart_write_str(fd, "도 ")

                if (i+1)%14 == 0:
                    uart_write_str(fd, "\n\r")

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
    os.close(fd)  # Close the UART connection

    