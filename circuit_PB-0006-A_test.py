import board
import digitalio
import busio
import time
import neopixel
from rainbowio import colorwheel
from adafruit_bme280 import basic as adafruit_bme280

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
    onbord_neopix = OnbordNeopix()
    
    i2c = busio.I2C(board.GP3, board.GP2)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    
    while True:
        onbord_neopix.rainbow_step()
        print("\nTemperature: %0.1f C" % bme280.temperature)
        print("Humidity: %0.1f %%" % bme280.relative_humidity)
        print("Pressure: %0.1f hPa" % bme280.pressure)
        print("Altitude = %0.2f meters" % bme280.altitude)
        time.sleep(1)

if __name__ == '__main__':
    main()