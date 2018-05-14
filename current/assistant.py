from __future__ import division
from six.moves import queue
import os
from pyaudio import PyAudio, paContinue, paInt16
from abc import ABCMeta, abstractmethod
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from gtts import gTTS
from recipe_scrapers import scrape_me
# import time


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
                    if lazy_regex_search('STOP', transcript):  # ask gordon to stop
                        break


class Assistant(Listening):
    START_EXAMPLES = ['LETS GET STARTED', 'START']
    NEXT_EXAMPLES = ['NEXT', 'NEX', 'NEXTS', 'NEXT STEP', 'THEN', 'GO ON',
                     'WHATS NEXT', 'CONTINUE', 'MORE', 'FORWARD', 'TEXT']
    PREV_EXAMPLES = ['PREVIOUS', 'GO BACK', 'GO BACKWARDS', 'GO BACKWARD',
                     'LAST STEP', 'PRIOR', 'PREVIOUS STEP']
    REPEAT_EXAMPLES = ['AGAIN', 'REPEAT', 'SAY AGAIN', 'SAY IT AGAIN',
                       'ONE MORE TIME']
    QUANTITY_EXAMPLES = ['HOW MUCH', 'HOW MANY']


    def __init__(self, instructions = [], ingredients = [], current_step = 0, recipe_name = ''):
        super(Assistant, self).__init__()
        self.title = 'Banana Poppy Seed Pancakes'
        self.instructions = ['Whisk whole wheat flour, all-purpose flour, baking powder, poppy seeds, and salt together in a bowl.',
                             'Beat eggs in a large bowl. Add milk, bananas, coconut oil, honey, and vanilla extract; whisk together. Pour in flour mixture and stir until just combined.',
                             'Preheat a lightly oiled griddle on medium-low heat. Ladle batter 1/4 cup at a time onto the prepared griddle, sprinkling a few blueberries over each pancake. Cook until bubbles start to appear and edges are dry, about 3 minutes. Flip and cook until other side is browned, about 2 minutes.]']
        self.ingredients = ['1 cup whole wheat flour', '1 cup all-purpose flour',
                            '4 teaspoons baking powder', '2 teaspoons poppy seeds',
                            '1 teaspoon salt', '2 eggs', '2 cups milk', '2 ripe bananas, mashed',
                            'quarter cup coconut oil, melted', '2 tablespoons honey',
                            '1 teaspoon vanilla extract', 'half cup fresh blueberries']
        self.current_step = 0


    @staticmethod
    def check_examples(transcript, examples):
        found = False
        for example in examples:
            if lazy_regex_search(example, transcript):
                found = True
                break
        return found


    def process_speech(self, transcript):
        if self.check_examples(transcript, Assistant.START_EXAMPLES):
            self.speak(self.start_cooking())
        elif self.check_examples(transcript, Assistant.NEXT_EXAMPLES):
            self.speak(self.next_step())
        elif self.check_examples(transcript, Assistant.PREV_EXAMPLES):
            self.speak(self.previous_step())
        elif self.check_examples(transcript, Assistant.REPEAT_EXAMPLES):
            self.speak(self.repeat())
        elif self.check_examples(transcript, Assistant.QUANTITY_EXAMPLES):
            self.speak(self.match_ingredients(transcript))
        else:
            self.speak('Sorry, I didn\'t understand.')


    @staticmethod
    def speak(text):
        speaker = gTTS(text = text, lang = 'en', slow = False)
        speaker.save(real_dirname() + '/tmp.mp3')
        os.system('mpg321 -q ' + real_dirname() + '/tmp.mp3')


    def start_cooking(self):
        self.current_step = 0
        text = 'Today we will be cooking ' + self.title + '. '
        # text += 'The ingredients are ' + ', '.join(self.ingredients) + '.'
        text += 'To start, ' + self.instructions[self.current_step]
        return text


    def next_step(self):
        self.current_step += 1
        return self.instructions[self.current_step]


    def previous_step(self):
        self.current_step -= 1
        return self.instructions[self.current_step]


    def repeat(self):
        return self.instructions[self.current_step]


    # @staticmethod
    # def match_ingredients(transcript, ingredients):
    #     for ingredient in ingredients:
    #         if lazy_regex_search(ingredient.name.upper(), transcript): 
    #             return ingredient.quantity
    #     return False


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
    unit_types['fluid ounce']  = ['fluid ounce','fl oz','fluid ounces','fl ozs']
    unit_types['wineglass']    = ['wineglass','wgf','wineglasses','wgfs']
    unit_types['gill']         = ['gill','teacup','gills','teacups']
    unit_types['pottle']       = ['pottle','pot','pottles','pots']
    unit_types['cup']          = ['cup','c','cups']
    unit_types['pint']         = ['pint','p','pt','fl pt','pints','pts','fl pts']
    unit_types['quart']        = ['quart','q','qt','fl qt','quarts','qts','fl qts']
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

    def __init__(self, url = '', title = '', time = '',
                 instructions = [], ingredients = []):
        self.url = url
        if title == '':
            title, time, instructions, ingredients = self.parse()
        self.title = title
        self.time = time
        self.instructions = instructions
        self.ingredients = ingredients


    # def __str__():
    #     temp = self.title + '\n'
    #     temp += 'Time: ' + str(self.time) + '\n'
    #     temp += ' # INSTRUCTIONS # \n'


    @staticmethod
    def removeToken(string, token):
        string = string.replace(token, '')
        return string.strip()


    @staticmethod
    def findParentheticals(string):
        if string.find('(') != -1 and string.find(')') != -1:
            paren = string[string.find('('):string.find(')')+1]
            return paren, Recipe.removeToken(string, paren)
        return (None, string)


    # TODO - change this and transformDigits so we can handle two digit numbers.
    @staticmethod
    def readableFractions(numer, denom):
        intro = 'a' if int(numer) == 1 else str(numer) + ' '
        fraction = ''
        if denom == 2:
            fraction = 'half'
        elif denom == 3:
            fraction = 'third'
        elif denom == 4:
            fraction = 'fourth'
        elif denom == 5:
            fraction = 'fifth'
        elif denom == 6:
            fraction = 'sixth'
        elif denom == 7:
            fraction = 'seventh'
        elif denom == 8:
            fraction = 'eighth'
        elif denom == 9:
            fraction = 'ninth'
        elif denom == 10:
            fraction = 'tenth'
        plural = 's' if int(numer) != 1 else ''
        return intro + fraction + plural


    @staticmethod
    def transformDigits(digits):
        if len(digits) == 3:
            quantity = digits[0] + ' ' + digits[1] + '/' + digits[2]
            readable = digits[0] + ' and ' + Recipe.readableFractions(digits[1], digits[2])
            value = float(digits[0]) + (float(digits[1]) / float(digits[2]))
            return quantity, readable, value
        elif len(digits) == 2:
            quantity = digits[0] + '/' + digits[1]
            readable = Recipe.readableFractions(digits[0], digits[1])
            value = float(digits[0]) / float(digits[1])
            return quantity, readable, value
        elif len(digits) == 1:
            readable = 'a' if int(digits[0]) == 1 else digits[0]
            return digits[0], readable, float(digits[0])
        return None, None, None


    @staticmethod
    def findUnit(quantity, value, string):
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
        unit = words[unit_loc] if unit is None else unit
        if unit in Recipe.abbrevs:
            for real, abbrev in Recipe.unit_types.iteritems():
                if unit in abbrev:
                    unit = Recipe.pluralize(value, real)
            return unit, Recipe.removeToken(Recipe.removeToken(string, unit), quantity)
        return None, Recipe.removeToken(string, quantity)


    @staticmethod
    def pluralize(quantity, string):
        if float(quantity) > 1.0:
            if string == 'foot':
                return 'feet'
            return string + 's'
        return string


    def parse(self):
        scrape = scrape_me(self.url)
        title = scrape.title()
        time = scrape.total_time()
        instructions = [i for i in scrape.instructions().split('\n') if i is not '']
        raw_ingredients = []
        for ingredient in scrape.ingredients():
            paren, ingredient = Recipe.findParentheticals(ingredient)
            quantity, readable, value = Recipe.transformDigits(filter(str.isdigit, ingredient))
            unit, ingredient = Recipe.findUnit(quantity, value, ingredient)
            if unit:
                readable += ' ' + unit + ' ' + ingredient
            else:
                readable += ' ' + ingredient
            if paren:
                readable += ' ' + paren
            raw_ingredients.append([readable, value, unit, ingredient, paren])
        return title, time, instructions, raw_ingredients

def main():
    # assist = Assistant()
    # assist.config_and_start('GORDON')
    url = 'https://www.allrecipes.com/recipe/260895/banana-poppy-seed-pancakes/?internalSource=popular&referringContentType=home%20page&clickId=cardslot%2038'
    scrape = Recipe(url)
    print scrape.title
    print scrape.time
    print scrape.ingredients
    print scrape.instructions


if __name__ == '__main__':
    main()
