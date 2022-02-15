from setup import lib
from lib.pwm import PWM
from lib.servo import Servo


if __name__ == '__main__':
    P_11 = Servo(PWM('P11'))         
    P_11.angle(0)     

