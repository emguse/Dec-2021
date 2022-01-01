import board
import digitalio
import busio
import time
import neopixel
from rainbowio import colorwheel
from adafruit_bme280 import basic as adafruit_bme280
import displayio
import terminalio
import adafruit_displayio_sh1107
from adafruit_display_text import label

class OnbordNeopix():
    def __init__(self) -> None:
        self.pixel = neopixel.NeoPixel(board.GP16, 1, auto_write=False)
        self.pixel.brightness = 0.3
        self.color_step = 0

    def rainbow(self, delay):
        for color_value in range(255):
            for led in range(1):
                pixel_index = (led * 256 // 1) + color_value
                self.pixel[led] = colorwheel(pixel_index & 255)
            self.pixel.show()
            time.sleep(delay)

    def rainbow_step(self): # Each time it is called, it advances the color one step
        self.color_step += 1
        self.pixel[0] = colorwheel(self.color_step & 255)
        self.pixel.show()

def main():
    displayio.release_displays()
    onbord_neopix = OnbordNeopix()
    
    i2c = busio.I2C(board.GP3, board.GP2)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
    display = adafruit_displayio_sh1107.SH1107(display_bus, width=128, height=64, rotation=0)
    
    while True:
        onbord_neopix.rainbow_step()
        
        tmp = ("Tmp: %0.1f C" % bme280.temperature)
        print(tmp)
        text_area1 = label.Label(terminalio.FONT, text=tmp)
        text_area1.x = 10
        text_area1.y = 10

        hum = ("Hum: %0.1f %%" % bme280.relative_humidity)
        print(hum)
        text_area2 = label.Label(terminalio.FONT, text=hum)
        text_area2.x = 10
        text_area2.y = 20

        prs = ("Prs: %0.1f hPa" % bme280.pressure)
        print(prs)
        text_area3 = label.Label(terminalio.FONT, text=prs)
        text_area3.x = 10
        text_area3.y = 30

        alt = ("Alt: %0.2f m" % bme280.altitude)
        print(alt)
        text_area4 = label.Label(terminalio.FONT, text=alt)
        text_area4.x = 10
        text_area4.y = 40

        now = displayio.Group()
        now.append(text_area1)
        now.append(text_area2)
        now.append(text_area3)
        now.append(text_area4)
        display.show(now)
        
        time.sleep(1)

if __name__ == '__main__':
    main()