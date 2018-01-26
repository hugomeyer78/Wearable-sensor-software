# -*- coding: utf-8 -*-
"""
Created on Mon Dec 04 14:24:32 2017

@author: Hugo
"""

import Data_aquisition
import rotating_cube


Data_aquisition.initSerial(port='COM5', bdrate=115200)
Data_aquisition.initBuffers()
Data_aquisition.initPoller()

IMU = rotating_cube.Simulation()

while 1:
    q1, q2 = Data_aquisition.getQuater()
    IMU.run()
    if q2[0] != 0:
       IMU.update_angles(q2[1:])
       print(q2[1:])
       
Data_aquisition.exit_prg()
