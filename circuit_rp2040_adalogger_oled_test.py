import busio
import adafruit_pcf8523
import time
import board
import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label

displayio.release_displays()

i2c = busio.I2C(board.SCL, board.SDA)
rtc = adafruit_pcf8523.PCF8523(i2c)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

days = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")

if False:
    #t = time.struct_time((year, mon, date, hour, min, sec, wday, yday, isdst))
    t = time.struct_time((2021,  12,   18,   14,  41,  00,    6,   -1,    -1))
    print("Setting time to:", t)
    rtc.datetime = t

while True:
    t = rtc.datetime

    print("%s %d/%d/%d" % (days[t.tm_wday], t.tm_mday, t.tm_mon, t.tm_year))
    print("%d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec))

    dmy = ("%s %d/%d/%d" % (days[t.tm_wday], t.tm_mday, t.tm_mon, t.tm_year))
    text_area1 = label.Label(terminalio.FONT, text=dmy)
    text_area1.x = 10
    text_area1.y = 10

    hms = ("%d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec))
    text_area2 = label.Label(terminalio.FONT, text=hms)
    text_area2.x = 10
    text_area2.y = 20

    now = displayio.Group()
    now.append(text_area1)
    now.append(text_area2)

    display.show(now)

    time.sleep(1)
