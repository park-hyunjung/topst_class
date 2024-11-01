import os
import time

# GPIO 핀 번호 리스트
GPIO_PINS = [112, 113, 114, 121, 117, 118, 120, 115]
#index = 0

# GPIO 초기화 함수
def gpio_setup(pin):
    # GPIO 핀을 내보내기 (export)
    with open("/sys/class/gpio/export", "w") as f:
        f.write(str(pin))
    
    # 핀 모드 설정 (출력)
    with open(f"/sys/class/gpio/gpio{pin}/direction", "w") as f:
        f.write("out")
      
# GPIO 상태 쓰기 함수
def gpio_write(pin, value):
    with open(f"/sys/class/gpio/gpio{pin}/value", "w") as f:
        f.write(str(value))

# GPIO 초기화 및 모든 핀 설정
def setup_all_pins():
    for pin in GPIO_PINS:
        gpio_setup(pin)

# GPIO 해제 함수
# GPIO 핀이 이미 export되어 있는지 확인하고, 그렇다면 unexport
def gpio_cleanup(pin):
    if os.path.exists(f"/sys/class/gpio/gpio{pin}"):
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(pin))

# 모든 GPIO 해제
def cleanup_all_pins():
    for pin in GPIO_PINS:
        gpio_cleanup(pin)

try:
    cleanup_all_pins()
    setup_all_pins()

    while True:
        # LED 8개를 500ms 간격으로 이동해서 켜기
        for pin in GPIO_PINS:
            gpio_write(pin, 1)
            time.sleep(0.5)
            
            pre_pin = pin
            gpio_write(pre_pin, 0)

except KeyboardInterrupt:
    for pin in GPIO_PINS:
        gpio_write(pin, 0)
    print("프로그램 종료")

finally:
    cleanup_all_pins()