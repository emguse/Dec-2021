import time
import board
import neopixel
from rainbowio import colorwheel

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
    onbord_neopix = OnbordNeopix()
    while True:
        onbord_neopix.rainbow(0.02)

if __name__ == '__main__':
    main()
