import time
from typing import List


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
        yield probability >= rand_gen.random()


def complex_event_generator(probability: List[float], seed: int = None) -> List[bool]:
    rand_gen = CustomRandom(seed)
    event_list = []
    for prob in probability:
        event_list.append(prob >= rand_gen.random())
    return event_list


def complex_event_of_dependent_events_generator(
    p_a: float, p_b_given_a: float, seed: int = None
):
    rand_gen = CustomRandom(seed)

    p_not_a = 1 - p_a
    p_b_given_not_a = 1 - p_b_given_a
    p_not_b_given_a = 1 - p_b_given_a

    p_ab = p_a * p_b_given_a
    p_a_not_b = p_a * p_not_b_given_a
    p_not_a_b = p_not_a * p_b_given_not_a
    p_not_a_not_b = p_not_a * (1 - p_b_given_not_a)

    total_prob = p_ab + p_a_not_b + p_not_a_b + p_not_a_not_b
    p_ab /= total_prob
    p_a_not_b /= total_prob
    p_not_a_b /= total_prob
    p_not_a_not_b /= total_prob

    while True:
        rand_value = rand_gen.random()

        if rand_value <= p_ab:
            yield 0
        elif rand_value <= p_ab + p_a_not_b:
            yield 1
        elif rand_value <= p_ab + p_a_not_b + p_not_a_b:
            yield 2
        else:
            yield 3
