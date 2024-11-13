import spidev
import os
import termios
import time
from enum import IntEnum

# UART and SPI settings
UART_DEV = "/dev/ttyAMA2"
SPI_BUS = 0
SPI_DEVICE = 0
SPI_SPEED_HZ = 1000000

# MPU-9250 register addresses
MPU9250_PWR_MGMT_1 = 0x6B
MPU9250_ACCEL_XOUT_H = 0x3B
MPU9250_GYRO_XOUT_H = 0x43

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
    # SPI setup
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEVICE)
    spi.max_speed_hz = SPI_SPEED_HZ

    # UART setup
    fd = os.open(UART_DEV, os.O_RDWR | os.O_NOCTTY)
    uart_set_speed(fd, 115200)

    mpu9250_initialize(spi)  # Initialize MPU-9250
    # 현재 SPI 모드 읽기
    current_mode = spi.mode
    print(f"Current SPI Mode: {current_mode}")
    
    while True:
        # Read accelerometer and gyroscope data
        accel_x, accel_y, accel_z = read_accel_data(spi)
        gyro_x, gyro_y, gyro_z = read_gyro_data(spi)

        # Prepare data string
        data = f"Accel X: {accel_x}, Accel Y: {accel_y}, Accel Z: {accel_z}\r\n"
        data += f"Gyro X: {gyro_x}, Gyro Y: {gyro_y}, Gyro Z: {gyro_z}\r\n"
        data += "---------------------------------------\r\n"

        # Print data to console
        print(data.strip())

        # Send data over UART
        uart_write_str(fd, data)
       
        time.sleep(1)  # Wait for 1 second
except KeyboardInterrupt:
    print("프로그램 종료")
finally:    
    spi.close()  # Close the SPI connection
    os.close(fd)  # Close the UART connection
