from setup import lib

from lib.picarx import Picarx
from lib.ultrasonic import Ultrasonic

if __name__ == "__main__":
    try:
        sonar = Ultrasonic()
        px = Picarx()

        px.forward(30)
        while True:
            distance = sonar.read()
            print("distance: ",distance)
            if distance > 0 and distance < 10:
                px.forward(0)
                break
    finally:
        px.forward(0)


