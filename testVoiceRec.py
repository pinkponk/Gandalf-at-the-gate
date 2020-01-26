#python3 -m pip install --user SpeechRecognition

import speech_recognition as sr

r = sr.Recognizer()

mic = sr.Microphone()

print(sr.Microphone.list_microphone_names())

with mic as source:
    print("Adjusting..")
    r.adjust_for_ambient_noise(source)
    print("Adjusting done!")
    print("Say something!")
    audio = r.listen(source)
    audio_byte = audio.get_wav_data()
    
    with open("testWav.wav","wb") as file:
        file.write(audio_byte)
        
    #print("You said="+answer)
print("DONE")


def analyseAnswer(audio):
    
    try:
        answer = r.recognize_google(audio)
        return answer, True
    except sr.RequestError:
        print("API unavailable")
        return None, False
    except sr.UnknownValueError:
        print("Unable to recognize speech")
        return None, False
    

def listenForAnswer(source):
    try:
        audio = r.listen(source, timeout=10, phrase_time_limit=3)
        return audio, True
    except sr.WaitTimeoutError:
        print("You took to long")
        return None, False


#wav_file = sr.AudioFile("harvard.wav")
#with wav_file as source:
#    audio = r.record(source)
#    print("Made Audio")
#    print(audio)
    
#    print(r.recognize_google(audio))
#    #print(r.recognize_sphinx(audio))
#    print("DONE")