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

        if p_ab >= rand_value:
            yield 0, p_ab
        elif p_ab + p_a_not_b >= rand_value:
            yield 1, p_a_not_b
        elif p_ab + p_a_not_b + p_not_a_b >= rand_value:
            yield 2, p_not_a_b
        else:
            yield 3, p_not_a_not_b


def full_group_event_generator(probabilities: List[float], seed: int = None):
    rand_gen = CustomRandom(seed)

    if not (0.9999 < sum(probabilities) < 1.0001):
        raise ValueError(
            "The sum of the probabilities should be approximately equal to 1"
        )

    cummulative_probabilities = []
    cummulative_sum = 0

    for prob in probabilities:
        cummulative_sum += prob
        cummulative_probabilities.append(cummulative_sum)

    while True:
        rand_value = rand_gen.random()
        for index, cum_prob in enumerate(cummulative_probabilities):
            if cum_prob >= rand_value:
                yield index
                break
