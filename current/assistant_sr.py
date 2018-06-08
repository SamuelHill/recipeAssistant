# from __future__ import division
import os
import re
import random
import speech_recognition as sr
from gtts import gTTS
from recipe_scrapers import scrape_me
from Tkinter import *
from data import *


GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""{
  "type": "service_account",
  "project_id": "turnkey-lacing-201318",
  "private_key_id": "d84912f93175bbb9e135f1bde35b1f33f423489d",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDBlfoqYvglhbm/\nHYasMPqXEImyTksz+g8ktOONey0L6txhRssAzwTsIOf4E7Ejw0pI5OZW+KUd7+1X\nO22+qxjLSCn4rsdEq+QyjXf//ZGfy8QTtJXxr/IRlnxgmRfe24pltZM4cuJN7TFa\n2mcX6M4zddM2/b27EfKw8ApDGjibUBkTyZ3yFTQTdIAFXXwKIgmxjxLBXNPWb11/\nBzTHVpdaCKi39tMtj5ojJt0WvzUz2dhES9z/LATpVAycU8skpBjSRNZ5u538FVoF\nXWnU2ycC/6WfxhQ3vtdDF7B0uTGCL71lD7UZXPFQY2U1jF86E2uIVSbWmtCaC8Si\nJNGecXj7AgMBAAECggEADsvyy0k1gQS3xGRlqVHn4LxKXuWK7DLWWntn4Ax36BVj\neYOXbuN9k4dJkJXMvRhaj4TNGGO4ymq1RpNYmZgEjqRgiBoWSbW+/QaakzRwbF+y\nVPR0kfzDvdVo6PQUT4JfXm1vdQNolp7YXjXoZse/W+gxi0TM1KvHOmZpzZdtytOS\nWxjOL7Pgn0CCi1u71OCB+OkM4mcigj4+90X0J9FiIot5X3qma/KFCMhdQfC6eZ2B\n5ATNBK75FTZ3w14tRzTO4jc3T7Pub+vk5y5iEK8bmTNtq74fgilMqjMzNPwKVWHt\nKveWt2k/7zs3eaRuqhxesG+IIGehb57yd6fEEkpCkQKBgQDjzjszarAHo2dI+HEg\nnuRSkHpxMvL2Nt0gGOfWspaUmNwtfpVUhoUy8xQPiRYTYFTkKe5COb8FcMdcjpzD\niGwqm+J8atoxzb7TZ6mKV47Xf+AcBl63nPeFaRzfXkewqPG77V6MAz42FODMoQPd\nz+GXyuxL01A/WzLnzi2YKKpWCwKBgQDZi4f7nYvC/Hs0CsHuJ+8RQxhKW7tWLQg0\nda2I7cu946TBhCqoujKg85ssp4FSEntGIVTo5Blyu9Ts/9+qgMP+jfkUTyNCUCmq\nJ9moWp/wix6nopUfpG6RzeKP3kq9QjLPqTcGj1ZsV7zmvLI7fFhpTab4bACcfwU8\n1We5uwnu0QKBgFbORjbQh6VRedEPgqQoh96CWXX7MSPrQhWyB94DDWgwW24mlyav\nX+BLSjClTzkw8whChhzMPmMHV6CIY2oK+RS/c+1vFhf2S6npDWy+8pphiveC4eLb\nuGIo7KydE3pY1kyDJgz6S2F2UTcIgB2s0kzyMVqvehu6V8qHAU7C6C2DAoGAatvf\nL/lzbZQX8LhYCmQTSqdqhxwIKYx1O0+SrnAgZGYtx+DkE31i4SzITGb7XxU0+H3m\n938UAQfCz6fgdiBKJgAXGaLF7wzxamOoxsm9RqsPo8h499INfhFj+Md4bv7Vdqvo\nG5DNIur2H2ERK6coxpEeM2jZ5AWAzSEGknUNrAECgYEAgXIRXqwg+aSO1Mg6vyF7\n3DSJI62VEiljtREL+z9jY2VPV3BkmCg/vb5zT5mgNiO3fS4FL5kRrQxLz2MDr4Mj\nJElGRpl/wWoVN5DfaBY5GvBCXM8vdtwWKi4Y2+SLd1DiXgFYTrp+AEDzWaHDozoj\nHtJOnqRZLWo01IqYhhtMxVY=\n-----END PRIVATE KEY-----\n",
  "client_email": "cooking-assistant@turnkey-lacing-201318.iam.gserviceaccount.com",
  "client_id": "105827532822400372191",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cooking-assistant%40turnkey-lacing-201318.iam.gserviceaccount.com"
}"""


def real_dirname():
    return os.path.dirname(os.path.realpath(__file__))


# TODO - change this to be more robust (match without all uppercase, include
#        punctuation like - for hyphenated words)
def lazy_regex_search(regex, string):
    if regex in string.upper():  # assume regex is all upper
        return True
    return False


# TODO - make so this can save a recipe to file/load from file
# TODO - parse instructions to pull out time, utensils, methods...
# TODO - easier modification of recipe (substitute, changing quantity)
class Recipe(object):
    def __init__(self, url, *args, **kwargs):
        self.url = url
        title, time, instructions, ingredients = self._parse()
        self.title = title
        self.time = time
        self.instructions = instructions
        self.ingredients = ingredients

    def __str__(self):
        temp = self.title + '\n'
        temp += 'Time: ' + str(self.time) + '\n'
        temp += ' # INGREDIENTS # \n'
        for ingredient in self.ingredients:
            text = self.readableIngredient(ingredient)
            temp += '\t' + text + '\n'
        temp += ' # INSTRUCTIONS # \n'
        for instruction in self.instructions:
            temp += '\t' + instruction + '\n'
        return temp

    @staticmethod
    def readableIngredient(ingredient):
        readable = ingredient['quantity']
        if ingredient['unit']:
            readable += ' ' + ingredient['unit']
        readable += ' ' + ingredient['ingredient']
        if ingredient['extra']:
            readable += ' ' + ingredient['extra']
        return readable

    @staticmethod
    def _removeToken(string, token):
        string = string.replace(token, '')
        return string.strip()

    # TODO - change this to be more robust (make less assumptions about the)
    #        numbers you are going to see... use regex? \d+(\.\d*)?
    @staticmethod
    def _transformDigits(ingredient):
        digits = filter(str.isdigit, ingredient)
        if len(digits) == 3:
            quantity = digits[0] + ' ' + digits[1] + '/' + digits[2]
            value = float(digits[0]) + (float(digits[1]) / float(digits[2]))
            return quantity, value
        elif len(digits) == 2:
            quantity = digits[0] + '/' + digits[1]
            value = float(digits[0]) / float(digits[1])
            return quantity, value
        elif len(digits) == 1:
            return digits[0], float(digits[0])
        return None, None

    @staticmethod
    def _pluralize(value, string):
        if float(value) > 1.0:
            if string == 'foot':
                return 'feet'
            return string + 's'
        return string

    @classmethod
    def _findParentheticals(cls, string):
        if string.find('(') != -1 and string.find(')') != -1:
            paren = string[string.find('('):string.find(')')+1]
            return paren, cls._removeToken(string, paren)
        return (None, string)

    @classmethod
    def _findUnit(cls, quantity, value, string):
        words = string.split()
        unit = None
        if ' ' in quantity:
            unit_loc = words.index(quantity.split()[1]) + 1
        else:
            unit_loc = words.index(quantity) + 1
        if words[unit_loc] == 'fluid' or words[unit_loc] == 'fl':
            # assumes that finding fluid next to a number will always mean
            # that those two words following the number are the units.
            unit = 'fluid ' + words[unit_loc + 1]
        else:
            unit = words[unit_loc]
        if unit in abbrevs:
            for real, abbrev in unit_types.iteritems():
                if unit in abbrev:
                    unit = cls._pluralize(value, real)
            temp_string = cls._removeToken(string, unit)
            return unit, cls._removeToken(temp_string, quantity)
        return None, cls._removeToken(string, quantity)

    def _parse(self):
        scrape = scrape_me(self.url)
        title = scrape.title()
        time = scrape.total_time()
        line_split_instructs = scrape.instructions().split('\n')
        instructions = [i for i in line_split_instructs if i is not '']
        raw_ingredients = []
        for ingredient in scrape.ingredients():
            processed_ingredient = dict.fromkeys(['quantity', 'value', 'unit',
                                                  'ingredient', 'extra'], None)
            extra, ingredient = Recipe._findParentheticals(ingredient)
            quantity, value = Recipe._transformDigits(ingredient)
            unit, ingredient = Recipe._findUnit(quantity, value, ingredient)
            processed_ingredient['ingredient'] = ingredient
            processed_ingredient['quantity'] = quantity
            processed_ingredient['value'] = value
            processed_ingredient['extra'] = extra
            processed_ingredient['unit'] = unit
            raw_ingredients.append(processed_ingredient)
        return title, time, instructions, raw_ingredients

class Assistant(object):
    def __init__(self, url):
        super(Assistant, self).__init__()
        self.recipe = Recipe(url)
        self.current_step = 0
        # TODO - get the UI to be more responsive...
        #      - possibly redesign UI entirely? does it need one...
        # https://gordonlesti.com/use-tkinter-without-mainloop/
        self.root = Tk()
        self._setupMaster()

    def _setupMaster(self):
        self.root.title('Cooking Assistant')
        header_font = ('Courier', 24)
        default_font = ('Courier', 16)
        header_text = 'Welcome to the Recipe Assistant'
        main_label = Label(self.root, text = header_text, font = header_font)
        input_label = Label(self.root, text = 'Input', font = default_font)
        self.recipe_assistant_input = Text(self.root)
        output_label = Label(self.root, text = 'Output', font = default_font)
        self.recipe_assistant_output = Text(self.root)
        text = 'Ingredients'
        ingredient_label = Label(self.root, text = text, font = default_font)
        self.ingredient_list = Text(self.root, borderwidth = 0, wrap = WORD,
                                    font = default_font)
        for ingredient in self.recipe.ingredients:
            self.ingredient_list.insert(END, u'\u00B7', 'bullets')
            pretty = self.recipe.readableIngredient(ingredient)
            self.ingredient_list.insert(END, pretty)
            self.ingredient_list.insert(END, '\n\n')
        text = 'Instructions'
        instruction_label = Label(self.root, text = text, font = default_font)
        self.instruction_list = Text(self.root, borderwidth = 0, wrap = WORD,
                                font = default_font)
        for instruction in self.recipe.instructions:
            self.instruction_list.insert(END, u'\u00B7', 'bullets')
            self.instruction_list.insert(END, instruction)
            self.instruction_list.insert(END, '\n\n')
        main_label.grid(row = 0, column = 0, columnspan = 2)
        input_label.grid(row = 1, column = 0)
        output_label.grid(row = 1, column = 1)
        self.recipe_assistant_input.grid(row = 2, column = 0)
        self.recipe_assistant_output.grid(row = 2, column = 1)
        ingredient_label.grid(row = 3, column = 0)
        instruction_label.grid(row = 3, column = 1)
        self.ingredient_list.grid(row = 4, column = 0)
        self.instruction_list.grid(row = 4, column = 1)
        self.root.update()

    def addInputToGUI(self, input_text):
        self.recipe_assistant_input.insert(END, input_text + '\n')
        self.recipe_assistant_input.see('end')
        self.root.update()

    def _speak(self, text):
        self.recipe_assistant_output.insert(END, text + '\n\n')
        self.recipe_assistant_output.see('end')
        self.root.update()
        if text:
            speaker = gTTS(text = text, lang = 'en', slow = False)
            speaker.save(real_dirname() + '/tmp.mp3')
            os.system('mpg321 -q ' + real_dirname() + '/tmp.mp3')
        else:
            print text, 'Nothing'

    @staticmethod
    def _check_examples(transcript, examples):
        found = False
        for example in examples:
            if lazy_regex_search(example, transcript):
                found = True
                break
        return found

    # TODO - pull repeated patterns out into functions
    def process_speech(self, transcript):
        if lazy_regex_search('START', transcript):
            if self.current_step == 0:
                text = 'Today we will be cooking ' + self.recipe.title + '. '
                text += 'To start, ' + self._currentInstruction()
            else:
                self.current_step = 0
                text += 'Starting from the beginning, '
                text += self._currentInstruction()
            self._speak(text)
        elif self._check_examples(transcript, ['NEXT', 'GO ON', 'CONTINUE']):
            if lazy_regex_search('GO ON TO', transcript):
                self._goto(transcript)
            else:
                self.current_step += 1
                self._speak_step()
        elif self._check_examples(transcript, ['PREVIOUS', 'BACK', 'LAST']):
            if lazy_regex_search('GO BACK TO', transcript):
                self._goto(transcript)
            else:
                self.current_step -= 1
                self._speak_step()
        elif self._check_examples(transcript, ['AGAIN', 'REPEAT', 'ONE MORE']):
            if lazy_regex_search('DO I NEED TO DO', transcript):
                self._speak_step()
            elif self._check_examples(transcript, ['I NEED', 'INGREDIENT']):
                if lazy_regex_search('ALL THE INGREDIENTS', transcript):
                    self._speak(self._list_all_ingredients())
                else:
                    self._speak(self._list_all_ingredients_in_step())
            else:
                self._speak_step()
        elif lazy_regex_search('GO TO', transcript):
            self._goto(transcript)
        elif lazy_regex_search('HOW', transcript):
            if lazy_regex_search('MANY STEPS', transcript):
                self._speak(str(len(self.recipe.instructions)))
            elif self._check_examples(transcript, ['MANY MINUTES',
                                                   'MUCH TIME',
                                                   'LONG']):
                all_sentences = []
                instruction = self._currentInstruction()
                self._get_sentences(instruction, 'until', all_sentences)
                self._get_sentences(instruction, 'minutes', all_sentences)
                self._get_sentences(instruction, 'minute', all_sentences)
                time = ' '.join(all_sentences)
                if not time:
                    time = "No time for step found"
                self._speak(time)
            elif self._check_examples(transcript, ['MUCH', 'MANY']):
                step_ingredients = self._find_ingredients_in_step()
                match_step = None
                for ingredient in step_ingredients:
                    if lazy_regex_search(ingredient['ingredient'].upper(),
                                         transcript):
                        match_step = self.recipe.readableIngredient(ingredient)
                        break
                if match_step:
                    self._speak(match_step)
                else:
                    match = None
                    for ingredient in self.recipe.ingredients:
                        if lazy_regex_search(ingredient['ingredient'].upper(),
                                             transcript):
                            match = self.recipe.readableIngredient(ingredient)
                            break
                    if match:
                        self._speak('This is not used in the current step, ' +
                            'but you need ' + match)
                    else:
                        self._speak('Could not find that ingredient')
            elif self._check_examples(transcript, ['DO YOU', 'IS THAT USED']):
                match_primary = None
                for method in primary:
                    if lazy_regex_search(method.upper(), transcript):
                        match_primary = primary[method]
                        break
                if match_primary:
                    self._speak(match_primary)
            else:
                self._speak('Not sure how to answer that question.')
        elif self._check_examples(transcript, ['WHAT IS', 'WHAT ARE']):
            match_measurement = None
            for measure in measurements:
                if lazy_regex_search(measure.upper(), transcript):
                    match_measurement = measurements[measure]
                    break
            if match_measurement:
                self._speak(match_measurement)
            else:
                match_preparations = None
                for preparation in preparations:
                    if lazy_regex_search(preparation.upper(), transcript):
                        match_preparations = preparations[preparation]
                        break
                if match_preparations:
                    self._speak(match_preparations)
                else:
                    match_primary = None
                    for method in primary:
                        if lazy_regex_search(method.upper(), transcript):
                            match_primary = primary[method]
                            break
                        else:
                            if method[-1] == 'e':
                                methoding = method[:-1] + 'ing'
                            else:
                                methoding = method + 'ing'
                            if lazy_regex_search(methoding.upper(),
                                                 transcript):
                                match_primary = primary[method]
                                break
                    if match_primary:
                        self._speak(match_primary)
                    else:
                        if lazy_regex_search('THE INGREDIENTS', transcript):
                            self._do_list_ingredients(transcript)
                        else:
                            self._speak('Not sure how to answer that question')
        elif self._check_examples(transcript, ['I NEED', 'THE INGREDIENTS']):
            self._do_list_ingredients(transcript)
        elif self._check_examples(transcript, ['SUBSTITUTE',
                                               'SUBSTITUTION',
                                               'REPLACEMENT',
                                               'REPLACE',
                                               'SWAP']):
            ingredient_to_sub = None
            for ingredient in self.recipe.ingredients:
                if lazy_regex_search(ingredient['ingredient'].upper(),
                                     transcript):
                    ingredient_to_sub = ingredient['ingredient']
                    break
            sub = ''
            if ingredient_to_sub in substitutions:
                substitute = substitutions[ingredient_to_sub]
                sub = 'For ' + substitute[0] + ' of ' + ingredient_to_sub
                or_split = substitute[1].split(' OR ')
                sub += ' use ' + ', or use '.join(or_split)
            else:
                sub = 'No substitutions found'
            self._speak(sub)
        elif lazy_regex_search('IS THIS VEGETARIAN', transcript):
            vegetarian_nontype_list = self._check_type(vegetarian_nontype)
            print vegetarian_nontype_list
            if vegetarian_nontype_list:
                responce = 'I found some ingredients with meat in them, '
                responce += 'so I think this is not vegetarian.'
            else:
                responce = 'I didn\'t find any ingredients with meat in them, '
                responce += 'so I think this is vegetarian.'
            self._speak(responce)
        elif lazy_regex_search('IS THIS VEGAN', transcript):
            vegan_nontype_list = self._check_type(vegan_nontype)
            print vegan_nontype_list
            if vegan_nontype_list:
                responce = 'I found some animal product ingredients, '
                responce += 'so I think this is not vegan.'
            else:
                responce = 'I didn\'t find any animal product ingredients, '
                responce += 'so I think this is vegan.'
            self._speak(responce)
        elif lazy_regex_search('MAKE THIS VEGETARIAN', transcript):
            vegetarian_nontype_list = self._check_type(vegetarian_nontype)
            if vegetarian_nontype_list:
                print vegetarian_nontype_list
                replacements = self._replace_type(vegetarian_nontype_list,
                                                  vegetarian_rtype)
                replacements = 'To make this vegetarian ' + replacements
            else:
                replacements = 'I didn\'t find any ingredients with meat in '
                replacements += 'them, so I think this is vegetarian.'
            self._speak(replacements)
        elif lazy_regex_search('MAKE THIS VEGAN', transcript):
            vegan_nontype_list = self._check_type(vegan_nontype)
            if vegan_nontype_list:
                print vegan_nontype_list
                replacements = self._replace_type(vegan_nontype_list,
                                                  vegan_rtype)
                replacements = 'To make this vegan ' + replacements
            else:
                replacements = 'I didn\'t find any animal product ingredients'
                replacements += ', so I think this is vegan.'
            self._speak(replacements)
        else:
            self._speak('Sorry, I didn\'t understand.')

    def _currentInstruction(self):
        return self.recipe.instructions[self.current_step]

    def _speak_step(self):
        self._speak(self._currentInstruction())

    def _goto(self, transcript):
        digits = filter(str.isdigit, str(transcript))
        term_nums = {'FIRST'    : 1,  'SECOND'   : 2,  'THIRD'    : 3,
                     'FOURTH'   : 4,  'FIFTH'    : 5,  'SIXTH'    : 6,
                     'SEVENTH'  : 7,  'EIGHTH'   : 8,  'NINETH'   : 9,
                     'TENTH'    : 10, 'ELEVENTH' : 11, 'TWELFTH'  : 12}
        if digits:
            cast_digit = int(digits)
            if cast_digit <= len(self.recipe.instructions):
                self.current_step = cast_digit - 1
                self._speak_step()
            else:
                self._speak('There are not that many steps in this recipe.')
        else:
            found = ''
            for term, value in term_nums.iteritems:
                if lazy_regex_search(term, transcript):
                    if value <= len(self.recipe.instructions):
                        self.current_step = value - 1
                        found = self._currentInstruction()
                        break
                    else:
                        found = 'There are not that many steps in this recipe.'
            if found:
                self._speak(found)
            else:
                self._speak('I\'m not sure how to go to there')

    def _check_number_terms():
        for term, value in term_nums.iteritems:
            if lazy_regex_search(term, transcript):
                self.current_step = value
                return self._currentInstruction()
        return 'There are not that many steps in this recipe.'

    def _find_ingredients_in_step(self):
        ingredients_in_step = []
        current_step = self._currentInstruction().upper()
        for ingredient in self.recipe.ingredients:
            if lazy_regex_search(ingredient['ingredient'].upper(),
                                 current_step):
                ingredients_in_step.append(ingredient)
        return ingredients_in_step

    def _list_all_ingredients_in_step(self):
        step_ingredients = 'For this step you will need: '
        ingredients = self._find_ingredients_in_step()
        step_ingredients += self._list_ingredients(ingredients)
        return step_ingredients

    def _list_all_ingredients(self):
        recipe_ingredients = 'For this recipe you will need: '
        recipe_ingredients += self._list_ingredients(self.recipe.ingredients)
        return recipe_ingredients

    def _list_ingredients(self, ingredients):
        recipe_ingredients = ''
        for ingredient in ingredients[:-1]:
            recipe_ingredients += self.recipe.readableIngredient(ingredient)
            recipe_ingredients += ', '
        last = self.recipe.readableIngredient(ingredients[-1])
        recipe_ingredients += 'and ' + last
        return recipe_ingredients

    def _do_list_ingredients(self, transcript):
        check_all = lazy_regex_search('ALL THE INGREDIENTS', transcript)
        if check_all and not lazy_regex_search('THIS STEP', transcript):
            self._speak(self._list_all_ingredients())
        else:
            self._speak(self._list_all_ingredients_in_step())

    def _get_sentences(self, paragraph, term, all_sentences):
        m_index = [m.start() for m in re.finditer(term, paragraph)]
        for index in m_index:
            start = index - 1
            end = index
            while start >= 0:
                if self._non_decimal_period(paragraph, start):
                    start += 2
                    break
                else:
                    start -= 1
            while end < len(paragraph):
                if end == len(paragraph) - 1:
                    break
                elif self._non_decimal_period(paragraph, end):
                    break
                else:
                    end += 1
            start = 0 if start < 0 else start
            minute_sentence = paragraph[start:end + 1]
            if minute_sentence not in all_sentences:
                all_sentences.append(minute_sentence)
    
    @staticmethod
    def _non_decimal_period(text, index):
        return text[index] == '.' and not text[index + 1].isdigit()

    def _check_type(self, nontype):
        nontype_list = []
        for ingredient in self.recipe.ingredients:
            for category, ingredient_list in nontype.iteritems():
                for to_check in ingredient_list:
                    if lazy_regex_search(ingredient['ingredient'].upper(),
                                         to_check):
                        nontype_list.append([category, ingredient, to_check])
        return nontype_list

    def _replace_type(self, nontype_list, rtype):
        replacement = 'you will need to use the following replacement '
        replacement = 'ingredients: '
        for nontype in nontype_list[:-1]:
            substitute = random.choice(rtype[nontype[0]])
            nontype[1]['ingredient'] = substitute
            replacement += self.recipe.readableIngredient(nontype[1]) + ', '
        nontype[1]['ingredient'] = random.choice(rtype[nontype_list[-1][0]])
        replacement += 'and ' + self.recipe.readableIngredient(nontype[1])
        return replacement
        

def main():
    # url = 'https://www.allrecipes.com/recipe/260895/banana-poppy-seed-pancakes'
    # url += '/?internalSource=popular&referringContentType=home%20page&clickId='
    # url += 'cardslot%2038'
    url = 'https://www.allrecipes.com/recipe/16268/apple-pie/?internalSource=hub%20recipe&referringContentType=search%20results'
    wake_word = 'GORDON'
    assist = Assistant(url)
    # TODO - move this loop to assistant
    r = sr.Recognizer()
    with sr.Microphone() as source:
        assist.addInputToGUI('Please wait. Calibrating microphone...')
        r.adjust_for_ambient_noise(source, duration=5)
        while True:
            assist.addInputToGUI('Listening:')
            audio = r.listen(source)
            try:
                attempt = r.recognize_google_cloud(audio,
                            credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
                # attempt = r.recognize_sphinx(audio)
                if lazy_regex_search(wake_word, attempt.upper()):
                    if lazy_regex_search('QUIT', attempt.upper()):
                        break
                    assist.addInputToGUI(attempt)
                    assist.process_speech(attempt)
                attempt += '\''
                assist.addInputToGUI('\tGoogle thinks you said \'' + attempt)
            except sr.UnknownValueError:
                assist.addInputToGUI('\tGoogle could not understand audio')
            except sr.RequestError as e:
                assist.addInputToGUI('\tGoogle error; {0}'.format(e))


if __name__ == '__main__':
    main()
