from gtts import gTTS
import os

#tts = gTTS(text="Good morning", lang="en")


from tts_watson.TtsWatson import TtsWatson

userName = "b7b26cf2-cbd4-4694-80e7-647125f44891"
password = "qkvnNARYpgc1"
ttsWatson = TtsWatson(userName,password,"en-AllisonVoice")
text = 'Hello world'
ttsWatson.play(text)