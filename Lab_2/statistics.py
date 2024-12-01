import math
from decimal import Decimal
from enum import Enum, auto
from functools import reduce

import matplotlib.pyplot as plt
import numpy as np
import scipy as sp


class Distribution(Enum):
    pass


class ContinuousDistribution(Distribution):
    NORMAL = auto()
    EXPONENTIAL = auto()


class DiscreteDistribution(Distribution):
    GEOMETRIC = auto()
    POISSON = auto()


def clear_left(sorted_distribution, vals_part, width_part, cut_coeff):

    while True:
        vals_count = int(len(sorted_distribution) * vals_part)

        distribution_width = sorted_distribution[-1] - sorted_distribution[0]

        if distribution_width == 0:
            break

        shorted_part_width = sorted_distribution[vals_count] - sorted_distribution[0]
        shorted_part = shorted_part_width / distribution_width

        if shorted_part < width_part:
            return sorted_distribution

        trash_sep_width = shorted_part_width / vals_count * cut_coeff

        for i in range(vals_count):
            left_width_diff = (
                sorted_distribution[vals_count - i]
                - sorted_distribution[vals_count - i - 1]
            )

            if abs(left_width_diff) > abs(trash_sep_width):
                sorted_distribution = sorted_distribution[vals_count - i :]
                break

    return sorted_distribution


def clear(sorted_distribution, vals_part, width_part, cut_coeff):
    sorted_distribution = clear_left(
        sorted_distribution, vals_part, width_part, cut_coeff
    )
    sorted_distribution = clear_left(
        sorted_distribution[::-1], vals_part, width_part, cut_coeff
    )[::-1]

    return sorted_distribution


def get_x_axis(sorted_distribution, step):
    x_start = sorted_distribution[0] // step * step
    if x_start >= sorted_distribution[0]:
        x_start -= step

    current = x_start
    result = []

    while current <= sorted_distribution[-1]:
        result.append(current)
        current += step

    return result


def get_heights(x_axis, sorted_distribution):
    heights = [0] * len(x_axis)
    current_index = len(x_axis) - 1

    for value in reversed(sorted_distribution):
        if value > x_axis[current_index]:
            heights[current_index] += 1
        else:
            if value == x_axis[current_index]:
                heights[current_index] += 0.5
                heights[current_index - 1] += 0.5
            current_index -= 1

    return heights


def get_expected_value(distribution):
    return reduce(lambda x, y: x + y, distribution) / len(distribution)


def get_variance(distribution, expected_value):
    return (
        reduce(lambda x, y: x + y * y, distribution, 0) / len(distribution)
        - expected_value**2
    )


def lower_count(sorted_distribution, value):
    if len(sorted_distribution) == 0:
        return 0

    median = len(sorted_distribution) // 2

    if sorted_distribution[median] <= value:
        return median + 1 + lower_count(sorted_distribution[median + 1 :], value)
    else:
        return lower_count(sorted_distribution[:median], value)


def distribution_function(sorted_distribution, value):
    return lower_count(sorted_distribution, value) / len(sorted_distribution)


def draw_hist(cleared_sorted_distribution, step):
    x_axis = get_x_axis(cleared_sorted_distribution, step)
    heights = get_heights(x_axis, cleared_sorted_distribution)

    plt.bar([value + step / 2 for value in x_axis], heights, step)


def draw_distribution_plot(sorted_distribution, density, low, high):
    xs = np.linspace(low, high, density)
    ys = [distribution_function(sorted_distribution, x) for x in xs]

    plt.plot(xs, ys)


def draw_plot(function, density, low, high):
    xs = np.linspace(low, high, density)
    ys = [function(x) for x in xs]

    plt.plot(xs, ys)


def approximate(sorted_distribution, window):
    result = []

    for i in range(len(sorted_distribution) - window + 1):
        avg = sum(sorted_distribution[i : i + window]) / window
        result.append(avg)

    return result


def get_colmogorov_statistics(first_function, second_function, distribution):
    diff = np.max(
        [np.abs(first_function(value) - second_function(value)) for value in distribution]
    )
    return np.sqrt(len(distribution)) * diff


def get_p_value(k_statistics):
    max_iter = 1000000

    result = 0
    for k in range(1, max_iter + 1):
        term = (-1) ** (k - 1) * np.exp(-2 * k**2 * k_statistics**2)
        result += term

    return result * 2


def is_correct(p_value, alpha):
    return p_value >= alpha


def get_distribution_function_t(sorted_distribution):

    def distribution_function_t(value):
        return distribution_function(sorted_distribution, value)

    return distribution_function_t


def get_normal_distribution_function(mean, std):

    def normal_distribution_function(value):
        return 0.5 * (1 + math.erf((value - mean) / (std * np.sqrt(2))))

    return normal_distribution_function


def get_exponential_distribution_function(mean, std):
    if mean is not None and std is not None:
        raise ValueError(
            "Cannot provide both mean and std. Please provide one or the other."
        )
    elif mean is not None:
        lambda_ = 1 / mean
    elif std is not None:
        lambda_ = 1 / std
    else:
        raise ValueError("Must provide either mean or std.")

    def expontnential_distribution_function(value):
        if value < 0:
            return 0
        return 1 - math.exp(-lambda_ * value)

    return expontnential_distribution_function


def get_poisson_distribution_function(mean, std):
    if mean is not None and std is not None:
        raise ValueError(
            "Cannot provide both mean and std. Please provide one or the other."
        )
    elif mean is not None:
        lambda_ = mean
    elif std is not None:
        lambda_ = std * std
    else:
        raise ValueError("Must provide either mean or std.")

    def poisson_distribution_function(value):
        value = int(math.floor(value))
        return math.exp(-lambda_) * float(
            sum(
                [
                    Decimal(lambda_) ** k / Decimal(math.factorial(k))
                    for k in range(value + 1)
                ]
            )
        )

    return poisson_distribution_function


def get_geometric_distribution_function(mean, std):
    if mean is not None and std is not None:
        raise ValueError(
            "Cannot provide both mean and std. Please provide one or the other."
        )
    elif mean is not None:
        lambda_ = 1 / mean
    elif std is not None:
        lambda_ = (-1 + (1 + 4 * std**2) ** 0.5) / 2 / std**2
    else:
        raise ValueError("Must provide either mean or std.")

    def geometric_distribution_function(value):
        value = int(math.floor(value))
        return 1 - (1 - lambda_) ** value

    return geometric_distribution_function


def check_distribution(distribution_function, distribution, alpha):
    starting_distribution = get_distribution_function_t(distribution)

    statistics = get_colmogorov_statistics(
        distribution_function, starting_distribution, distribution
    )
    p_value = sp.stats.kstwobign.sf(statistics)

    if is_correct(p_value, alpha):
        return True

    return False


def get_inverse_normal_distribution_function(mean, std):  # should return function

    def inverse_normal_distribution_function(value):
        return mean + std * np.sqrt(2) * sp.special.erfinv(2 * value - 1)

    return inverse_normal_distribution_function


def get_inverse_exponential_distribution_function(mean, std):  # should return function
    if mean is not None and std is not None:
        raise ValueError(
            "Cannot provide both mean and std. Please provide one or the other."
        )
    elif mean is not None:
        lambda_ = 1 / mean
    elif std is not None:
        lambda_ = 1 / std
    else:
        raise ValueError("Must provide either mean or std.")

    def inverse_exponential_distribution_function(value):
        return -np.log(1 - value) / lambda_

    return inverse_exponential_distribution_function


def generate_continuous_distribution(distribution_function_inverse, random_values_sorted):
    result = []

    for value in random_values_sorted:
        result.append(distribution_function_inverse(value))

    return result


def generate_discrete_distribution(distribution_function, random_values_sorted):
    result = []
    i = 1
    current_p = distribution_function(i)

    for value in random_values_sorted:
        while value > current_p:
            i += 1
            current_p = distribution_function(i)
        result.append(i)

    return result


DISTRIBUTION_GENERATORS = {
    ContinuousDistribution.NORMAL: get_normal_distribution_function,
    ContinuousDistribution.EXPONENTIAL: get_exponential_distribution_function,
    DiscreteDistribution.GEOMETRIC: get_geometric_distribution_function,
    DiscreteDistribution.POISSON: get_poisson_distribution_function,
}

INVERSE_CONTINUOUS_DISTRIBUTION_GENERATORS = {
    ContinuousDistribution.NORMAL: get_inverse_normal_distribution_function,
    ContinuousDistribution.EXPONENTIAL: get_inverse_exponential_distribution_function,
}
