

'''
- 2021/12/20 ver.1.00
- Author : emguse
- License: MIT License
- note
This class was created as a temporary class because "Deque" was not supported by Circuitpython. 
It is assumed that it will be recreated with "Deque" when it is supported in the future.
'''

class RingBuffer:
    def __init__(self, length):
        self.size = length
        self.ring = [None] * length
        self.left = self.right = self.count = 0

    def popleft(self):
        if self.count == 0:
            raise IndexError("Que is enpty")
        data = self.ring[self.left]
        self.left += 1
        self.count -= 1
        if self.left == self.size:
            self.left = 0
        return data
    
    def pop(self):
        if self.count == 0:
            raise IndexError("Que is enpty")
        self.right -= 1
        self.count -= 1
        if self.right < 0:
            self.right = length - 1
        return self.ring[self.right]

    def append(self, data):
        #print(str(self.count) +","+str(len(self.ring)))
        if self.count == self.size:  # If the ring is full
            self.popleft()  # discard the first piece of data
        self.ring[self.right] = data
        self.right += 1
        self.count += 1
        if self.right == self.size:
            self.right = 0

    def appendleft(self, value):
        if self.count == self.size:  # If the ring is full
            self.pop()  # discard the last data
        self.left -= 1
        self.count += 1
        if self.left < 0:
            self.left = self.size - 1
        self.ring[self.left] = value
    
    def clear(self):
        self.left = self.right = self.count = 0
    
    def __len__(self):
        return self.count

if __name__ == "__main__":
    length = 5
    rbuf = RingBuffer(length)
    for i in range(length * 2):
        rbuf.append(i)
        print(rbuf.ring)
    for i in range(length):
        print(rbuf.popleft())