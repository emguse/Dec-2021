import board
import busio
import time
from adafruit_bus_device.i2c_device import I2CDevice
import adafruit_ds3231

TIME_ADJUSTING = False

TIME_TO_SET = (2021, 12, 13, 20, 45, 00, 0, -1, -1)
# TIME_TO_SET = (year, mon, date, hour, min, sec, wday, yday, isdst)
# Year, month, day, hour, minute, second, and weekday are required.
# weekday is Number between [0,6], where Monday is 0
# Substitute "-1" for "yearday, isdst".

class RtcDs3231():
    def __init__(self,i2c: I2C) -> None:
        self.ds3231 = adafruit_ds3231.DS3231(i2c)
        self.time_adjusting = TIME_ADJUSTING
        self.time_to_set = TIME_TO_SET
    def adjust(self) -> None:
        if self.time_adjusting:
            t = time.struct_time(self.time_to_set)
            print("Time to set is:", t)
            self.ds3231.datetime = t
    def read(self):
        t = self.ds3231.datetime
        return t

def main():
    I2C_SCL = board.GP1
    I2C_SDA = board.GP0
    i2c = busio.I2C(scl=I2C_SCL, sda=I2C_SDA)
    rtc = RtcDs3231(i2c)
    rtc.adjust()
    t = rtc.read()
    print(t)

if __name__ == '__main__':
    main()


