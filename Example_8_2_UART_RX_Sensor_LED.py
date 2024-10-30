import os
import time
import smbus2
import serial

PWM_NUM = 1  # PWM1 사용

# Constants
I2C_BUS = 1
GY302_ADDR = 0x23
CMD_POWER_ON = 0x01
CMD_RESET = 0x07
CMD_CONT_H_RES_MODE = 0x10

# Initialize I2C bus
bus = smbus2.SMBus(I2C_BUS)

# UART and SPI settings
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
    # PWM 초기 설정
    pwm_unexport(PWM_NUM)
    pwm_export(PWM_NUM)
    pwm_set_period(PWM_NUM, 100)

    duty_cycle_ms = 0  # 초기 duty cycle을 0%로 설정
    pwm_set_duty_cycle(PWM_NUM, duty_cycle_ms)
    pwm_enable(PWM_NUM, True)

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
                    pwm_set_duty_cycle(PWM_NUM, 0)
                elif lux_value <= 900 and lux_value > 600:
                    pwm_set_duty_cycle(PWM_NUM, 20)
                elif lux_value <= 600 and lux_value > 300:
                    pwm_set_duty_cycle(PWM_NUM, 40)
                elif lux_value <= 300 and lux_value > 150:
                    pwm_set_duty_cycle(PWM_NUM, 70)
                elif lux_value <= 150:
                    pwm_set_duty_cycle(PWM_NUM, 100)

                #time.sleep(0.1)  # Wait for 1 second

except KeyboardInterrupt:
    pwm_set_duty_cycle(PWM_NUM, 0)
    print("프로그램 종료")

finally:
    pwm_enable(PWM_NUM, False)
    pwm_unexport(PWM_NUM)
    bus.close()
    ser.close()
