import os
import time

# GPIO 핀 번호
GPIO_PINS = 83

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

# GPIO 해제 함수
# GPIO 핀이 이미 export되어 있는지 확인하고, 그렇다면 unexport
def gpio_cleanup(pin):
    if os.path.exists(f"/sys/class/gpio/gpio{pin}"):
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(pin))

try:
    gpio_cleanup(GPIO_PINS)
    gpio_setup(GPIO_PINS)

    while True:
        # LED 1개를 500ms 간격으로 켜고 끄기
        gpio_write(GPIO_PINS, 1)
        time.sleep(0.5)
        
        gpio_write(GPIO_PINS, 0)
        time.sleep(0.5)

except KeyboardInterrupt:
    gpio_write(GPIO_PINS, 0)
    print("프로그램 종료")

finally:
    gpio_cleanup(GPIO_PINS)
