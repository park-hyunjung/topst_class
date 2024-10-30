import os
import time
import serial
import spidev

# GPIO 핀 번호
GPIO_PIN = 83

# SPI settings
SPI_BUS = 0
SPI_DEVICE = 0
SPI_SPEED_HZ = 1000000

# MPU-9250 register addresses
MPU9250_PWR_MGMT_1 = 0x6B
MPU9250_ACCEL_XOUT_H = 0x3B
MPU9250_GYRO_XOUT_H = 0x43

# UART and SPI settings
SERIAL_PORT = '/dev/ttyAMA2'
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

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
        
# GPIO 해제 함수
# GPIO 핀이 이미 export되어 있는지 확인하고, 그렇다면 unexport
def gpio_cleanup(pin):
    if os.path.exists(f"/sys/class/gpio/gpio{pin}"):
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(pin))

# 모든 GPIO 해제
def cleanup_all_pins():
    gpio_cleanup(GPIO_PIN)

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

    # SPI setup
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEVICE)
    spi.max_speed_hz = SPI_SPEED_HZ

    mpu9250_initialize(spi)  # Initialize MPU-9250

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
                    ser.write(f"움직임 감지!!\r\n".encode())
                    for i in range(5):
                        gpio_write(GPIO_PIN, 1)
                        time.sleep(0.3)
                        gpio_write(GPIO_PIN, 0)
                        time.sleep(0.3)

                Accel_x_pre = Accel_x_cur

                time.sleep(0.3)  # Wait for 1 second

except KeyboardInterrupt:
    gpio_write(GPIO_PIN, 0)
    print("프로그램 종료")

finally:
    cleanup_all_pins()
    spi.close()  # Close the SPI connection
    ser.close()
