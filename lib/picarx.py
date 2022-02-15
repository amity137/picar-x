# from ezblock import Servo,PWM,fileDB,Pin,ADC
from .servo import Servo 
from .pwm import PWM
from .pin import Pin
from .adc import ADC
from .configfile import ConfigFile
import time
import math


class Picarx(object):
    PERIOD = 4095
    PRESCALER = 10
    TIMEOUT = 0.02

    # Wheel base in cm
    L = 9.4

    # Track width of the rear axel in cm
    B = 11.6

    B_by_2L = B * 0.5 / L

    def __init__(self):
        self.dir_servo_pin = Servo(PWM('P2'))
        self.camera_servo_pin1 = Servo(PWM('P0'))
        self.camera_servo_pin2 = Servo(PWM('P1'))

        self.config_file = ConfigFile('/home/pi/picar-x.config')

        self.dir_cal_value = int(self.config_file.get("picarx_dir_servo", default_value=0))
        self.dir_servo_pin.angle(self.dir_cal_value)

        self.cam_cal_value_1 = int(self.config_file.get("picarx_cam1_servo", default_value=0))
        self.cam_cal_value_2 = int(self.config_file.get("picarx_cam2_servo", default_value=0))
        self.camera_servo_pin1.angle(self.cam_cal_value_1)
        self.camera_servo_pin2.angle(self.cam_cal_value_2)

        self.left_rear_pwm_pin = PWM("P13")
        self.right_rear_pwm_pin = PWM("P12")
        self.left_rear_dir_pin = Pin("D4")
        self.right_rear_dir_pin = Pin("D5")

        self.S0 = ADC('A0')
        self.S1 = ADC('A1')
        self.S2 = ADC('A2')

        self.motor_direction_pins = [self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [self.left_rear_pwm_pin, self.right_rear_pwm_pin]
        self.cali_dir_value = self.config_file.get("picarx_dir_motor", default_value="[1,1]")
        self.cali_dir_value = [int(i.strip()) for i in self.cali_dir_value.strip("[]").split(",")]
        self.cali_speed_value = [0, 0]

        self.dir_current_angle = 0
        self.current_speed = 0

        # https://www.researchgate.net/publication/316133453_Wheel_Speed_Control_Algorithm_for_Rear_Wheel_Motor_Driven_Vehicle
        self.use_wheel_speed_control = True
        
        #初始化PWM引脚
        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)



    def set_motor_speed(self, motor, speed):
        # global cali_speed_value,cali_dir_value
        direction = (1 if speed >= 0 else -1) * self.cali_dir_value[motor]
        speed = abs(speed)
        if speed != 0:
            speed = min(speed, 100)
            speed = max(speed, 36)
        speed = speed - self.cali_speed_value[motor]
        if direction < 0:
            self.motor_direction_pins[motor].high()
        else:
            self.motor_direction_pins[motor].low()
        self.motor_speed_pins[motor].pulse_width_percent(speed)

    # TODO: this is broken.
    def motor_speed_calibration(self, value):
        # global cali_speed_value,cali_dir_value
        self.cali_speed_value = value
        if value < 0:
            self.cali_speed_value[0] = 0
            self.cali_speed_value[1] = abs(self.cali_speed_value)
        else:
            self.cali_speed_value[0] = abs(self.cali_speed_value)
            self.cali_speed_value[1] = 0

    # Reverses the direction
    def motor_direction_calibration(self, motor):
        self.cali_dir_value[motor] = -self.cali_dir_value[motor]
        self.config_file.set("picarx_dir_motor", self.cali_dir_value)


    def dir_servo_angle_calibration(self, value):
        # global dir_cal_value
        self.dir_cal_value = value
        print("calibrationdir_cal_value:",self.dir_cal_value)
        self.config_file.set("picarx_dir_servo", "%s"%value)
        self.dir_servo_pin.angle(value)

    def set_dir_servo_angle(self, value):
        if value == self.dir_current_angle:
            return

        abs_value = min(abs(value), 32)
        value = abs_value * (1 if value >= 0 else -1)
        
        self.dir_current_angle = value
        angle_value  = value + self.dir_cal_value
        print("angle_value:", value)
        self.dir_servo_pin.angle(angle_value)

        # Have the correct power scale
        self.forward(self.current_speed)

    def camera_servo1_angle_calibration(self, value):
        # global cam_cal_value_1
        self.cam_cal_value_1 = value
        self.config_file.set("picarx_cam1_servo", "%s"%value)
        print("cam_cal_value_1:",self.cam_cal_value_1)
        self.camera_servo_pin1.angle(value)

    def camera_servo2_angle_calibration(self, value):
        # global cam_cal_value_2
        self.cam_cal_value_2 = value
        self.config_file.set("picarx_cam2_servo", "%s"%value)
        print("picarx_cam2_servo:",self.cam_cal_value_2)
        self.camera_servo_pin2.angle(value)

    def set_camera_servo1_angle(self, value):
        # global cam_cal_value_1
        # TODO: understand this.
        self.camera_servo_pin1.angle(-1*(value + -1*self.cam_cal_value_1))
        # print("self.cam_cal_value_1:",self.cam_cal_value_1)
        print((value + self.cam_cal_value_1))

    def set_camera_servo2_angle(self, value):
        # global cam_cal_value_2
        # TODO: understand this.
        self.camera_servo_pin2.angle(-1*(value + -1*self.cam_cal_value_2))
        # print("self.cam_cal_value_2:",self.cam_cal_value_2)
        print((value + self.cam_cal_value_2))

    def get_adc_value(self):
        adc_value_list = []
        adc_value_list.append(self.S0.read())
        adc_value_list.append(self.S1.read())
        adc_value_list.append(self.S2.read())
        return adc_value_list

    def forward(self, speed):
        speed_scales = self._wheel_speed_control() if self.use_wheel_speed_control else self._wheel_speed_old()

        self.set_motor_speed(0, speed * speed_scales[0])
        self.set_motor_speed(1, -speed * speed_scales[1])

        self.current_speed = speed

    def backward(self, speed):
        self.forward(-speed)

    def stop(self):
        self.forward(0)

    def close(self):
        self.stop()
        self.set_dir_servo_angle(0)
        self.set_camera_servo1_angle(0)
        self.set_camera_servo2_angle(0)

    def _wheel_speed_control(self):
        angle_rad = self.dir_current_angle / 180.0 * math.pi
        factor = self.B_by_2L * math.tan(angle_rad)
        return 1 - factor, 1 + factor

    def _wheel_speed_old(self):
        abs_current_angle_cap = min(abs(self.dir_current_angle), 40)
        power_scale = (100 - abs_current_angle_cap) / 100.0
        print('power_scale:', power_scale)
        if self.dir_current_angle >= 0:
            motor0_scale = power_scale
            motor1_scale = 1
        else:
            motor0_scale = 1
            motor1_scale = power_scale

        return motor0_scale, motor1_scale
    

if __name__ == "__main__":
    px = Picarx()
    px.forward(50)
    time.sleep(1)
    px.stop()
    # set_dir_servo_angle(0)
    # time.sleep(1)
    # self.set_motor_speed(0, 1)
    # self.set_motor_speed(1, 1)
    # camera_servo_pin.angle(0)
# set_camera_servo1_angle(cam_cal_value_1)
# set_camera_servo2_angle(cam_cal_value_2)
# set_dir_servo_angle(dir_cal_value)

# if __name__ == "__main__":
#     try:
#         # dir_servo_angle_calibration(-10) 
#         while 1:
#             test()
#     finally: 
#         stop()