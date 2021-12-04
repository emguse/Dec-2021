from circuit_ring_buffer import RingBuffer

class MovingAverage():
    def __init__(self, length:int, zero_fill=True) -> None:
        self.length = abs(length)
        if self.length == 0:
            self.length = 1
        self.rb = RingBuffer(self.length) 
        if zero_fill == True:
            for i in range(self.length):
                self.rb.append(0)
    def simple_moving_average(self, new_value) -> float: 
        self.rb.append(new_value)
        sma = sum(self.rb.ring) / self.length
        return sma

def main():
    ma = MovingAverage(5)
    l = [1,2,3,4,5,6,7,8,9,10]
    for i in l:
        print(ma.simple_moving_average(i))

if __name__ == "__main__":
    main()