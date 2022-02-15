from setup import lib
from lib.tts import TTS

import time


if __name__ == "__main__":
    words = ["Hello", "Hi", "Good bye", "Nice to meet you"]
    tts_robot = TTS()
    #tts_robot.lang("de-DE")
    tts_robot.espeak_params(amp=199)

    for i in words:
        print(i)
        tts_robot.say(i)
        time.sleep(1)
