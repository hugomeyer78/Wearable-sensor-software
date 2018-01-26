#####################################################################
#                                                                   #
#                       EMG Module                                  #
#                                                                   #
#                                                                   #                     
#                 Created by: Hugo MEYER                            #
#   Supervisors: Prof. Floreano, Matteo Machini, Anand Bhaskaran    #
#                                                                   #
#####################################################################

import numpy as np
import Data_aquisition
import IMU
#signalMax = 600
#signalMin = 200
#signal = np.array([1, 0])
EMGs = []
nbEMG = 0
shoulder = 1
arm = 2
forearm = 3
hand = 4

""" EMG Sensor class with all its needed characteristics"""
class Sensor:
    
    def __init__(self, signal = 0, signalMin = 0, signalMax = 2000, id = -1, bodyPart=0):
        self.calibMin = 10000.0
        self.calibMax = 0.0
        self.signalMax = float(signalMax)
        self.signalMin = float(signalMin)
        self.signal = float(signal)
        self.id = int(id)
        self.bodyPart = bodyPart
    
    """ Find boundary values during calibration phase"""
    def calibrate(self):
        if self.signal != 0:
            if self.calibMin > self.signal:
                self.calibMin = self.signal
            if self.calibMax < self.signal:
                self.calibMax = self.signal

    """ Update boudary values of EMG analog signal after calibration"""
    def updateBoundaries(self):
        if self.calibMin != 10000.0:
            self.signalMin = self.calibMin
        if self.calibMax != 0.0:
            self.signalMax = self.calibMax
        print(self.calibMin, self.calibMax)
    

    def updateSignal(self):        
        for data in Data_aquisition.allData:
            if data[0] == self.id:
                self.signal = data[1]
            
    """ Return the color associated to a given EMG value"""
    def getColorMuscle(self):
        signalNorm = normalize(self.signalMin, self.signalMax, self.signal)
        R = 1.0

        if signalNorm < (1/3.0):
            G = 1.0
            B = 1.0 - 3.0*signalNorm        
        elif signalNorm < (2/3.0):
            G = -1.5*signalNorm + 1.5
            B = 0         
        elif signalNorm <= 1:
            G = -1.5*signalNorm + 1.5
            B = 0           
        else:
            G=0.0
            B=0.0
        
        return np.array([R,G,B,0.3], dtype = np.float32)
    
    """ Return the size of alimb associated to a given EMG value"""
    def getSizeMuscle(self):
        signalNorm = normalize(self.signalMin, self.signalMax, self.signal)
        
        return 0.04*signalNorm
    
#EMG1 = Sensor(id=4)
#EMG2 = Sensor()



def updateSensors():
    for EMG in EMGs:
        EMG.updateSignal()
        
def calibration():
    for EMG in EMGs:
        EMG.calibrate()


"""Create a Sensor class"""
def createInstance():
    global nbEMG
    
    nbEMG += 1
    new_id = 10+nbEMG
    EMGs.append(Sensor(id=new_id, bodyPart=nbEMG+1))
    Data_aquisition.createBuffer('EMG')


"""Return color and size of the limb according to the limb and EMG value"""
def getArmSizeAndColor(bodyPart):
    color = np.array([1.,1.,1.,0.3], dtype = np.float32)
    
    if bodyPart == arm:
        size = 0.06
    else:
        size = 0.04
    
    for EMG in EMGs:
        if EMG.bodyPart == bodyPart:
            color = EMG.getColorMuscle()
            if bodyPart == arm:
                size = EMG.getSizeMuscle() + 0.06
            else:
                size = EMG.getSizeMuscle()*0.7 + 0.04
   
    return color, size

        
    
def normalize(min, max, val):    
    return (val-min)/(float(max) - float(min))