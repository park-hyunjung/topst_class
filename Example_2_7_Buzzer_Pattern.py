import os
import time

# GPIO 핀 번호
GPIO_PINS = 89

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
    # GPIO 해제
    gpio_cleanup(GPIO_PINS)
    # GPIO 초기화 및 핀 설정
    gpio_setup(GPIO_PINS)

    while True:
        # Buzzer를 패턴동작으로 켜고 끄기
        gpio_write(GPIO_PINS, 1)
        print("대~~")
        time.sleep(1)
        gpio_write(GPIO_PINS, 0)
        time.sleep(0.1)

        gpio_write(GPIO_PINS, 1)
        print("한!")
        time.sleep(0.4)
        gpio_write(GPIO_PINS, 0)
        time.sleep(0.1)

        gpio_write(GPIO_PINS, 1)
        print("민!")
        time.sleep(0.3)
        gpio_write(GPIO_PINS, 0)
        time.sleep(0.1)

        gpio_write(GPIO_PINS, 1)
        print("국!")
        time.sleep(0.3)
        gpio_write(GPIO_PINS, 0)
        time.sleep(0.1)

        print("짝짝~ 짝 짝! 짝!")
        time.sleep(3)

except KeyboardInterrupt:
    gpio_write(GPIO_PINS, 0)
    print("프로그램 종료")

finally:
    gpio_cleanup(GPIO_PINS)
