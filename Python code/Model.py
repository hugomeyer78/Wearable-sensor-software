#####################################################################
#                                                                   #
#                       Main Module                                 #
#                                                                   #
#          To exit press "esc" key of your keyboard                 #
#                                                                   #                     
#          Created by: Johann HENES & Hugo MEYER                    #
#   Supervisors: Prof. Floreano, Matteo Machini, Anand Bhaskaran    #
#                                                                   #
#####################################################################

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders

from OpenGL.arrays import vbo
from OpenGL.raw.GL.ARB.vertex_array_object import glGenVertexArrays, \
                                                  glBindVertexArray
from ctypes import *
import numpy as np

import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

import math
import random
import time

import Cursor
import Definitions
import Events
import Graphics
import Saturations
import Sensors
import Shaders
import State
import StickMan
import Data_aquisition
import EMG
import IMU
from timeit import default_timer as timer
import sys
#import menuWindow


CALIB_TIME = 20
NB_IMU = 3
NB_EMG = 1

def refreshId():
    id = 0
    for i in range(0, len(Sensors.virtuSens)):
        Sensors.virtuSens[i].id = id
        id += 1
    for i in range(0, len(Sensors.zoiSens)):
        Sensors.zoiSens[i].id = id
        id += 1
        #TODO : do it with body & GUI as well, cange ID buffer also ?

def main():
    State.loadQuater()
    """ Create list of models """
    State.createList()
    State.updateTemplateList()
    """ Create Entities """
    StickMan.virtuMan = StickMan.characteristics(1.7, (0,0,0), StickMan.parts)
    State.loadModel(StickMan.virtuMan)
    Saturations.preprocessSaturations(StickMan.virtuMan)
    
    
    State.loadSensors()

    """ Create a window """
    pygame.init()
    
    screen = pygame.display.set_mode(Events.display, pygame.DOUBLEBUF|pygame.OPENGL|pygame.OPENGLBLIT|RESIZABLE|NOFRAME)
    glClearColor(0.0, 0.0, 0.0, 0.0);
    
    """ texture for ID buffer """
    # create texture
    plane_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, plane_texture)
    # texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    # texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, Events.display[0], Events.display[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
    glBindTexture(GL_TEXTURE_2D, 0)


    """ render buffer for depth for ID buffer """
    # create render buffer
    rbo = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rbo)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, Events.display[0], Events.display[1])
    glBindRenderbuffer(GL_RENDERBUFFER, 0)
    

    """ frame buffer object as ID buffer """
    # create frame buffer
    FBO = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, FBO)
    # attach texture to frame buffer
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, plane_texture, 0)
    # attach render buffer to frame buffer
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, rbo)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    """ Generate the VBOs """
    Graphics.VBO_init()
    

    """ Create the shaders """
    Shaders.shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(Shaders.vertex_shader,GL_VERTEX_SHADER),
                                                      OpenGL.GL.shaders.compileShader(Shaders.fragment_shader,GL_FRAGMENT_SHADER))
    glUseProgram(Shaders.shader)


    """ Enable position attrib ? """
    position = glGetAttribLocation(Shaders.shader, "position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, None) 
    glEnableVertexAttribArray(position)


    """ Initialize some more stuff"""
    glEnable(GL_TEXTURE_2D)
    glDepthFunc(GL_LEQUAL)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    

    """ Shader var. locations """
    Shaders.proj_loc = glGetUniformLocation(Shaders.shader, "projection")
    Shaders.view_loc = glGetUniformLocation(Shaders.shader, "view")
    Shaders.model_loc = glGetUniformLocation(Shaders.shader, "model")
    Shaders.setColor_loc = glGetUniformLocation(Shaders.shader, "setColor")
    
    Definitions.projectionMatrix.perspectiveProjection(90, 0.5*Events.display[0]/Events.display[1], 0.1, 100.0)
    glUniformMatrix4fv(Shaders.proj_loc, 1, GL_FALSE, Definitions.projectionMatrix.peek())
    glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, Definitions.modelMatrix.peek())
    


    """ Initialize UI Window """
    #menuWindow.init_window()
    
        
    
    """ Create Sensors Instances"""
    for imu in range(0, NB_IMU):
        IMU.createInstance()
        
    for emg in range(0, NB_EMG):
        EMG.createInstance()
    
    
    """ Initialize Data aquisition """
    Data_aquisition.initSerial()
    #Data_aquisition.initBuffers()
    Data_aquisition.initPoller()
    start_calib = True
    end_init = True
    t_start_init = 10000
    
    
    
    

    """ >>> main loop <<< """
    glViewport(0, 0, Events.display[0], Events.display[1])
    while True:
        # keep track of loop frequency
        flagStart = time.clock()

        """
            Events management.
            Most interactions between the user and the software is aknowledged here.
        """
        Events.manage()
        
        refreshId() # TODO : only when adding/removing sensors
        
        
        """ Aquire Data from serial port and update values"""        
        Data_aquisition.getData()
                     
        IMU.updateSensors(end_init)
        EMG.updateSensors()


        """ Initiate calibration phase"""  
        if start_calib==True:
            t_start_init = timer()
            start_calib = False
            print("START CALIBRATION")
            
        t_init = timer() - t_start_init
        
        """ Calibrate EMG during calibration phase"""  
        if t_init < CALIB_TIME:
            EMG.calibration()
            
        """ Terminate calibration phase and set-up EMG data"""  
        if t_init>=CALIB_TIME and end_init==True:
            print("END CALIBRATION")
            for imu in IMU.IMUs:
                imu.get_correct()
                
            for emg in EMG.EMGs:
                emg.updateBoundaries()
                
            end_init=False
            

        """ Correct coordinate frame and kinematics"""  
        for imu in IMU.IMUs:
            imu.apply_correct()  

        """ Apply quaternions to the virtual limbs""" 
        armData = [imu.quater for imu in IMU.IMUs if imu.bodyPart == IMU.arm]
        if armData:
            Qarm = Definitions.vector4D([imu.quater for imu in IMU.IMUs if imu.bodyPart == IMU.arm][0])#[1,1,0,0]
            StickMan.virtuMan.parts[StickMan.ARM][StickMan.Data_angle] = [Qarm.o,Qarm.x,Qarm.y,Qarm.z]
         
        forearmData = [imu.quater for imu in IMU.IMUs if imu.bodyPart == IMU.forearm]
        if forearmData:
            Qforearm = Definitions.vector4D([imu.quater for imu in IMU.IMUs if imu.bodyPart == IMU.forearm][0])#[1,0,0,0]
            StickMan.virtuMan.parts[StickMan.FOREARM][StickMan.Data_angle] = [Qforearm.o,Qforearm.x,Qforearm.y,Qforearm.z]
        #
        
        handData = [imu.quater for imu in IMU.IMUs if imu.bodyPart == IMU.hand]
        if handData:        
            Qhand = Definitions.vector4D([imu.quater for imu in IMU.IMUs if imu.bodyPart == IMU.hand][0])
            StickMan.virtuMan.parts[StickMan.HAND][StickMan.Data_angle] = [Qhand.o,Qhand.x,Qhand.y,Qhand.z]
        
        

        """
            Preprocess entities.
            Store all needed transformations to significantly lower calculation cost when rendering (redundancy otherwise between display buffer, ID buffer and bindings)
        """
        Definitions.modelMatrix.translate(-StickMan.lookingAt[0][0],-StickMan.lookingAt[0][1],-StickMan.lookingAt[0][2])
        StickMan.part = -1 # initialize the recursivity here
        Sensors.countID = 0
        Graphics.SaturationModelMatrix = []
        StickMan.stick(StickMan.virtuMan, (StickMan.virtuMan.x, StickMan.virtuMan.y, StickMan.virtuMan.z))

        i = 0
        for package in Definitions.packagePreprocess:
            j = 0
            for pack in package:
                if pack[Definitions.packParent] == "Ground":
                    Definitions.packageIndices[0] = Definitions.packageIndices[0] + [[i, j],]
                elif pack[Definitions.packParent] == "Body":
                    Definitions.packageIndices[1] = Definitions.packageIndices[1] + [[i, j],]
                elif pack[Definitions.packParent] == "Sensor":
                    Definitions.packageIndices[2] = Definitions.packageIndices[2] + [[i, j],]
                elif pack[Definitions.packParent] == "Link":
                    Definitions.packageIndices[3] = Definitions.packageIndices[3] + [[i, j],]
                j += 1
            i += 1


        """ 
            Draw on the ID buffer.
            The ID BUFFER is used for the mouse implementation, to know which body/sensor/gui part is targeted with the cursor.
        """
        # bind the ID buffer
        glBindFramebuffer(GL_FRAMEBUFFER, FBO)
        
        # clear the ID buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # fill ID buffer
        Graphics.modelView(Graphics.opaque)
        StickMan.drawBodySurface(Graphics.idBuffer)
        Sensors.drawSensor(Graphics.idBuffer)
        


        """
            Mouse interaction with ID buffer.
            Read the value of the ID buffer at mouse position, do some stuff.
        """
        Cursor.mouseManage()
        

        """
            Draw on the display buffer.
            The display buffer is what the user will see on his screen.
        """
        # bind the display buffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
        # clear the display buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        
        #draw saturation balls
        Graphics.modelView(Graphics.blending)
        Saturations.drawSaturationBalls()
        
        # draw body
        Graphics.modelView(Events.style)
        StickMan.drawBodySurface(Events.style)
        StickMan.drawBodyEdge(Events.style)
        
        #draw saturation balls
        Graphics.modelView(Graphics.opaque)
        Saturations.drawSaturationLines()

        # draw sensors
        Graphics.modelView(Graphics.opaque)
        Sensors.drawSensor(Events.style)
        Sensors.drawDashed(Events.style)

        if Events.style != Graphics.idBuffer:
            """ load matrix in shader """
            I = np.array([[1, 0, 0, 0],
                          [0, 1, 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]])
            Definitions.modelMatrix.push()
            Definitions.modelMatrix.set(I)
            Definitions.modelMatrix.translate(0,-0.5,0)
            Definitions.modelMatrix.scale(1,0,1)
            
            glUniformMatrix4fv(Shaders.model_loc, 1, GL_FALSE, Definitions.modelMatrix.peek())

            """ choose vbo """
            vboId = 0
            vboDraw = Graphics.vboEdges
            """ bind surfaces vbo """
            Graphics.indexPositions[vboId][vboDraw].bind()
            Graphics.vertexPositions[vboId].bind()
            glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
            """ send color to shader """
            r,g,b,a = [255, 255, 255, 255]
            color = np.array([r/255.,g/255.,b/255.,a/255.], dtype = np.float32)
            glUniform4fv(Shaders.setColor_loc, 1, color)
            Definitions.modelMatrix.pop()
            
            """ draw vbo """
            glDrawElements(Graphics.styleIndex[vboId][vboDraw], Graphics.nbIndex[vboId][vboDraw], GL_UNSIGNED_INT, None)
        

        # update screen
        pygame.display.flip()
        

        """
            empty preprocess package
        """
        i = len(Definitions.packagePreprocess)
        while i > 0:
            i -= 1
            while len(Definitions.packagePreprocess[i]) > 0:
                Definitions.packagePreprocess[i] = Definitions.packagePreprocess[i][:-1]
        i = len(Definitions.packageIndices)
        while i > 0:
            i -= 1
            while len(Definitions.packageIndices[i]) > 0:
                Definitions.packageIndices[i] = Definitions.packageIndices[i][:-1]


        pygame.time.wait(15)


        


main()