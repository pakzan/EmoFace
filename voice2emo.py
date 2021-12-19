# OpenVokaWavMean-win64.py
# public-domain sample code by Vokaturi, 2018-02-20
#
# A sample script that uses the VokaturiPlus library to extract the emotions from
# a wav file on disk. The file has to contain a mono recording.
#
# Call syntax:
#   python3 OpenVokaWavMean-win64.py path_to_sound_file.wav
#
# For the sound file hello.wav that comes with OpenVokaturi, the result should be:
#	Neutral: 0.760
#	Happy: 0.000
#	Sad: 0.238
#	Angry: 0.001
#	Fear: 0.000

import pyaudio
import numpy as np
from constant import EMPTY_VOICE_PROB
from vokaturi.api import Vokaturi

Vokaturi.load("Vokaturi/lib/Vokaturi_win64.dll")

chunksize = 100000  # fixed chunk size
sample_rate = 44100

# initialize portaudio
p = pyaudio.PyAudio()

device_info = p.get_default_input_device_info()
#device_info = p.get_device_info_by_index(1)
channelcount = device_info["maxInputChannels"] if (
    device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]
stream = p.open(format=pyaudio.paInt16,
                channels=channelcount,
                rate=int(device_info["defaultSampleRate"]),
                input=True,
                frames_per_buffer=chunksize,
                input_device_index=device_info["index"])

#stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=CHUNKSIZE)

def pred_voice():
    # get fresh samples
    data = stream.read(chunksize)
    samples = np.fromstring(data, dtype=np.int16)

    buffer_length = len(samples)
    c_buffer = Vokaturi.SampleArrayC(buffer_length)
    if samples.ndim == 1:  # mono
        c_buffer[:] = samples[:] / 32768.0
    else:  # stereo
        c_buffer[:] = 0.5*(samples[:,0]+samples[:,1]) / 32768.0

    # initialise voice with sample rate and size
    voice = Vokaturi.Voice(sample_rate, buffer_length)
    # assign current recorded voice into voice var
    voice.fill(buffer_length, c_buffer)
    quality = Vokaturi.Quality()
    emoProb = Vokaturi.EmotionProbabilities()
    # get probabilities
    voice.extract(quality, emoProb)

    # destroy voice before return value
    voice.destroy()
    if quality.valid:
        return (emoProb.neutrality, emoProb.happiness, emoProb.sadness, emoProb.anger, emoProb.fear)
    else:
        return EMPTY_VOICE_PROB
