from Tkinter import *
# import tkFont

## TODO:
    # button in input box to serve as temporary wakeword for demo
    # wrap current speech_to_text, call it upon clicking the button
    # wrap recipe parser and extract info for ingredients and recipe boxes
    # make a fxn that uses stt to call upon a couple of built-in recipes and display them

class App:

    def __init__(self, master):

        main_label = Label(master, text="Welcome to the Recipe Assistant", font=("Courier", 24)).grid(row=0, column=0, columnspan=2)
        recipe_assistant_input_label = Label(master, text="Input", font=("Courier", 16)).grid(row=1, column=0)
        recipe_assistant_output_label = Label(master, text="Output", font=("Courier", 16)).grid(row=1, column=1)

        recipe_assistant_input = Text(master).grid(row=2, column=0)
        recipe_assistant_output = Text(master).grid(row=2, column=1)

        ingredients_label = Label(master, text="Ingredients", font=("Courier", 16)).grid(row=3, column=0)
        recipe_label = Label(master, text="Recipe", font=("Courier", 16)).grid(row=3, column=1)

        ingredients_list = Listbox(master, borderwidth=0, font=("Courier", 12))
        for item in ["one", "two", "three", "four"]:
            ingredients_list.insert(END, ("ingredient {}").format(item))
        ingredients_list.grid(row=4, column=0)

        recipe_list = Listbox(master, borderwidth=0, font=("Courier", 12))
        for item in ["one", "two", "three", "four"]:
            recipe_list.insert(END, ("step {}").format(item))
        recipe_list.grid(row=4, column=1)

root = Tk()

app = App(root)

root.mainloop()
root.destroy()
