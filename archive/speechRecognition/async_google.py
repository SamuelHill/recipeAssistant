from google.cloud import speech

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "speechRecognition/googleAuth2.json"

client = speech.SpeechClient()

operation = client.long_running_recognize(
	audio=speech.types.RecognitionAudio(
		uri='gs://my-bucket/recording.flac',
	),
	config=speech.types.RecognitionConfig(
		encoding='LINEAR16',
		language_code='en-US',
		sample_rate_hertz=44100,
	),
)

op_result = operation.result()
for result in op_result.results:
	for alternative in result.alternatives:
		print('=' * 20)
		print(alternative.transcript)
		print(alternative.confidence)