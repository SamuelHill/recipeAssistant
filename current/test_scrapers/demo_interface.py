from Tkinter import *
from scrape import *
# import tkFont

## TODO:
    # button in input box to serve as temporary wakeword for demo
    # wrap current speech_to_text, call it upon clicking the button
    # wrap recipe parser and extract info for ingredients and recipe boxes
    # make a fxn that uses stt to call upon a couple of built-in recipes and display them

# scrape.scrapeRecipe('https://www.allrecipes.com/recipe/213262/sweet-and-savory-slow-cooker-pulled-pork/?internalSource=similar_recipe_banner&referringId=139603&referringContentType=recipe&clickId=simslot_2')

# print scrape.modules

class App:
    recipe = ()
    instrustions = []
    ingredients = []

    def get_recipe(self, url):
        self.recipe = scrapeRecipe(url)
        self.ingredients = formatRawIngredients(self.recipe[0])
        self.instrustions = self.recipe[1]

    # def display_ingredients():

    def __init__(self, master):
        self.recipe = ()

        self.get_recipe('https://www.allrecipes.com/recipe/213262/sweet-and-savory-slow-cooker-pulled-pork/?internalSource=similar_recipe_banner&referringId=139603&referringContentType=recipe&clickId=simslot_2')

        main_label = Label(master, text="Welcome to the Recipe Assistant", font=("Courier", 24)).grid(row=0, column=0, columnspan=2)
        recipe_assistant_input_label = Label(master, text="Input", font=("Courier", 16)).grid(row=1, column=0)
        recipe_assistant_output_label = Label(master, text="Output", font=("Courier", 16)).grid(row=1, column=1)

        recipe_assistant_input = Text(master).grid(row=2, column=0)
        recipe_assistant_output = Text(master).grid(row=2, column=1)

        ingredients_label = Label(master, text="Ingredients", font=("Courier", 16)).grid(row=3, column=0)
        recipe_label = Label(master, text="Steps", font=("Courier", 16)).grid(row=3, column=1)

        ingredients_list = Text(master, borderwidth=0, wrap=WORD, font=("Courier", 12))
        for item in self.ingredients:               #["one", "two", "three", "four"]:
            ingredients_list.insert(END, u'\u00B7', 'bullets')
            ingredients_list.insert(END, item)     #(END, ("ingredient {}").format(item))
            ingredients_list.insert(END, '\n\n')
        ingredients_list.grid(row=4, column=0)

        recipe_list = Text(master, borderwidth=0, wrap=WORD, font=("Courier", 12))
        for item in self.instrustions:                   #["one", "two", "three", "four"]:
            recipe_list.insert(END, u'\u00B7', 'bullets')
            recipe_list.insert(END, item)                   #(END, ("step {}").format(item))
            recipe_list.insert(END, '\n\n')
        recipe_list.grid(row=4, column=1)


root = Tk()

app = App(root)

root.mainloop()
root.destroy()
