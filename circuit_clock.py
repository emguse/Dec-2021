import time
import board
import busio
import bitbangio
import neopixel
import digitalio
from rainbowio import colorwheel
from circuit_rtc_ds3231 import RtcDs3231
from adafruit_ht16k33.segments import BigSeg7x4

'''
- 2021/12/22 ver.0.03
- Author : emguse
- License: MIT License
'''
'''
Hardware requirements
- Adafruit QT Py RP2040
- Adafruit DS3231 Precision RTC-STEMMA QT
- Adafruit 1.2" 4-Digit 7-Segment Display w/I2C Backpack - Yellow
- self-excited buzzer(optional)
- NPN transistor
- 10k Ohm resistor
'''

BUZZER_PIN = board.D4 # D4 silk is SDA
USE_BUZZER = True
TIME_ADJUSTING = False
TIME_TO_SET = (2021, 12, 23, 20, 21, 00, 4, -1, -1)
# TIME_TO_SET = (year, mon, date, hour, min, sec, wday, yday, isdst)
# Year, month, day, hour, minute, second, and weekday are required.
# weekday is Number between [0,6], where Monday is 0
# Substitute "-1" for "yearday, isdst".

print("Hello World!")

class OnbordNeopix():
    def __init__(self) -> None:
        self.pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=False)
        self.pixel.brightness = 0.1
        self.color_step = 0

    def rainbow(self, delay):
        for color_value in range(255):
            for led in range(1):
                pixel_index = (led * 256 // 1) + color_value
                self.pixel[led] = colorwheel(pixel_index & 255)
            self.pixel.show()
            time.sleep(delay)

    def rainbow_step(self):
        self.color_step += 1
        self.pixel[0] = colorwheel(self.color_step & 255)
        self.pixel.show()

class PiPi():
    def __init__(self) -> None:
        self.buzzer = digitalio.DigitalInOut(BUZZER_PIN)
        self.buzzer.direction = digitalio.Direction.OUTPUT
    def pi(self, count) -> None:
        for i in range(count):
            self.buzzer.value = True
            time.sleep(0.03)
            self.buzzer.value = False
            time.sleep(0.03)

def main():
    i2c = bitbangio.I2C(board.SCL1, board.SDA1)
    rtc = RtcDs3231(i2c)
    display = BigSeg7x4(i2c)
    display.brightness = 0.5
    onbord_neopix = OnbordNeopix()
    buzzer = PiPi()
    buzzer.pi(2)

    if TIME_ADJUSTING:
        rtc.time_adjusting = True
        rtc.time_to_set = TIME_TO_SET
        rtc.adjust()
        rtc.time_adjusting = False
        t = rtc.read()
        print(t)

    while True:
        onbord_neopix.rainbow_step()
        t = rtc.read()
        tstamp = str(
            "{:04}{:02}{:02}T{:02}{:02}{:02}".format(
                t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec
            ))
        print(tstamp)
        display.print("{:02}{:02}".format(t.tm_hour, t.tm_min))
        # Blinking cologne
        if t.tm_sec % 2 == 0:
            display.colon = True
        else:
            display.colon = False
        if USE_BUZZER:
            if t.tm_min + t.tm_sec == 0:
                buzzer.pi(2)
            if t.tm_min == 30:
                if t.tm_sec == 0:
                    buzzer.pi(1)
        time.sleep(1)

if __name__ == '__main__':
    main()
