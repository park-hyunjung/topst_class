import os
import termios
import time
from enum import IntEnum

# UART and SPI settings
UART_DEV = #TODO

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
    attrs[TCATTRS.ISPEED] = baudrates[#TODO]
    attrs[TCATTRS.OSPEED] = baudrates[#TODO]
    attrs[TCATTRS.CFLAG] &= ~termios.CSIZE
    attrs[TCATTRS.CFLAG] |= termios.CS8 | termios.CLOCAL | termios.CREAD
    attrs[TCATTRS.LFLAG] &= ~(termios.ICANON | termios.ECHO | termios.ECHOE | termios.ISIG)
    attrs[TCATTRS.OFLAG] &= ~termios.OPOST
    termios.tcsetattr(fd, termios.TCSANOW, attrs)

def uart_write_str(fd:int, data:str):
   #TODO

def uart_read_str(fd:int):
   #TODO

try:
    # UART setup
    fd = os.open(UART_DEV, os.O_RDWR | os.O_NOCTTY)
#TODO
    
    while True:
        # Send data over UART
#TODO

except KeyboardInterrupt:
    print("프로그램 종료")
finally:
#TODO

    