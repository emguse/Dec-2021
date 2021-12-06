import board
import digitalio
from circuit_D6F_PH0505 import DifferentialPressureSensorD6F_PH0505 as D6F_PH0505
from circuit_move_ave import MovingAverage
from circuit_ring_buffer import RingBuffer
import time

CYCLE_TIME = 0.033  # sec
IVENT_LENGTH = 10  # sec
QUE_SIZE = int(IVENT_LENGTH/2 * 1/CYCLE_TIME)
MOVE_AVE_LENGTH = 2
REFARENCE_PAST_SAMPLE = 2
THRESHOLD = 0.25
ZERO_OFFSET = 0 # Zero point correction
USE_PRINTER = False
EXPORT_CSV = False
EXPORT_WAV = False
USE_BUZZER = True

class DifferentialPressureLogger():
    def __init__(self) -> None:
        self.rb_p = RingBuffer(QUE_SIZE)
        self.rb_ref = RingBuffer(REFARENCE_PAST_SAMPLE)
        self.d6f_ph0505 = D6F_PH0505()
        self.ma_p = 0
        self.past_sample = 0
    def read_dp(self) -> Float:
        self.d6f_ph0505.start_order()
        self.d6f_ph0505.read_order()
        return self.d6f_ph0505.diff_p
    def read_and_record(self) -> None:
        self.ma_p = self.read_dp() - ZERO_OFFSET
        self.rb_p.append(self.ma_p)
        self.rb_ref.append(self.ma_p)

class PiPi():
    def __init__(self) -> None:
        self.buzzer = digitalio.DigitalInOut(board.GP6)
        self.buzzer.direction = digitalio.Direction.OUTPUT
    def pi(self) -> None:
        self.buzzer.value = True
        time.sleep(0.03)
        self.buzzer.value = False

def main():
    logger = DifferentialPressureLogger()
    ma = MovingAverage(MOVE_AVE_LENGTH, True)
    buzzer = PiPi()
    past_time = 0 
    for _ in range(MOVE_AVE_LENGTH):
        logger.read_and_record()    
        logger.past_sample = logger.ma_p
    while True:
        logger.read_and_record()
        delta = logger.past_sample - logger.ma_p
        if past_time <= time.time():
            if abs(delta) >= THRESHOLD:
                #print("diff_p:" + str(round(ma_p, 4)) + "  Δ:" + str(round(delta, 4)) + "  time:" + str(time.time()))
                print((round(logger.ma_p, 4), round(delta, 4)))
                buzzer.pi()
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


if __name__ == "__main__":
    main()

