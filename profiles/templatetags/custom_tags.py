from django import template
import random

register = template.Library()

@register.filter(name="random_range")
def random_range(_=None):
    value = random.randint(10, 20)
    print(value,"random value ................")
    return range(value)

@register.filter(name="number_rangeobj")
def number_rangeobj(value : int):
    print(f"user given value = {value} range_obj = {range(value)}")
    return range(value)
