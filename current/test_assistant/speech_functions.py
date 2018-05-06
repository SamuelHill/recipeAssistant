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



def remove_spaces(str):
    return str.strip()

def process_speech(speech):
    if speech in next_array:
        next_step()
    elif speech in previous_array:
        previous_step()
    elif speech in repeat_array:
        repeat()
    elif detect_quantity(speech):
        match_ingredients(speech)
    # else:
    #     print("Sorry, I didn't understand.")

def next_step(self=None):
    print("Moving to next step...")
    # self.recipe_index += self.recipe_index + 1
    # return self.recipe_array[self.recipe_index]



def previous_step(self=None):
    print("Moving to previous step...")
    # self.recipe_index += self.recipe_index - 1
    # return self.recipe_array[self.recipe_index]

def repeat(self=None):
    print("Moving to previous step...")
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


