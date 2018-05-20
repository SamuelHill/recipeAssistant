from __future__ import division
from abc import ABCMeta, abstractmethod
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from gtts import gTTS
from pyaudio import PyAudio, paContinue, paInt16
from recipe_scrapers import scrape_me
# from data import substitutions
from six.moves import queue
from Tkinter import *

import os
# import re

# @TODO - make some of the class/static functions private as needed

substitutions = []

def real_dirname():
    return os.path.dirname(os.path.realpath(__file__))


def lazy_regex_search(regex, string):
    if regex in string.upper():  # assume regex is all upper
        return True
    return False


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = PyAudio()
        self._audio_stream = self._audio_interface.open(
            format = paInt16,
            channels = 1,
            rate = self._rate,
            input = True,
            frames_per_buffer = self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b''.join(data)
 

class Listening(ABCMeta('ABC', (), {})):
    # https://github.com/GoogleCloudPlatform/python-docs-samples/blob/
    # speech-continuous/speech/cloud-client/transcribe_streaming_indefinite.py
    DEFAULT_RATE = 16000
    DEFAULT_CHUNK = 1600
    DEFAULT_LANG = 'en-US'

    def __init__(self, rate = DEFAULT_RATE,
                 chunk = DEFAULT_CHUNK,
                 language_code = DEFAULT_LANG):
        # add google auth info for speech recognition (assuming file location)
        auth_location = real_dirname() + '/google-speech-recog-auth.json'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = auth_location
        # add instance variables
        self._rate = rate
        self._chunk = int(self._rate / 10)
        self.language_code = language_code


    @abstractmethod
    def process_speech(transcript):
        pass


    def config_and_start(self, wake_word):
        client = speech.SpeechClient()
        config = types.RecognitionConfig(
                encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz = self._rate,
                language_code = self.language_code)
        streaming_config = types.StreamingRecognitionConfig(
                config = config,
                interim_results = True)
        with MicrophoneStream(self._rate, self._chunk) as stream:
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content = audio)
                        for audio in audio_generator)
            responses = client.streaming_recognize(streaming_config, requests)
            self._transcription_loop(responses, wake_word)


    def _transcription_loop(self, responses, wake_word):
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue
            transcript = result.alternatives[0].transcript
            # Only process responses if they have the wake word
            if lazy_regex_search(wake_word, transcript):
                if result.is_final:
                    self.process_speech(transcript)
                    if lazy_regex_search('QUIT', transcript):  # ask to quit
                        break


class Recipe(object):
    """docstring for Recipe"""
    unit_types = dict()
    # METRIC (volume, weight)
    unit_types['milliliter'] = ['ml','milliliter','millilitre','cc','mL',
                                'milliliters','millilitres']
    unit_types['liter']      = ['l','liter','litre','L','liters','litres']
    unit_types['deciliter']  = ['dl','deciliter','decilitre','dL',
                                'deciliters','decilitres']
    unit_types['milligram']  = ['mg','milligram','milligramme',
                                'milligrams','milligrammes']
    unit_types['gram']       = ['g','gram','gramme','grams','grammes']
    unit_types['kilogram']   = ['kg','kilogram','kilogramme',
                                'kilograms','kilogrammes']
    # US CUSTOMARY (volume, weight)
    unit_types['drop']         = ['drop','dr','gt','gtt','drops','drs'] 
    unit_types['smidgen']      = ['smidgen','smdg','smi']
    unit_types['pinch']        = ['pinch','pn','pinchs','pinches']
    unit_types['dash']         = ['dash','ds','dashes']
    unit_types['saltspoon']    = ['saltspoon','scruple','ssp',
                                  'saltspoons','scruples','ssps']
    unit_types['coffeespoon']  = ['coffeespoon','csp','coffeespoons','csps']
    unit_types['fluid dram']   = ['fluid dram','fl.dr','fluid drams','fl.drs']
    unit_types['dessertspoon'] = ['dessertspoon','dsp','dssp','dstspn',
                                  'dessertspoons','dsps','dssps','dstspns']
    unit_types['teaspoon']     = ['teaspoon','t','tsp','teaspoons','tsps']
    unit_types['tablespoon']   = ['tablespoon','T','tbl','tbs','tbsp',
                                  'tablespoons','tbls','tbsps']
    unit_types['fluid ounce']  = ['fluid ounce','fl oz','fluid ounces',
                                  'fl ozs']
    unit_types['wineglass']    = ['wineglass','wgf','wineglasses','wgfs']
    unit_types['gill']         = ['gill','teacup','gills','teacups']
    unit_types['pottle']       = ['pottle','pot','pottles','pots']
    unit_types['cup']          = ['cup','c','cups']
    unit_types['pint']         = ['pint','p','pt','fl pt','pints','pts',
                                  'fl pts']
    unit_types['quart']        = ['quart','q','qt','fl qt','quarts','qts'
                                  'fl qts']
    unit_types['gallon']       = ['gallon','g','gal','gallons','gals']
    unit_types['pound']        = ['pound','lb','pounds','lbs']
    unit_types['ounce']        = ['ounce','oz','ounces','ozs']
    # DISTANCE:
    unit_types['millimeter'] = ['mm','millimeter','millimetre',
                                'millimeters','millimetres']
    unit_types['centimeter'] = ['cm','centimeter','centimetre',
                                'centimeters','centimetres']
    unit_types['inch']       = ['inch','\"','inches']
    unit_types['foot']       = ['foot','\'','feet']
    # ALL ABBREVIATIONS
    abbrevs = [abbrev for abbrevs in unit_types.values()
                                   for abbrev in abbrevs]

    def __init__(self, url, *args, **kwargs):
        self.url = url
        title, time, instructions, ingredients = self.parse()
        self.title = title
        self.time = time
        self.instructions = instructions
        self.ingredients = ingredients
        # self.title = kwargs.get('title',random_holes())


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
    def removeToken(string, token):
        string = string.replace(token, '')
        return string.strip()


    # @TODO - change this to be more robust (make less assumptions about the)
    #         numbers you are going to see... use regex? \d+(\.\d*)?
    @staticmethod
    def transformDigits(ingredient):
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
    def pluralize(value, string):
        if float(value) > 1.0:
            if string == 'foot':
                return 'feet'
            return string + 's'
        return string


    @classmethod
    def findParentheticals(cls, string):
        if string.find('(') != -1 and string.find(')') != -1:
            paren = string[string.find('('):string.find(')')+1]
            return paren, cls.removeToken(string, paren)
        return (None, string)


    @classmethod
    def findUnit(cls, quantity, value, string):
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
        if unit in cls.abbrevs:
            for real, abbrev in cls.unit_types.iteritems():
                if unit in abbrev:
                    unit = cls.pluralize(value, real)
            temp_string = cls.removeToken(string, unit)
            return unit, cls.removeToken(temp_string, quantity)
        return None, cls.removeToken(string, quantity)


    def parse(self):
        scrape = scrape_me(self.url)
        title = scrape.title()
        time = scrape.total_time()
        line_split_instructs = scrape.instructions().split('\n')
        instructions = [i for i in line_split_instructs if i is not '']
        raw_ingredients = []
        for ingredient in scrape.ingredients():
            processed_ingredient = dict.fromkeys(['quantity', 'value', 'unit',
                                                  'ingredient', 'extra'], None)
            extra, ingredient = Recipe.findParentheticals(ingredient)
            quantity, value = Recipe.transformDigits(ingredient)
            unit, ingredient = Recipe.findUnit(quantity, value, ingredient)
            processed_ingredient['ingredient'] = ingredient
            processed_ingredient['quantity'] = quantity
            processed_ingredient['value'] = value
            processed_ingredient['extra'] = extra
            processed_ingredient['unit'] = unit
            raw_ingredients.append(processed_ingredient)
        return title, time, instructions, raw_ingredients


class Assistant(Listening):
    START_EXAMPLES    = ['LETS GET STARTED', 'START']
    NEXT_EXAMPLES     = ['NEXT', 'NEX', 'NEXTS', 'NEXT STEP', 'THEN', 'GO ON',
                         'WHATS NEXT', 'CONTINUE', 'MORE', 'FORWARD', 'TEXT']
    PREV_EXAMPLES     = ['PREVIOUS', 'GO BACK', 'GO BACKWARDS', 'GO BACKWARD',
                         'LAST STEP', 'PRIOR', 'PREVIOUS STEP']
    REPEAT_EXAMPLES   = ['AGAIN', 'REPEAT', 'SAY AGAIN', 'SAY IT AGAIN',
                         'ONE MORE TIME']
    QUANTITY_EXAMPLES = ['HOW MUCH', 'HOW MANY']
    SUBSTITUTION_EXAMPLES = ['SUBSTITUTE', 'SUBSTITUTION', 'REPLACEMENT', 'REPLACE', 'SWAP']
    TIME_EXAMPLES = [["HOW LONG", "STEP"], ["HOW LONG", "CURRENT"], ["LENGTH", "STEP"], ["LENGTH", "CURRENT"],
                     ["HOW MANY", "MINUTES", "STEP"], ["HOW MANY", "MINUTES", "CURRENT"], ["HOW MUCH", "TIME", "STEP"],
                     ["HOW MUCH", "TIME", "CURRENT"]]


    def __init__(self, url, wake_word):
        super(Assistant, self).__init__()
        self.wake_word = wake_word
        self.recipe = Recipe(url)
        self.current_step = 0
        # https://gordonlesti.com/use-tkinter-without-mainloop/
        # self.root = Tk()
        # self.setupMaster()


    def newRecipe(self, url):
        self.recipe = Recipe(url)


    def setupMaster(self):
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
        self.addIngredientsToGUI()
        text = 'Instructions'
        instruction_label = Label(self.root, text = text, font = default_font)
        self.instruction_list = Text(self.root, borderwidth = 0, wrap = WORD,
                                font = default_font)
        self.addInstructionsToGUI()
        main_label.grid(row = 0, column = 0, columnspan = 2)
        input_label.grid(row = 1, column = 0)
        output_label.grid(row = 1, column = 1)
        self.recipe_assistant_input.grid(row = 2, column = 0)
        self.recipe_assistant_output.grid(row = 2, column = 1)
        # What about row 3?
        ingredient_label.grid(row = 4, column = 0)
        instruction_label.grid(row = 4, column = 1)
        self.ingredient_list.grid(row = 5, column = 0)
        self.instruction_list.grid(row = 5, column = 1)


    def addIngredientsToGUI(self):
        for ingredient in self.recipe.ingredients:
            self.ingredient_list.insert(END, u'\u00B7', 'bullets')
            pretty = self.recipe.readableIngredient(ingredient)
            self.ingredient_list.insert(END, pretty)
            self.ingredient_list.insert(END, '\n\n')


    def addInstructionsToGUI(self):
        for instruction in self.recipe.instructions:
            self.instruction_list.insert(END, u'\u00B7', 'bullets')
            self.instruction_list.insert(END, instruction)
            self.instruction_list.insert(END, '\n\n')


    @staticmethod
    def speak(text):
        # self.recipe_assistant_output.insert(END, text)
        if text:
            speaker = gTTS(text = text, lang = 'en', slow = False)
            speaker.save(real_dirname() + '/tmp.mp3')
            os.system('mpg321 -q ' + real_dirname() + '/tmp.mp3')
        else:
            print text, 'Nothing'


    @staticmethod
    def check_examples(transcript, examples):
        found = False
        for example in examples:
            if lazy_regex_search(example, transcript):
                found = True
                break
        return found

    @staticmethod
    def check_examples_multiple(transcript, examples):
        found = False
        for example in examples:
            for i in range(0, len(example)):
                if not lazy_regex_search(example[i], transcript):
                    continue
                elif i == len(example) - 1:
                    found = True
                    break
        return found

    @classmethod
    def checkAndSpeak(cls, transcript, examples, function, multiple=None):
        if multiple:
            if cls.check_examples_multiple(transcript, examples):
                cls.speak(function(transcript))
                return True

        else:
            if cls.check_examples(transcript, examples):
                cls.speak(function(transcript))
                return True

        return False


    def process_speech(self, transcript):
        # self.recipe_assistant_input.insert(END, transcript)
        # self.root.update()
        if self.checkAndSpeak(transcript, self.START_EXAMPLES,
                              self.start):
            return
        elif self.checkAndSpeak(transcript, self.NEXT_EXAMPLES,
                                self.next_step):
            return
        elif self.checkAndSpeak(transcript, self.PREV_EXAMPLES,
                                self.prev_step):
            return
        elif self.checkAndSpeak(transcript, self.REPEAT_EXAMPLES,
                                self.repeat_step):
            return
        elif self.checkAndSpeak(transcript, self.QUANTITY_EXAMPLES,
                                self.match_ingredients):
            return
        elif self.checkAndSpeak(transcript, self.SUBSTITUTION_EXAMPLES,
                                self.substitute_ingredients):
            return
        # elif self.checkAndSpeak(transcript, self.TIME_EXAMPLES,
        #                         self.length_of_step, True):
        #     return
        else:
            self.speak('Sorry, I didn\'t understand.')
        # self.root.update()


    def config_and_start(self):
        super(Assistant, self).config_and_start(self.wake_word)


    def currentInstruction(self):
        return self.recipe.instructions[self.current_step]


    def start(self, *_):
        if self.current_step == 0:
            text = 'Today we will be cooking ' + self.recipe.title + '. '
            text += 'To start, ' + self.currentInstruction()
        else:
            self.current_step = 0
            text += 'Starting from the beginning, ' + self.currentInstruction()
        return text


    def next_step(self, *_):
        self.current_step += 1
        return self.currentInstruction()


    def prev_step(self, *_):
        self.current_step -= 1
        return self.currentInstruction()


    def repeat_step(self, *_):
        return self.currentInstruction()


    def time_of_step(self, *_):
        instruction = self.currentInstruction().upper()

        until = instruction.find("UNTIL")
        if until:
            return self.get_sentence(instruction, until)

        minutes = instruction.find("MINUTES")

        if minutes:
            return self.get_sentence(instruction, minutes)

        minute = instruction.find("MINUTE")
        if minute:
            return self.get_sentence(instruction, minute)
        return "No time for step found"

    def get_sentence(self, paragraph, index):
        start = index - 1
        end = index

        while start > 0:
            if paragraph[start] == '.' and (not paragraph[start + 1].isdigit()):
                break
            else:
                start -= 1
        while end < len(paragraph):
            if end == len(paragraph) - 1:
                break

            if paragraph[end] == "." and (not paragraph[end + 1].isdigit()):
                break
            else:
                end += 1

        if start < 0:
            start = 0

        if end >= len(paragraph):
            end = len(paragraph) - 1
        return paragraph[start, end + 1]






    # @TODO - Limit ingredient search to ingredients in this step
    def match_ingredients(self, transcript):
        for ingredient in self.recipe.ingredients:
            if lazy_regex_search(ingredient['ingredient'].upper(), transcript):
                return self.recipe.readableIngredient(ingredient)
        return False

    def substitute_ingredients(self, transcript):
        ingredient = self.match_ingredients(transcript)
        if ingredient:
            return "For" + substitutions[ingredient][0] + " of " + ingredient + " use " + substitutions[ingredient[1]]
        else:
            return "No substitutions found"
    

    # @TODO - list all ingredients in step
    # @TODO - list all (regardless)
    # @TODO - what is/how do you use
    # @TODO - substitution
    # @TODO - healthy/vegan/veggie subs
    # @TODO - time (from instructions)


def main():
    url = 'https://www.allrecipes.com/recipe/260895/banana-poppy-seed-pancakes'
    url += '/?internalSource=popular&referringContentType=home%20page&clickId='
    url += 'cardslot%2038'
    assist = Assistant(url, 'GORDON')
    assist.config_and_start()


if __name__ == '__main__':
    main()
