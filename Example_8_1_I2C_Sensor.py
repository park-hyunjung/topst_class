import smbus2
import serial
import time

# Constants
I2C_BUS = 1
GY302_ADDR = #TODO
CMD_POWER_ON = #TODO
CMD_RESET = #TODO
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
    #TODO
    time.sleep(0.1)
    
    # Reset the sensor
    #TODO
    time.sleep(0.1)
    
    # Set continuous high-resolution mode
    bus.write_byte(GY302_ADDR, CMD_CONT_H_RES_MODE)
    time.sleep(0.5)
    
    # Read data from the sensor
    #TODO
    
    # Convert data to lux
    #TODO
    return lux

try:
    while True:
        # Read lux value
        #TODO
        
        # Send lux value via serial
        #TODO
        
except KeyboardInterrupt:
    print("프로그램 종료")
finally:
    # Close the I2C bus and serial port
    bus.close()
    ser.close()
