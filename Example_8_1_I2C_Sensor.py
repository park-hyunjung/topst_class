import smbus2
import serial
import time

# Constants
I2C_BUS = 1
GY302_ADDR = 0x23
CMD_POWER_ON = 0x01
CMD_RESET = 0x07
CMD_CONT_H_RES_MODE = 0x10

SERIAL_PORT = '/dev/ttyAMA2'
BAUD_RATE = 115200

# Initialize I2C bus and serial port
bus = smbus2.SMBus(I2C_BUS)
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

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
    while True:
        # Read lux value
        lux_value = int(read_lux())
        print(f"Lux: {lux_value}")
        
        # Send lux value via serial
        ser.write(f"Lux: {lux_value}\r\n".encode())
        
except KeyboardInterrupt:
    print("프로그램 종료")
finally:
    # Close the I2C bus and serial port
    bus.close()
    ser.close()
