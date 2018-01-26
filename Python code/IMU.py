#####################################################################
#                                                                   #
#                       IMU Module                                  #
#                                                                   #
#                                                                   #                     
#                 Created by: Hugo MEYER                            #
#   Supervisors: Prof. Floreano, Matteo Machini, Anand Bhaskaran    #
#                                                                   #
#####################################################################

import numpy as np
from pyquaternion import Quaternion
import Data_aquisition
from math import fabs
#import Model



IMUs = []
nbIMU = 0
shoulder = 1
arm = 2
forearm = 3
hand = 4
BNO055 = 1
MPU6050 = 2

""" IMU Sensor class with all its needed characteristics"""
class Sensor:
    def __init__(self, quater=[1, 0, 0, 0], id=-1, bodyPart=0, model=0):
        self.bodyPart = bodyPart
        self.prevQuater = Quaternion([1, 0, 0, 0])
        self.quater = quater
        self.id = int(id)
        self.state = 'NotActive'
        self.model = model
        self.correc_shift = Quaternion([1, 0, 0, 0])
        self.correc_frame = Quaternion([1, 0, 0, 0])
    
    """ Update the quaternion of the IMU classby getting it from the circular buffer """
    def updateQuater(self, endInit): 
        new_quater = [1,0,0,0]
        IMUActive = False        
        for data in Data_aquisition.allData:
            if self.id == data[0]:
                new_quater = Quaternion(data[1:].tolist())
                self.state = 'Active'
                IMUActive = True  
                
        if IMUActive == False:
            self.state = 'NotActive'
                
        if np.any(new_quater)==False or self.state == 'NotActive':
            new_quater = [1,0,0,0]
        else:
            new_quater = Quaternion(new_quater)#self.filter_shift(Quaternion(new_quater), endInit) ##
            
        self.quater = new_quater
        
        self.prevQuater = self.quater
        

    """ 
        Bring all the limbs to the intial comfiguration (w=1, x=0, y=0, z=0)at the end of the calibration
        This allows to remove any shift or drift of the IMUs durinfg this phase
    """
    def get_correct(self):
        
        if self.state == 'Active':
            init_q = Quaternion(w=1, x=0, y=0, z=0) 
                    
            if self.model == BNO055:
                self.correc_shift = init_q /self.quater
                #self.correc_frame = Quaternion(w=1, x=0, y=0, z=0) 
            elif self.model == MPU6050:
                self.correc_shift = init_q /self.quater
               # self.correc_frame = Quaternion(w=1, x=1, y=0, z=0) 
        
        
    """ Remove discontinuous behavior of the sensors """ 
    def filter_shift(self, new_q, endInit):
        remove_shift = False
        for new_comp, comp in zip(new_q, self.prevQuater):
            if fabs(new_comp - comp) > 0.5:
                remove_shift = True
                
        if remove_shift and endInit == False:
            #print('shift removed')
            return self.prevQuater
        else:
            #print(self.prevQuater, new_q)
            return new_q
        
        

        
    """ 
        Apply the correction calculated during the calibration phase
        Specific to the sensor type and the body limb
    """
    def apply_correct(self):
    
        if self.state == 'Active':
            correc_shift_q = Quaternion(self.correc_shift)
            correc_frame_q = Quaternion(self.correc_frame)
            
            if self.model == BNO055:
                self.quater = self.quater*correc_shift_q
                #self.quater = Quaternion(w=self.quater[0], x=-self.quater[1], y=-self.quater[3], z=-self.quater[2])
                self.quater = Quaternion(w=self.quater[0], x=-self.quater[2], y=-self.quater[3], z=self.quater[1])
                #self.quater = self.quater*correc_frame_q
                
            elif self.model == MPU6050:            
                #self.quater = self.quater*correc_frame_q
                pass
            
            if self.bodyPart == forearm:
                arm_quater = [imu.quater for imu in IMUs if imu.bodyPart == arm][0]
                arm_model = [imu.model for imu in IMUs if imu.bodyPart == arm][0]
                
                if arm_model == BNO055 and self.model == MPU6050:
                    arm_quater = FromBNOtoMPU(arm_quater)
                    
                self.quater = self.quater/arm_quater
                
            elif self.bodyPart == hand:
                forearm_quater = [imu.quater for imu in IMUs if imu.bodyPart == forearm][0]
                forearm_model = [imu.model for imu in IMUs if imu.bodyPart == forearm][0]
                
                if forearm_model == BNO055 and self.model == MPU6050:
                    forearm_quater = FromBNOtoMPU(forearm_quater)
                    
                self.quater = self.quater/forearm_quater
            
            
""" adjustment to go from BNO's frame to MPU's one """ 
def FromBNOtoMPU(q):
    return Quaternion(q[0], q[1], q[3], -q[2])

def updateSensors(endInit):
    for IMU in IMUs:
        IMU.updateQuater(endInit)
    

""" Create IMU class """
def createInstance():
    global nbIMU
    
    nbIMU += 1
    #new_id = nbIMU
    new_id = nbIMU
    if nbIMU < 3:
        IMUs.append(Sensor(id=new_id, bodyPart=nbIMU+1, model=BNO055))
    else:
        IMUs.append(Sensor(id=new_id, bodyPart=nbIMU+1, model=MPU6050))
    Data_aquisition.createBuffer('IMU')
