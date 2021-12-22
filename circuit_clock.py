import time
import board
import busio
import neopixel
from rainbowio import colorwheel
from circuit_rtc_ds3231 import RtcDs3231
from adafruit_ht16k33.segments import BigSeg7x4

'''
- 2021/12/22 ver.0.01
- Author : emguse
- License: MIT License
Hardware requirements
- Adafruit QT Py RP2040
- Adafruit DS3231 Precision RTC Breakout
- Adafruit 1.2" 4-Digit 7-Segment Display w/I2C Backpack - Yellow
'''

TIME_ADJUSTING = False
TIME_TO_SET = (2021, 12, 21, 23, 23, 00, 02, -1, -1)
# TIME_TO_SET = (year, mon, date, hour, min, sec, wday, yday, isdst)
# Year, month, day, hour, minute, second, and weekday are required.
# weekday is Number between [0,6], where Monday is 0
# Substitute "-1" for "yearday, isdst".

print("Hello World!")

class OnbordNeopix():
    def __init__(self) -> None:
        self.pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=False)
        self.pixel.brightness = 0.1

    def rainbow(self, delay):
        for color_value in range(255):
            for led in range(1):
                pixel_index = (led * 256 // 1) + color_value
                self.pixel[led] = colorwheel(pixel_index & 255)
            self.pixel.show()
            time.sleep(delay)

def main():
    i2c = busio.I2C(board.SCL1, board.SDA1)
    rtc = RtcDs3231(i2c)
    #display = BigSeg7x4(i2c)
    #display.brightness = 0.3
    #display.blink_rate = 3

    onbord_neopix = OnbordNeopix()

    if TIME_ADJUSTING:
        rtc.time_to_set = TIME_TO_SET
        rtc.adjust()
        rtc.time_adjusting = False
        t = rtc.read()
        print(t)

    while True:
        onbord_neopix.rainbow(0.02)

if __name__ == '__main__':
    main()
