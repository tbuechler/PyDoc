""" Hello :). """

## Imports incoming
import numpy as np

## Another import incoming :o
import torch


def mul(v1: float, v2: float):
    r""" 
    ## Multiplication of two float values. 
    
    Args:
    
    * `v1 (float)`:W
        * First factor
    * `v2 (float)`:
        * Second factor

    Returns:

    * `float`: Multiplication of `v1` and `v2`.
    """
    print("sad") # <- Is not shown in document because no comment before
    ## Return statement
    return (v1 * v2)

class Person:
    r"""
    # Person

    Represents a person by its name and age. 
    """
    def __init__(self, name, age):
        r"""
        Args:

        * `name (str)`:
            * Name of the person.
        * `age (int)`:
            * Age of the person.
        """
        self.name = name
        self.age = age

    def myfunc(self):
        r""" Introduce myself! """
        ## Greetings are printed.
        print("Hello my name is " + self.name)



