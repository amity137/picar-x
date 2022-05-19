from .adc import ADC

class Grayscale_Module(object):
    def __init__(self):
        self.chn_0 = ADC("A0")
        self.chn_1 = ADC("A1")
        self.chn_2 = ADC("A2")

    def read(self):
        return (self.chn_0.read(), self.chn_1.read(), self.chn_2.read())