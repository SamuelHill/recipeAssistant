import speech_recognition as sr
import pyttsx3

# Setup recognizer for obtaining audio from the microphone and
# pyttsx3 engine for the resulting speech
r = sr.Recognizer()
engine = pyttsx3.init()

with sr.Microphone() as source:
    print("Please wait. Calibrating microphone...")
    r.adjust_for_ambient_noise(source, duration=5)
    print("Ready!")

    while True:
        audio = r.listen(source)
        try:
            print(u"\U0001F442" + " '" + r.recognize_sphinx(audio) + "'")
            engine.say('Generic response')
            engine.runAndWait()
        except sr.UnknownValueError:
            print("Not sure what you said...")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))