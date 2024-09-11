import time


class CustomRandom:
    def __init__(self, seed: int = None):
        if seed is None:
            seed = int(time.time() * 1000)
        self.m = 2**32
        self.a = 1664525
        self.c = 1013904223
        self.state = seed

    def random(self):
        self.state = (self.a * self.state + self.c) % self.m
        return self.state / self.m


def simple_event_generator(probability: float, seed: int = None):
    rand_gen = CustomRandom(seed)
    while True:
        yield rand_gen.random() <= probability
