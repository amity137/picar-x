from setup import lib
from lib.grayscale_module import Grayscale_Module
from lib.picarx import Picarx

import time


if __name__=='__main__':
    gm = Grayscale_Module()
    while True:
        print(gm.read())
        time.sleep(1)

    px = Picarx()
    