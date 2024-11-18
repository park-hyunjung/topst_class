import os
import time
import spidev
import serial

# GPIO 핀 번호
GPIO_PIN = 83
M_IN1 = 120
M_IN2 = 121

PWM_NUM = 2  # PWM2 사용

SERIAL_PORT = '/dev/ttyAMA2'
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# SPI settings
SPI_BUS = 0
SPI_DEVICE = 0
SPI_SPEED_HZ = 1000000

# MPU-9250 register addresses
MPU9250_PWR_MGMT_1 = 0x6B
MPU9250_ACCEL_XOUT_H = 0x3B
MPU9250_GYRO_XOUT_H = 0x43

State = 0
Accel_dif = 0

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
    gpio_setup_output(GPIO_PIN)
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
    gpio_cleanup(GPIO_PIN)
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

def mpu9250_initialize(spi):
    spi.xfer2([MPU9250_PWR_MGMT_1, 0x00])  # Wake up MPU-9250 by writing 0 to the power management register

def read_word_2c(spi, addr):
    high = spi.xfer2([addr | 0x80, 0x00])[1]  # Read the high byte
    low = spi.xfer2([addr + 1 | 0x80, 0x00])[1]  # Read the low byte
    value = (high << 8) + low  # Combine high and low bytes
    if value >= 0x8000:  # Convert to signed value if necessary
        value = -((65535 - value) + 1)
    return value

def read_accel_data(spi):
    accel_x = read_word_2c(spi, MPU9250_ACCEL_XOUT_H)
    accel_y = read_word_2c(spi, MPU9250_ACCEL_XOUT_H + 2)
    accel_z = read_word_2c(spi, MPU9250_ACCEL_XOUT_H + 4)
    return accel_x, accel_y, accel_z

def read_gyro_data(spi):
    gyro_x = read_word_2c(spi, MPU9250_GYRO_XOUT_H)
    gyro_y = read_word_2c(spi, MPU9250_GYRO_XOUT_H + 2)
    gyro_z = read_word_2c(spi, MPU9250_GYRO_XOUT_H + 4)
    return gyro_x, gyro_y, gyro_z

try:
    cleanup_all_pins()
    setup_all_pins()

    gpio_write(M_IN1, 1)
    gpio_write(M_IN2, 0)

    # PWM 2 초기 설정
    pwm_unexport(PWM_NUM)
    pwm_export(PWM_NUM)
    pwm_set_period(PWM_NUM, 100)

    duty_cycle_ms = 100  # 초기 duty cycle을 100%로 설정
    pwm_set_duty_cycle(PWM_NUM, duty_cycle_ms)
    pwm_enable(PWM_NUM, True)

    # SPI setup
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEVICE)
    spi.max_speed_hz = SPI_SPEED_HZ

    mpu9250_initialize(spi)  # Initialize MPU-9250

    ser.write(f"정상 운행 시작!!\r\n".encode())
    print("정상 운행 시작!!")

    while True:
        # Read accelerometer and gyroscope data
        accel_x, accel_y, accel_z = read_accel_data(spi)
        gyro_x, gyro_y, gyro_z = read_gyro_data(spi)

        # Prepare data string
        data = f"Accel X: {accel_x}, Accel Y: {accel_y}, Accel Z: {accel_z}\r\n"
        data += f"Gyro X: {gyro_x}, Gyro Y: {gyro_y}, Gyro Z: {gyro_z}\r\n"
        data += "----------------------------------------------------------\r\n"

        # Print data to console
        print(data.strip())
        # Send data over UART
        ser.write(f"{data}\r\n".encode())

        Accel_x_cur = accel_x

        if State == 0:
            State = 1
            Accel_x_pre = Accel_x_cur
        else:
            if Accel_x_cur > Accel_x_pre:
                Accel_dif = Accel_x_cur - Accel_x_pre
            else:
                Accel_dif = Accel_x_pre - Accel_x_cur
        
        if Accel_dif > 700:
            gpio_write(M_IN1, 0)
            gpio_write(M_IN2, 0)
            ser.write(f"차량 충돌!!! 긴급상황 발생!!\r\n".encode())

            while True:
                gpio_write(GPIO_PIN, 1)
                ser.write(f"Emergency Lamp On!!\r\n".encode())
                time.sleep(0.3)
                gpio_write(GPIO_PIN, 0)
                ser.write(f"Emergency Lamp Off!!\r\n".encode())
                time.sleep(0.3)

        time.sleep(0.3)

except KeyboardInterrupt:
    gpio_write(GPIO_PIN, 0)
    gpio_write(M_IN1, 0)
    gpio_write(M_IN2, 0)
    pwm_set_duty_cycle(PWM_NUM, 0)
    print("프로그램 종료")

finally:
    pwm_enable(PWM_NUM, False)
    pwm_unexport(PWM_NUM)
    cleanup_all_pins()
    spi.close()
    ser.close()
