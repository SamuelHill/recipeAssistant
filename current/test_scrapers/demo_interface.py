from Tkinter import *
from scrape import *
import demo_google_speech_api
import threading

# To Use:
    # Run python demo_interface.py
    # dialog box pops up, click the button and talk
    # once you pause for long enough, recipe and ingredients pop up in respective boxes

# To Close:
    # close out of dialog box as normal
    # hit control+z (use actual control button, not command, on macs)

class App(threading.Thread):
    recipe = ()
    instrustions = []
    ingredients = []
    recipe_assistant_input = None
    recipe_assistant_output = None
    ingredients_list = None
    recipe_list = None
    clicked = False
    speech = ""
    app_root = None

    def ask_me_a_question(self): #(self, textbox):
        self.speech = demo_google_speech_api.main()
        self.clicked = True
        # textbox.insert(END, speech)

    def get_recipe(self, url):
        self.recipe = scrapeRecipe(url)
        self.ingredients = formatRawIngredients(self.recipe[0])
        self.instrustions = self.recipe[1]

    def __init__(self, master):
        self.recipe = ()


        main_label = Label(master, text="Welcome to the Recipe Assistant", font=("Courier", 24)).grid(row=0, column=0, columnspan=2)
        recipe_assistant_input_label = Label(master, text="Input", font=("Courier", 16)).grid(row=1, column=0)
        recipe_assistant_output_label = Label(master, text="Output", font=("Courier", 16)).grid(row=1, column=1)

        self.recipe_assistant_input = Text(master)
        self.recipe_assistant_input.insert(END, "Please click the button below to ask a question")
        self.recipe_assistant_input.grid(row=2, column=0)

        self.recipe_assistant_output = Text(master)
        self.recipe_assistant_output.grid(row=2, column=1)

        wake_button = Button(master, text="Ask Me a Question", command=self.ask_me_a_question).grid(row=3, column=0)

        ingredients_label = Label(master, text="Ingredients", font=("Courier", 16)).grid(row=4, column=0)
        recipe_label = Label(master, text="Steps", font=("Courier", 16)).grid(row=4, column=1)

        self.ingredients_list = Text(master, borderwidth=0, wrap=WORD, font=("Courier", 12))
        self.ingredients_list.grid(row=5, column=0)

        self.recipe_list = Text(master, borderwidth=0, wrap=WORD, font=("Courier", 12))
        self.recipe_list.grid(row=5, column=1)

        self.app_root = master
        threading.Thread.__init__(self)
        self.start()

    def print_speech_to_textbox(self):
        self.recipe_assistant_input.insert(END, self.speech)

    def add_ingredients_to_textbox(self):
        for item in self.ingredients:
            self.ingredients_list.insert(END, u'\u00B7', 'bullets')
            self.ingredients_list.insert(END, item)
            self.ingredients_list.insert(END, '\n\n')


    def add_steps_to_textbox(self):
        for item in self.instrustions:
            self.recipe_list.insert(END, u'\u00B7', 'bullets')
            self.recipe_list.insert(END, item)
            self.recipe_list.insert(END, '\n\n')

    def clear_textboxes(self):
        self.recipe_assistant_input.delete(1.0, END)
        self.recipe_list.delete(1.0, END)
        self.ingredients_list.delete(1.0, END)
        self.recipe_assistant_output.delete(1.0, END)


    def run(self):
        loop_active = True
        while loop_active:
            if self.clicked:
                self.clear_textboxes()
                self.print_speech_to_textbox()
                self.clicked = False
                self.get_recipe('https://www.allrecipes.com/recipe/213262/sweet-and-savory-slow-cooker-pulled-pork/?internalSource=similar_recipe_banner&referringId=139603&referringContentType=recipe&clickId=simslot_2')
                self.add_ingredients_to_textbox()
                self.add_steps_to_textbox()
                self.recipe_assistant_output.insert(END, "Here are your results!")

root = Tk()
app = App(root)
root.mainloop()
root.destroy()
