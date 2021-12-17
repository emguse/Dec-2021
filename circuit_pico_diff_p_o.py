import board
import digitalio
from circuit_D6F_PH0505 import DifferentialPressureSensorD6F_PH0505 as D6F_PH0505
from circuit_move_ave import MovingAverage
from circuit_ring_buffer import RingBuffer
import time
import busio
import adafruit_thermal_printer
from circuit_rtc_ds3231 import RtcDs3231
import sdcardio

CYCLE_TIME = 0.033  # sec
IVENT_LENGTH = 10  # sec
QUE_SIZE = int(IVENT_LENGTH / 2 * 1 / CYCLE_TIME)
MOVE_AVE_LENGTH = 2
REFARENCE_PAST_SAMPLE = 2
THRESHOLD = 0.5
ZERO_OFFSET = 0  # Zero point correction
USE_PRINTER = False
EXPORT_CSV = False
EXPORT_WAV = False
USE_BUZZER = True
I2C_SCL = board.GP1
I2C_SDA = board.GP0
PRINTER_RX = board.GP13
PRINTER_TX = board.GP12
BUTTON_A = board.GP16
BUTTON_B = board.GP17
SPI_SCK = board.GP18
SPI_MOSI = board.GP19
SPI_MISO = board.GP20
SPI_CS = board.GP21
TIME_ADJUSTING = False
TIME_TO_SET = (2021, 12, 13, 20, 45, 00, 0, -1, -1)
# TIME_TO_SET = (year, mon, date, hour, min, sec, wday, yday, isdst)
# Year, month, day, hour, minute, second, and weekday are required.
# weekday is Number between [0,6], where Monday is 0
# Substitute "-1" for "yearday, isdst".

class DifferentialPressureLogger:
    def __init__(self) -> None:
        i2c = busio.I2C(scl=I2C_SCL, sda=I2C_SDA)
        self.rb_p = RingBuffer(QUE_SIZE)
        self.rb_ref = RingBuffer(REFARENCE_PAST_SAMPLE)
        self.d6f_ph0505 = D6F_PH0505(i2c)
        self.rtc = RtcDs3231(i2c)
        self.thermal_printer = PrinterDpEh600()
        self.ma_p = 0
        self.past_sample = 0
        self.button_up = digitalio.DigitalInOut(BUTTON_A)
        self.button_up.switch_to_input(pull=digitalio.Pull.DOWN)
        self.button_down = digitalio.DigitalInOut(BUTTON_B)
        self.button_down.switch_to_input(pull=digitalio.Pull.DOWN)
        self.threshold = THRESHOLD
        self.buzzer = PiPi()
    def read_dp(self) -> Float:
        self.d6f_ph0505.start_order()
        self.d6f_ph0505.read_order()
        return self.d6f_ph0505.diff_p
    def read_and_record(self) -> None:
        self.ma_p = self.read_dp() - ZERO_OFFSET
        self.rb_p.append(self.ma_p)
        self.rb_ref.append(self.ma_p)
    def time_adjusting(self) -> None:
        self.rtc.time_adjusting = True
        self.rtc.time_to_set = TIME_TO_SET
        self.rtc.adjust()
        t = self.rtc.read()
        print(t)
        self.rtc.time_adjusting = False
    def timestamp(self) -> None:
        t = self.rtc.read()
        print(
            "{}-{}-{}T{}:{}:{}".format(
                t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec
            )
        )
        self.thermal_printer.printer.print(
            "{}-{}-{}T{}:{}:{}".format(
                t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec
            )
        )
    def threshold_up(self) -> None:
        print("up")
        self.threshold = round(self.threshold + 0.1, 3)
        self.thermal_printer.printer.print("THRESHOLD:" + str(self.threshold))
        time.sleep(0.5)
    def threshold_down(self) -> None:
        print("down")
        self.threshold = round(self.threshold - 0.1, 3)
        self.thermal_printer.printer.print("THRESHOLD:" + str(self.threshold))
        time.sleep(0.5)

class PiPi:
    def __init__(self) -> None:
        self.buzzer = digitalio.DigitalInOut(board.GP6)
        self.buzzer.direction = digitalio.Direction.OUTPUT
    def pi(self) -> None:
        self.buzzer.value = True
        time.sleep(0.03)
        self.buzzer.value = False

class PrinterDpEh600:
    def __init__(self) -> None:
        self.TX = PRINTER_TX
        self.RX = PRINTER_RX
        self.Thermal_Printer = adafruit_thermal_printer.get_printer_class(2.69)
        self.uart = busio.UART(self.TX, self.RX, baudrate=115200)
        self.printer = self.Thermal_Printer(self.uart, auto_warm_up=False)
    def print(self, data) -> None:
        self.printer.print(data)
    def feed(self, lines) -> None:
        self.printer.feed(lines)

def main():
    logger = DifferentialPressureLogger()
    ma = MovingAverage(MOVE_AVE_LENGTH, True)
    past_time = 0

    spi = busio.SPI(SPI_SCK, MOSI=SPI_MOSI, MISO=SPI_MISO)
    cs = SPI_CS
    sdcard = sdcardio.SDCard(spi, cs)

    if TIME_ADJUSTING == True:
        logger.time_adjusting()
    logger.timestamp()
    logger.thermal_printer.printer.print("THRESHOLD:" + str(logger.threshold))

    for _ in range(MOVE_AVE_LENGTH):
        logger.read_and_record()
        logger.past_sample = logger.ma_p

    while True:
        logger.read_and_record()
        delta = logger.past_sample - logger.ma_p
        if past_time <= time.time():
            if abs(delta) >= logger.threshold:
                # print("diff_p:" + str(round(ma_p, 4)) + "  Δ:" + str(round(delta, 4)) + "  time:" + str(time.time()))
                print((round(logger.ma_p, 4), round(delta, 4)))
                logger.timestamp()
                logger.thermal_printer.printer.print(
                    str(
                        "diff_P:"
                        + str(round(logger.ma_p, 4))
                        + ", delta:"
                        + str(round(delta, 4))
                    )
                )
                logger.thermal_printer.printer.feed(1)
                logger.buzzer.pi()
                past_time = time.time() + IVENT_LENGTH
                for _ in range(QUE_SIZE):
                    logger.ma_p = logger.read_dp() - ZERO_OFFSET
                    after_p = []
                    after_p.append(logger.ma_p)
                for i in range(QUE_SIZE):
                    Forward_p = []
                    Forward_p.append(logger.rb_p.ring[i])
                Forward_p.extend(after_p)
        past_sample = logger.ma_p
        if logger.button_up.value:
            logger.threshold_up()
        if logger.button_down.value:
            logger.threshold_down()

if __name__ == "__main__":
    main()
