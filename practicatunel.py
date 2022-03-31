import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "south"
NORTH = "north"

NCARS = 100

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.nobody_north = Condition(self.mutex)
        self.nobody_south = Condition(self.mutex)
        self.go_north = Value('i', 0)
        self.go_south = Value('i', 0)
        self.wait_north = Value('i', 0)
        self.wait_south = Value('i', 0)
        self.turn = Value('i', 0)
        #turn=0 north priority
        #turn=1 south priority

    def nobody_go_south(self):
        return (self.go_south.value == 0) and \
            (self.turn.value == 0 or self.wait_north.value == 0)

    def nobody_go_north(self):
        return (self.go_north.value == 0) and \
            (self.turn.value == 1 or self.wait_south.value == 0)
    
    def wants_enter(self, direction):
        self.mutex.acquire()
        if direction == NORTH:
            self.wait_north.value += 1
            self.nobody_south.wait_for(self.nobody_go_south)
            self.wait_north.value -= 1
            self.go_north.value += 1
        else:
            self.wait_south.value += 1
            self.nobody_north.wait_for(self.nobody_go_north)
            self.wait_south.value -= 1
            self.go_south.value += 1
        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        if self.go_north.value > 0:
            self.go_north.value -= 1
            self.turn.value = 1
            if self.go_north.value == 0:
                self.nobody_north.notify_all()
        elif self.go_south.value > 0:
            self.go_south.value -= 1
            self.turn.value = 0
            if self.go_south.value == 0:
                self.nobody_south.notify_all()
        self.mutex.release()
        #turn=0 north priority
        #turn=1 south priority
        
def delay(n=3):
    time.sleep(random.random()*n)

def car(cid, direction, monitor):
    print(f"car {cid} direction {direction} created")
    delay(6)
    print(f"car {cid} heading {direction} wants to enter")
    monitor.wants_enter(direction)
    print(f"car {cid} heading {direction} enters the tunnel")
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")



def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s

if __name__ == '__main__':
    main()
