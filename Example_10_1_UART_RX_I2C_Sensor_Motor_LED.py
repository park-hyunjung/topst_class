import os
import time
import smbus2
import serial

# GPIO 핀 번호
M_IN1 = 120
M_IN2 = 121

PWM_NUM_1 = 1  # PWM1 사용
PWM_NUM_2 = 2  # PWM2 사용

SERIAL_PORT = '/dev/ttyAMA2'
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Constants
I2C_BUS = 1
GY302_ADDR = 0x23
CMD_POWER_ON = 0x01
CMD_RESET = 0x07
CMD_CONT_H_RES_MODE = 0x10

# Initialize I2C bus
bus = smbus2.SMBus(I2C_BUS)

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

def read_lux():
    """
    Read the lux value from the GY-302 sensor.
    """
    # Power on the sensor
    bus.write_byte(GY302_ADDR, CMD_POWER_ON)
    time.sleep(0.1)
    
    # Reset the sensor
    bus.write_byte(GY302_ADDR, CMD_RESET)
    time.sleep(0.1)
    
    # Set continuous high-resolution mode
    bus.write_byte(GY302_ADDR, CMD_CONT_H_RES_MODE)
    time.sleep(0.5)
    
    # Read data from the sensor
    data = bus.read_i2c_block_data(GY302_ADDR, CMD_CONT_H_RES_MODE, 2)
    
    # Convert data to lux
    lux = (data[0] << 8) | data[1]
    lux /= 1.2
    return lux

try:
    cleanup_all_pins()
    setup_all_pins()

    gpio_write(M_IN1, 1)
    gpio_write(M_IN2, 0)

    # PWM 1 초기 설정
    pwm_unexport(PWM_NUM_1)
    pwm_export(PWM_NUM_1)
    pwm_set_period(PWM_NUM_1, 100)

    duty_cycle_ms_1 = 0  # 초기 duty cycle을 100%로 설정
    pwm_set_duty_cycle(PWM_NUM_1, duty_cycle_ms_1)
    pwm_enable(PWM_NUM_1, True)

    # PWM 2 초기 설정
    pwm_unexport(PWM_NUM_2)
    pwm_export(PWM_NUM_2)
    pwm_set_period(PWM_NUM_2, 100)

    duty_cycle_ms_2 = 0  # 초기 duty cycle을 100%로 설정
    pwm_set_duty_cycle(PWM_NUM_2, duty_cycle_ms_2)
    pwm_enable(PWM_NUM_2, True)

    while True:
        ser.write("동작을 시작하려면 'S'를 입력하세요.\r\n".encode())

        if ser.readable():
            msg = ser.read(1).decode('utf-8')

            ser.write(f"Recived : {msg}\r\n".encode())
            print(f"Recived : {msg}".encode())

        if msg == 'S':
            msg = 'Z'
            ser.write(f"동작 시작!!\r\n".encode())
            print("동작 시작!!")

            while 1:
                # Read lux value
                lux_value = int(read_lux())
                print(f"Lux: {lux_value}")
                
                # Send lux value via serial
                ser.write(f"Lux: {lux_value}\r\n".encode())

                if lux_value > 900:
                    pwm_set_duty_cycle(PWM_NUM_1, 0)
                    pwm_set_duty_cycle(PWM_NUM_2, 100)
                    ser.write(f"밝음 / 주행 안전~~~\r\n".encode())
                elif lux_value <= 900 and lux_value > 600:
                    pwm_set_duty_cycle(PWM_NUM_1, 20)
                    pwm_set_duty_cycle(PWM_NUM_2, 80)
                    ser.write(f"높은구름 / 주행 보통~~~\r\n".encode())
                elif lux_value <= 600 and lux_value > 300:
                    pwm_set_duty_cycle(PWM_NUM_1, 40)
                    pwm_set_duty_cycle(PWM_NUM_2, 60)
                    ser.write(f"먹구름 / 주행 경계~!\r\n".encode())
                elif lux_value <= 300 and lux_value > 150:
                    pwm_set_duty_cycle(PWM_NUM_1, 70)
                    pwm_set_duty_cycle(PWM_NUM_2, 40)
                    ser.write(f"소나기 / 주행 주의~!!\r\n".encode())
                elif lux_value <= 150:
                    pwm_set_duty_cycle(PWM_NUM_1, 100)
                    pwm_set_duty_cycle(PWM_NUM_2, 20)
                    ser.write(f"폭우 / 서행 필수!!!\r\n".encode())

except KeyboardInterrupt:
    gpio_write(M_IN1, 0)
    gpio_write(M_IN2, 0)
    pwm_set_duty_cycle(PWM_NUM_1, 0)
    pwm_set_duty_cycle(PWM_NUM_2, 0)
    print("프로그램 종료")

finally:
    pwm_enable(PWM_NUM_1, False)
    pwm_enable(PWM_NUM_2, False)
    pwm_unexport(PWM_NUM_1)
    pwm_unexport(PWM_NUM_2)
    cleanup_all_pins()
    ser.close()
