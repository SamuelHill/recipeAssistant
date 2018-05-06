from __future__ import division
from gtts import gTTS
import re
import sys
import os
import time
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from MicrophoneStream import MicrophoneStream

next_array = ["next", "nex", "nexts", "next step", "then", "go on", "whats next", "continue", "more", "forward", "text"]

previous_array = ["previous", "back", "backwards", "backward", "last step", "prior", "previous step"]
repeat_array = ["again", "repeat", "say again", "say it again", "one more time"]
quantity_array = ["how much", "how many"]

"""

Data is envisioned as 

RecipeArray[] - Array of Steps
RecipeIndex - Current Index
Ingredients - Array of ingredient objects
"""



def remove_spaces(input_text):
    return input_text.strip()

def process_speech(speech):
    speech = set(speech)
    if speech & set(next_array):
        return next_step()
    elif speech & set(previous_array):
        return previous_step()
    elif speech & set(repeat_array):
        return repeat()
    elif detect_quantity(speech):
        match_ingredients(speech)
    # else:
    #     print("Sorry, I didn't understand.")



def next_step(self=None):
    return "Moving to next step..."
    # self.recipe_index += self.recipe_index + 1
    # return self.recipe_array[self.recipe_index]



def previous_step(self=None):
    return "Moving to previous step..."
    # self.recipe_index += self.recipe_index - 1
    # return self.recipe_array[self.recipe_index]

def repeat(self=None):
    return "Moving to previous step..."
    # return self.recipe_array[self.recipe_index]

def detect_quantity(str):
    for q in quantity_array:
        if q in str:
            return True
    return False


def match_ingredients(str, self=None):
    for i in self.ingredients:
        if i in str:
            return self.ingredients[i].quantity
    return False




