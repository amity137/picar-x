import sys
sys.path.append(r'/home/pi/git/picar-x/lib')
from utils import reset_mcu
reset_mcu()

from picarx import Picarx
from picamera import PiCamera

import time
import os.path

camera = PiCamera()
camera.resolution = (1024, 768)
camera.start_preview()
time.sleep(2)

# Capture images at different camera angles
px = Picarx()
for angle in range(0, -45, -5):
    px.set_camera_servo2_angle(angle)
    camera.capture(os.path.join('camera_media', 'camera_angle_' + str(angle) + '.jpg'))
    time.sleep(.5)

# Capture video while moving
px.set_camera_servo2_angle(0)
camera.resolution = (640, 480)
camera.start_recording(os.path.join('camera_media', 'car_moving.h264'))
time.sleep(0.5)

px.forward(50)
time.sleep(2)
px.set_dir_servo_angle(32)
time.sleep(2)
px.set_dir_servo_angle(-32)
time.sleep(2)

camera.stop_recording()

px.close()
camera.close()