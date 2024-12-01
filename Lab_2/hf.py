import math
import time
from functools import reduce

import ipywidgets as widgets
import numpy as np
from IPython.display import display
from jupyter_ui_poll import ui_events


a = 6364136223846793005
c = 1
current = 0
RAND_MAX = 2**64


def set_seed(value):
    global current

    current = value


def random():
    global current

    current = (a * current + c) % RAND_MAX
    return current


def float_input(prompt, min, max, count, first_inclusive=True, last_inclusive=True):
    clicked = False

    prompt_widget = widgets.Label(value=prompt)

    probability_widgets = []

    for _ in range(count):
        probability_widgets.append(widgets.FloatText(placeholder=0.0))

    def on_button_clicked(button):
        nonlocal clicked
        clicked = True

    button = widgets.Button(description="Ok")
    button.on_click(on_button_clicked)

    display(prompt_widget, *probability_widgets, button)

    with ui_events() as poll:
        while True:
            if clicked:
                for probability_widget in probability_widgets:
                    if (
                        min < probability_widget.value < max
                        or (first_inclusive and min == probability_widget.value)
                        or (last_inclusive and max == probability_widget.value)
                    ):
                        prompt_widget.close()
                        for widget in probability_widgets:
                            widget.close()
                        button.close()
                        return [widget.value for widget in probability_widgets]
                clicked = False

            poll(10)
            time.sleep(0.1)


def int_input(prompt, min, max, count, first_inclusive=True, last_inclusive=True):
    clicked = False

    prompt_widget = widgets.Label(value=prompt)

    probability_widgets = []

    for _ in range(count):
        probability_widgets.append(widgets.IntText(placeholder=0.0))

    def on_button_clicked(button):
        nonlocal clicked
        clicked = True

    button = widgets.Button(description="Ok")
    button.on_click(on_button_clicked)

    display(prompt_widget, *probability_widgets, button)

    with ui_events() as poll:
        while True:
            if clicked:
                for probability_widget in probability_widgets:
                    if (
                        min < probability_widget.value < max
                        or (first_inclusive and min == probability_widget.value)
                        or (last_inclusive and max == probability_widget.value)
                    ):
                        prompt_widget.close()
                        for widget in probability_widgets:
                            widget.close()
                        button.close()
                        return [widget.value for widget in probability_widgets]
                clicked = False

            poll(10)
            time.sleep(0.1)


def selector(prompt, options):
    prompt_widget = widgets.Label(value=prompt)
    wgt = widgets.Dropdown(options=options, value=options[0])

    clicked = False

    def on_button_clicked(button):
        nonlocal clicked
        clicked = True

    button = widgets.Button(description="Ok")
    button.on_click(on_button_clicked)

    display(prompt_widget, wgt, button)

    with ui_events() as poll:
        while True:
            if clicked:
                prompt_widget.close()
                wgt.close()
                button.close()
                return wgt.value

            poll(10)
            time.sleep(0.1)
