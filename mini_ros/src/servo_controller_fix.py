#!/usr/bin/env python3

"""
servo_controller_fix.py
====
본 파일은 이전 배포판에서 사용한 ServoKit 라이브러리를 PCA9685 라이브러리로 교체한 파일입니다.
PCA9685 라이브러리는 example/test_servos_*.py에서 사용된 것과 동일합니다.
PWM제어에 필요한 min_pulse, max_pulse, frequency를 직접 수정할 수 있으며,
이전 배포판보다 정확하게 서보모터 각도를 제어할 수 있습니다.
"""
import sys
sys.path.append("..")

# import Kinematics.kinematics as kn
import numpy as np

from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
import board
import busio
import time
# from adafruit_extended_bus import ExtendedI2C as I2C

class Controllers:
    def __init__(self):

        print("Initializing Servos")
        self._i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1))
        # self._i2c_bus0= I2C(2)
        print("skanning,",self._i2c_bus0.scan())


        print("Initializing ServoKit")
        self._pca_1 = PCA9685(self._i2c_bus0, address=0x40)
        self._pca_1.frequency = 60
        self._pca_2 = PCA9685(self._i2c_bus0, address=0x41)
        self._pca_2.frequency = 60

        self._servos = list()
        for i in range(0, 12):
            if i<6:
                self._servos.append(servo.Servo(self._pca_1.channels[i], min_pulse=500, max_pulse=2440))
            else:
                a = i%6
                print("a is", a)
                self._servos.append(servo.Servo(self._pca_2.channels[a], min_pulse=500, max_pulse=2440))

        print("Done initializing")

        # [0]~[2] : 왼쪽 앞 다리 // [3]~[5] : 오른쪽 앞 다리 // [6]~[8] : 왼쪽 뒷 다리 // [9]~[11] : 오른쪽 뒷 다리
        # centered position perpendicular to the ground
        # self._servo_offsets = [180, 90, 90, 1, 90, 90,
        #             180, 90, 90, 1, 90, 90]
        # offset James:
        # self._servo_offsets = [180+2, 90-16, 90+7, 1+12, 90+45, 90+9,
        #             180-13, 90-33, 90+6, 1+11, 90+49, 90+13]
        # Offset Jake:
        # self._servo_offsets = [180+2-10, 90-16-13, 90+7, 1+12+23, 90+45+5, 90+9,
        #         180-13-13, 90-33-12, 90+6, 1+11+9, 90+49+9, 90+13]    
        # self._servo_offsets = [180+2-10, 90-16-13-7, 90+7-2, 1+12+23, 90+45+5+7, 90+9+2,\
        #     180-13-13+3, 90-33-12+3, 90+6+2, 1+11+9-3, 90+49+9-3, 90+13-2] 

        # before right hind leg broke:
        # self._servo_offsets = [180+2-10, 90-16-13-7, 90+7-2, 1+12+23, 90+45+5+7, 90+9+2,\
        #             180-13-13+3, 90-33-12+3, 90+6+2-9, 1+11+9-3, 90+49+9-3, 90+13-2-16] 
        
 #       self._servo_offsets = [180+2-10, 90-16-13-7, 90+7-2, 1+12+23, 90+45+5+7, 90+9+2,\
#            180-13-13+3, 90-33-12+3, 90+6+2-9, 1+11+9-3, 90+49+9-3-15, 90+13-2-16+15] 


        # tue 30 aug: found it like this
        # self._servo_offsets = [180+2-10-8, 90-16-13-7, 90+7-2, 1+12+23+8, 90+45+5+7, 90+9+2,\
        #     180-13-13+3, 90-33-12+3+5+10, 90+6+2-9, 1+11+9-3, 90+49+9-3-23, 90+13-2-16+15] 

        # after recalibrating: take 1    
 #       self._servo_offsets = [180+2-10-2, 90-16-13-7+10-2, 90+7-2+7, 1+12+23-3, 90+45+5+7-10+3+3, 90+9+2+6,\
#            180-13-13+3, 90-33-12+3+5-10+6, 90+6+2-9+3, 1+11+9-3, 90+49+9-3-15-4, 90+13-2-16+15+2] 

        # self._servo_offsets = [180+2-10-8, 90-16-13-7, 90+7-2, 1+12+23+8, 90+45+5+7, 90+9+2,\
        #     180-13-13+3, 90-33-12+3+5+10, 90+6+2-9, 1+11+9-3, 90+49+9-3-23, 90+13-2-16+15] 

        # removed redundent old changes, from standing.py to steady.py
#        self._servo_offsets = [170, 62-7, 102-2, 33, 143+7, 107+2, \
 #               157+3, 49+3, 92+2, 18-3, 126-3, 102-2]

        # best as found on 3 okt. first did similar to simulation, but then changed a lot to improve front hind legs weight 
        #self._servo_offsets = [170+1+2+4-7, 62-7-3+3+4, 102-2-4, 33-2-4+7, 143+7+5-4+3, 107+2, \
         #           157+3+2, 49+3-6+10, 92+2, 18-3-3, 126-3+11-10, 102-2]
        self._servo_offsets = [170, 59, 96, 34-4, 154-7, 109, \
            162, 56, 94, 12, 124, 100]
 

        self._val_list = [ x for x in range(len(self._servos)) ]

        # All Angles for Leg 3 * 4 = 12 length
        self._thetas = []
        self.reset_offset = False
        # self.stand_val = [97, 98, 95, 111, 103, 101, 82, 92, 98, 93, 101, 101]
        self.stand_val = [97, 91, 93, 111, 110, 103, \
                            85, 95, 91, 90, 98, 83]

    def getDegreeAngles(self, La, rads):
        # radian to degree
        if rads == True:
            La *= 180/np.pi
        La = [ [ int(x) for x in y ] for y in La ]

        self._thetas = La

    # Angle mapping from radian to servo angles
    def angleToServo(self, La, rads= False):
        # print("")
        self.getDegreeAngles(La, rads=rads)
        # print("thetas",self._thetas)
        #FL Lower
        self._val_list[0] = self._servo_offsets[0] - self._thetas[0][2]
        #FL Upper
        self._val_list[1] = self._servo_offsets[1] - self._thetas[0][1]    
        #FL Shoulder
        self._val_list[2] = self._servo_offsets[2] + self._thetas[0][0]

        #FR Lower
        self._val_list[3] = self._servo_offsets[3] + self._thetas[1][2]
        #FR Upper
        self._val_list[4] = self._servo_offsets[4] + self._thetas[1][1]    
        #FR Shoulder
        self._val_list[5] = self._servo_offsets[5] + self._thetas[1][0]

        #BL Lower
        self._val_list[6] = self._servo_offsets[6] - self._thetas[2][2]
        #BL Upper
        self._val_list[7] = self._servo_offsets[7] - self._thetas[2][1]    
        #BL Shoulder, Formula flipped from the front
        self._val_list[8] = self._servo_offsets[8] + self._thetas[2][0]
        # print("just check: this is 8:", self._val_list[8])
        #BR Lower. 
        self._val_list[9] = self._servo_offsets[9] + self._thetas[3][2]
        #BR Upper
        self._val_list[10] = self._servo_offsets[10] + self._thetas[3][1]    
        #BR Shoulder, Formula flipped from the front
        self._val_list[11] = self._servo_offsets[11] + self._thetas[3][0]     

    def getServoAngles(self):
        return self._val_list

    def servoRotate(self, thetas, rads=False):
        # print("rotate thetas:", thetas)
        self.angleToServo(thetas, rads)
        # if self.reset_offset:
        #     offset_diff = np.array(self.stand_val) - np.array(self._val_list)
        #     newoffset = np.array(self._servo_offsets) + offset_diff
        #     print("offset was:", self._servo_offsets, "offset is:", newoffset)
            
        #     self._servo_offsets = newoffset.tolist()
        #     self.reset_offset = False
        #     # quit()
        #     self.servoRotate(thetas, rads)
        # print("vals:", self._val_list)
        # if self.start ==True:
        #     newoffset = 
        i = 0
        # print(self._val_list)
        for x in range(len(self._val_list)):
            # print("item:", i)
            i+=1
            if (self._val_list[x] > 180):
                print("Over 180!!")
                self._val_list[x] = 179
            if (self._val_list[x] <= 0):
                print("Under 0!!")
                self._val_list[x] = 1
            # a = 
            self._servos[x].angle = float(self._val_list[x])


# if __name__=="__main__":
#     legEndpoints=np.array([[100,-100,87.5,1],[100,-100,-87.5,1],[-100,-100,87.5,1],[-100,-100,-87.5,1]])
#     thetas = kn.initIK(legEndpoints) #radians
    
#     controller = Controllers()

#     # Get radian thetas, transform to integer servo angles
#     # then, rotate servos
#     controller.servoRotate(thetas)

#     # Get AngleValues for Debugging
#     svAngle = controller.getServoAngles()
#     print(svAngle)

#     # #plot at the end
#     kn.plotKinematics()
