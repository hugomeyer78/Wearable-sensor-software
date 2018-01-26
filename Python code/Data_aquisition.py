#####################################################################
#                                                                   #
#                  Data_acquisition Module                          #
#                                                                   #
#                                                                   #                     
#                 Created by: Hugo MEYER                            #
#   Supervisors: Prof. Floreano, Matteo Machini, Anand Bhaskaran    #
#                                                                   #
#####################################################################


# example that displays a rolling graph of random numbers
import rolling_buffer
import polling_acquisition
import time
import numpy as np
import serial
import re
import sys
import pygame
import EMG
import IMU
import threading as th
#import time

s = 0
BufferEMG = []
BufferIMU = []
Poller1 = 0
allData = []
port = 'COM5'   # On mac : '/dev/cu.usbmodem1421'
baudrate = 115200
idEMGStreamed = []
idIMUStreamed = []
dataCheckTimer = 0
#t = 0



""" Initilize serial object to read the port """
def initSerial():
    global s
    global baudrate
    global port
    s = serial.Serial(port, baudrate)
    
    
    
""" Read the port, convert binary data to quaternion array (IMU) or single 
    float value (EMG) and convert label to int value
"""
def pollerReadData( ):
    global s
    global t

   # lock up the port reading 
   # self._lock.acquire()
    
    try:
        sensor_data = s.readline().decode("utf-8")
    except:
        print('ERROR: FAILED READING PORT')
        
    # Unlock the port reading 
    #self._lock.release()
            
    r = re.compile("([a-zA-Z]+)([0-9]+)")
    sensor_data = re.split('\t+', sensor_data)
    
    m = r.match(sensor_data[0])
    
    sensorType = m.group(1).decode('ascii')
    sensorID = m.group(2)
    
    if sensorType == 'EMG':
        sensor_data[0] = 10+float(sensorID)
    elif sensorType == 'IMU':
        sensor_data[0] = float(sensorID)
    
    sensor_data = [float(i) for i in sensor_data]
    sensor_data = np.asarray(sensor_data)
    
    dataStreamCheck(int(sensorID), sensorType)
    
    if sensor_data[0] == 1:
       print(sensor_data)
       pass

    if sensor_data[0] == 2:
       #print(sensor_data)
       pass
   
    if sensor_data[0] == 3:
       #print('coucou')
       pass
   
    if sensor_data[0] == 11:
        #print(sensor_data)
        pass

    #print(IMU_data[0])
    
    return sensor_data


""" Check if a sensor has been disconnected or reconnected 
    If yes -> remove acquisition system related to the sensor
"""
def dataStreamCheck(id, sensorType):
    global idEMGStreamed
    global idIMUStreamed 
    global dataCheckTimer
    global BufferIMU
    global BufferEMG
    
    if sensorType == 'IMU':
        if id not in idIMUStreamed:
            idIMUStreamed.append(id)
    if sensorType == 'EMG':
        if id not in idEMGStreamed:
            idEMGStreamed.append(id)
    
    if dataCheckTimer == 20:
        dataCheckTimer = 0
    
        if len(idIMUStreamed) != len(BufferIMU):
            UpdateBuffers(idIMUStreamed, idEMGStreamed, len(BufferIMU), len(idIMUStreamed))
        if len(idEMGStreamed) != len(BufferEMG):
            UpdateBuffers(idIMUStreamed, idEMGStreamed, nbEMGBuffer=len(BufferEMG), nbEMGData=len(idEMGStreamed))
        idIMUStreamed = []
        idEMGStreamed = [] 
            
    
    dataCheckTimer += 1
        
    
""" Manage creation or deletion of the buffers if an IMU is disconnected or reconnected 
    Could be extended to the EMGs
"""
def UpdateBuffers (id_IMUStreamed, id_EMGStreamed, nbIMUBuffer=-1, nbIMUData=-1, nbEMGBuffer=-1, nbEMGData=-1):
    global BufferIMU
    global BufferEMG
    
    if nbIMUBuffer != -1:
        if nbIMUBuffer > nbIMUData:
            missing_ids = []
            for imu in IMU.IMUs:
                if imu.id not in id_IMUStreamed:
                    missing_ids.append(imu.id)
            for id in missing_ids:
                IMU.IMUs[id-1].state = 'NotActive'
                del BufferIMU[id-1]
        if nbIMUBuffer < nbIMUData:
            for imu in IMU.IMUs:
                if imu.state == 'NotActive' and imu.id in id_IMUStreamed: 
                    imu.state = 'Active'
                    BufferIMU.insert(imu.id-1, rolling_buffer.RollingBuffer())
                    BufferIMU[imu.id-1].reset( length=1000, dimensions=(5) )
                
        print('Number of IMU streamed data changed: nbBuffer: {}   nbData: {}   Missing IDs: {}   idstreamed: {}' .format(nbIMUBuffer, nbIMUData, missing_ids, id_IMUStreamed))


""" define the "write" function to inject the queued data into the buffer """
def pollerWriteBuffer( packet ):
    global BufferIMU
    global BufferEMG
    
    
    id = int(packet[0])
        
    
    if id < 11:   
        index = id-1
        if index < len(BufferIMU):
            BufferIMU[id-1].add_new( time.time(), packet )
    elif id < 21:
        index = id-11
        if index < len(BufferEMG):
            BufferEMG[id-11].add_new( time.time(), packet )
    


""" polling data acquisition to grab the data """
def initPoller():
    global Poller1
    global Poller2
    
    Poller1 = polling_acquisition.PollingAquisition()
    Poller1.setup( size = 100 )
    #Poller1.read = pollerReadData
    Poller1.write = pollerWriteBuffer
    Poller1.start()     # start "acquiring data"
    
   
    
""" Create a Buffer which size depends on data nature: IMU or EMG """
def createBuffer(sensor):
    global BufferIMU
    global BufferEMG
    
    if sensor == 'IMU':
        BufferIMU.append(rolling_buffer.RollingBuffer())
        BufferIMU[-1].reset( length=1000, dimensions=(5) )
    elif sensor == 'EMG':
        BufferEMG.append(rolling_buffer.RollingBuffer())
        BufferEMG[-1].reset( length=1000, dimensions=(2) )
    

""" Function which transmit data to the main loop of the program for further visualisation """
def getData():
    global allData
    global BufferIMU
    global BufferEMG
    
    allData = []
    
    for buffer in BufferIMU:
        ts_last_val, data_last_val = buffer.get_latest()
        allData.append(data_last_val)
        
    for buffer in BufferEMG:
        ts_last_val, data_last_val = buffer.get_latest()
        allData.append(data_last_val)


def exit_aquisition():
    Poller1.stop()
    s.close()
