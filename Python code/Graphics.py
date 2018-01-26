#####################################################################
#                                                                   #
#                       Graphics Module                             #
#                                                                   #
#                                                                   #                     
#                 Created by: Johann HENES                          #
#   Supervisors: Prof. Floreano, Matteo Machini, Anand Bhaskaran    #
#                                                                   #
#####################################################################

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import math
import time
import numpy as np

import Definitions
import Shaders



vertexPositions = []
indexPositions = []
nbIndex = []
styleIndex = []

vboCube = 0
vboPyramide = 1
vboDashed = 2
vboHexagon = 3
vboSphere = 4
vboCylindre = 5
vboCircle = 6
vboCone = 7
vboEdges = 0
vboSurfaces = 1
def VBO_cube():
    """ Create the "cube" VBO & EBO """
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    vertices = np.array([[-0.5,-0.5,-0.5],  [0.5,-0.5,-0.5],    [0.5,0.5,-0.5],     [-0.5,0.5,-0.5],    \
                         [-0.5,-0.5,0.5],   [0.5,-0.5,0.5],     [0.5,0.5,0.5],      [-0.5,0.5,0.5]],    dtype='f')

    edgeIndices = np.array([[0,1,   1,2,    2,3,    3,0,    \
                             0,4,   1,5,    2,6,    3,7,    \
                             4,5,   5,6,    6,7,    7,4,    ]], dtype=np.int32)
    surfIndices = np.array([[0,1,2,3,    \
                             0,4,5,1,    \
                             1,5,6,2,    \
                             2,6,7,3,    \
                             3,7,4,0,    \
                             7,6,5,4,    ]], dtype=np.int32)

    vertexPositions = vertexPositions + [vbo.VBO(vertices),]
    
    indexPositions = indexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]
    
    nbIndex = nbIndex + [[edgeIndices.size, surfIndices.size],]
    
    styleIndex = styleIndex + [[GL_LINES, GL_QUADS],]

def VBO_pyramide():
    """ Create the "pyramide" VBO & EBO """
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    vertices = np.array([[-0.5,0,0],    [0.5,0,0.5],   [0.5,0.25*math.sqrt(3),-0.25],    [0.5,-0.25*math.sqrt(3),-0.25]],    dtype='f')

    edgeIndices = np.array([[0,1,   0,2,    0,3,    1,2,    2,3,    3,1]], dtype=np.int32)

    surfIndices = np.array([[0,1,2,   0,2,3,    0,3,1,    1,2,3]], dtype=np.int32)

    vertexPositions = vertexPositions + [vbo.VBO(vertices),]
    
    indexPositions = indexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]
    
    nbIndex = nbIndex + [[edgeIndices.size, surfIndices.size],]
    
    styleIndex = styleIndex + [[GL_LINES, GL_TRIANGLES],]

def VBO_cone(iMax = 8):
    """ Create the "pyramide" VBO & EBO """
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex
    
    vertices = []
    edgeIndices = []
    surfIndices = []

    i = 0
    while i <= iMax:
        phi = 2*math.pi*i/float(iMax)
        vertices = vertices + [-0.5, 0.5*math.cos(phi), 0.5*math.sin(phi)]
        if i != iMax:
            edgeIndices = edgeIndices + [i, i+1]
            edgeIndices = edgeIndices + [i, (iMax+1)]
            surfIndices = surfIndices + [i, i+1, (iMax+1)]
        i +=1
    vertices = vertices + [0.5, 0., 0.]


    vertices = np.array([vertices],    dtype='f')

    edgeIndices = np.array([edgeIndices], dtype=np.int32)

    surfIndices = np.array([surfIndices], dtype=np.int32)

    vertexPositions = vertexPositions + [vbo.VBO(vertices),]
    
    indexPositions = indexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]
    
    nbIndex = nbIndex + [[edgeIndices.size, surfIndices.size],]
    
    styleIndex = styleIndex + [[GL_LINES, GL_TRIANGLES],]

def VBO_dashed():
    """ Create the "dashed" VBO & EBO """
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    vertices = np.array([[-5/10.,0,0],    [-3/10.,0,0],   [-1/10.,0,0],    [1/10.,0,0],    [3/10.,0,0],    [5/10.,0,0]],    dtype='f')

    edgeIndices = np.array([[0,1,   2,3,    4,5]], dtype=np.int32)

    surfIndices = np.array([[0,1,   2,3,    4,5]], dtype=np.int32)

    vertexPositions = vertexPositions + [vbo.VBO(vertices),]
    
    indexPositions = indexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]
    
    nbIndex = nbIndex + [[edgeIndices.size, surfIndices.size],]
    
    styleIndex = styleIndex + [[GL_LINES, GL_LINES],]
    
def VBO_hexagon():
    """ Create the "hexagon" VBO & EBO """
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    vertices = np.array([[-0.5,-0.5,0],    [-0.5,-0.25,0.25*math.sqrt(3)],   [-0.5,0.25,0.25*math.sqrt(3)],    [-0.5,0.5,0],    [-0.5,0.25,-0.25*math.sqrt(3)],   [-0.5,-0.25,-0.25*math.sqrt(3)],    \
                         [0.5,-0.5,0],     [0.5,-0.25,0.25*math.sqrt(3)],    [0.5,0.25,0.25*math.sqrt(3)],     [0.5,0.5,0],     [0.5,0.25,-0.25*math.sqrt(3)],    [0.5,-0.25,-0.25*math.sqrt(3)]],    dtype='f')

    edgeIndices = np.array([[0,1,   1,2,    2,3,    3,4,    4,5,    5,0,    \
                             6,7,   7,8,    8,9,    9,10,   10,11,  11,6,   \
                             0,6,   1,7,    2,8,    3,9,    4,10,   5,11]], dtype=np.int32)

    surfIndices = np.array([[0,1,2,3,   3,4,5,0,    \
                             6,7,8,9,   9,10,11,6,  \
                             0,6,7,1,   1,7,8,2,   2,8,9,3,   3,9,10,4,   4,10,11,5,   5,11,6,0]], dtype=np.int32)

    vertexPositions = vertexPositions + [vbo.VBO(vertices),]
    
    indexPositions = indexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]
    
    nbIndex = nbIndex + [[edgeIndices.size, surfIndices.size],]
    
    styleIndex = styleIndex + [[GL_LINES, GL_QUADS],]

def VBO_sphere(iMax = 8, jMax = 8, iMin = 8, jMin = 8):
    """ Create the "sphere" VBO & EBO """
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    vertices = []
    edgeIndices = []
    surfIndices = []
    
    
    i = 0
    while i <= iMin:
        phi = math.pi*i/float(iMax)
        j = 0
        while j < jMin:
            theta = 2*math.pi*j/float(jMax)
            vertices = vertices + [0.5*math.cos(phi), 0.5*math.sin(phi)*math.cos(theta), 0.5*math.sin(phi)*math.sin(theta)]
            if i != iMin:
                edgeIndices = edgeIndices + [i*jMin + j, i*jMin + (j+1)%jMin]
                edgeIndices = edgeIndices + [i*jMin + j, (i+1)*jMin + j]
                surfIndices = surfIndices + [i*jMin + j, i*jMin + (j+1)%jMin, (i+1)*jMin + (j+1)%jMin]
                surfIndices = surfIndices + [(i+1)*jMin + (j+1)%jMin, (i+1)*jMin + j, i*jMin + j]
            j +=1
        i +=1


    vertices = np.array([vertices],    dtype='f')

    edgeIndices = np.array([edgeIndices], dtype=np.int32)

    surfIndices = np.array([surfIndices], dtype=np.int32)

    vertexPositions = vertexPositions + [vbo.VBO(vertices),]
    
    indexPositions = indexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]
    
    nbIndex = nbIndex + [[edgeIndices.size, surfIndices.size],]
    
    styleIndex = styleIndex + [[GL_LINES, GL_TRIANGLES],]

def VBO_cylindre(iMax = 8):
    """ Create the "sphere" VBO & EBO """
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    vertices = []
    edgeIndices = []
    surfIndices = []
    
    
    i = 0
    while i <= iMax:
        phi = 2*math.pi*i/float(iMax)
        vertices = vertices + [-0.5, 0.5*math.cos(phi), 0.5*math.sin(phi)]
        vertices = vertices + [0.5, 0.5*math.cos(phi), 0.5*math.sin(phi)]
        if i != iMax:
            edgeIndices = edgeIndices + [2*i, 2*i+1]
            edgeIndices = edgeIndices + [2*i, 2*(i+1)]
            edgeIndices = edgeIndices + [2*i+1, 2*(i+1)+1]
            surfIndices = surfIndices + [2*i, 2*(i+1), 2*(i+1)+1]
            surfIndices = surfIndices + [2*(i+1)+1, 2*i+1, 2*i]
            surfIndices = surfIndices + [2*i, 2*(i+1), 2*(iMax+1)]
            surfIndices = surfIndices + [2*i+1, 2*(i+1)+1, 2*(iMax+1)+1]
        i +=1
    vertices = vertices + [-0.5, 0., 0.]
    vertices = vertices + [0.5, 0., 0.]


    vertices = np.array([vertices],    dtype='f')

    edgeIndices = np.array([edgeIndices], dtype=np.int32)

    surfIndices = np.array([surfIndices], dtype=np.int32)

    vertexPositions = vertexPositions + [vbo.VBO(vertices),]
    
    indexPositions = indexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]
    
    nbIndex = nbIndex + [[edgeIndices.size, surfIndices.size],]
    
    styleIndex = styleIndex + [[GL_LINES, GL_TRIANGLES],]

def VBO_circle(iMax = 8):
    """ Create the "sphere" VBO & EBO """
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    vertices = []
    edgeIndices = []
    surfIndices = []
    
    
    i = 0
    while i <= iMax:
        phi = 2*math.pi*i/float(iMax)
        vertices = vertices + [-0.5, 0.5*math.cos(phi), 0.5*math.sin(phi)]
        if i != iMax:
            edgeIndices = edgeIndices + [i, i+1]
            surfIndices = surfIndices + [i, i+1, (iMax+1)]
        i +=1
    vertices = vertices + [-0.5, 0., 0.]


    vertices = np.array([vertices],    dtype='f')

    edgeIndices = np.array([edgeIndices], dtype=np.int32)

    surfIndices = np.array([surfIndices], dtype=np.int32)

    vertexPositions = vertexPositions + [vbo.VBO(vertices),]
    
    indexPositions = indexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]
    
    nbIndex = nbIndex + [[edgeIndices.size, surfIndices.size],]
    
    styleIndex = styleIndex + [[GL_LINES, GL_TRIANGLES],]

SaturationVertexPositions = []
SaturationIndexPositions = []
SaturationNbIndex = []
SaturationStyleIndex = []
SaturationModelMatrix = []
def VBO_hypar(saturation = (0, 0, 0, 0, 0, 0)):
    """ Create the "sphere" VBO & EBO """
    global SaturationVertexPositions
    global SaturationIndexPositions
    global SaturationNbIndex
    global SaturationStyleIndex


    vertices = []
    edgeIndices = []
    surfIndices = []
    
    Cy = 0.5*(saturation[2]+saturation[3])
    Cz = 0.5*(saturation[4]+saturation[5])
    Ey = 0.5*(saturation[2]-saturation[3])
    Ez = 0.5*(saturation[4]-saturation[5])
    
    i = 0
    iMax = 360
    while i <= iMax:
        swingAngle = math.pi/180.*i
        if Ey != 0 and Ez != 0:
            k = 1./math.sqrt(Ez*Ez*math.cos(swingAngle)*math.cos(swingAngle) + Ey*Ey*math.sin(swingAngle)*math.sin(swingAngle))
            theta = k*Ey*Ez*math.sin(swingAngle)
            phi = k*Ey*Ez*math.cos(swingAngle)
        elif Ey != 0:
            phi = -Ey + 2*Ey*i/360.
            theta = 0
        elif Ez != 0:
            phi = 0
            theta = -Ez + 2*Ez*i/360.
        else:
            phi = 0
            theta = 0
        theta *= math.pi/180.
        phi *= math.pi/180.
        x = 0.5*math.cos(phi)*math.cos(theta)
        y = 0.5*math.cos(phi)*math.sin(theta)
        z = 0.5*math.sin(phi)
        vertices = vertices + [x, y, z]
        if i != iMax:
            edgeIndices = edgeIndices + [i, i+1]
            surfIndices = surfIndices + [i, i+1, (iMax+1)]
        i +=1

    vertices = vertices + [0., 0., 0.]

    vertices = np.array([vertices],    dtype='f')

    edgeIndices = np.array([edgeIndices], dtype=np.int32)

    surfIndices = np.array([surfIndices], dtype=np.int32)

    SaturationVertexPositions = SaturationVertexPositions + [vbo.VBO(vertices),]

    SaturationIndexPositions = SaturationIndexPositions + [[vbo.VBO(edgeIndices, target=GL_ELEMENT_ARRAY_BUFFER), vbo.VBO(surfIndices, target=GL_ELEMENT_ARRAY_BUFFER)],]

    SaturationNbIndex = SaturationNbIndex + [[edgeIndices.size, surfIndices.size],]

    SaturationStyleIndex = SaturationStyleIndex + [[GL_LINES, GL_TRIANGLES],]

def VBO_init():
    global vertexPositions
    global indexPositions
    global nbIndex
    global styleIndex

    """ init VBO & EBO buffers """
    VBO_init = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_init)

    EBO_init = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO_init)

    """ Create VBOs"""
    n = -1
    n+=1 ; VBO_cube()
    n+=1 ; VBO_pyramide()
    n+=1 ; VBO_dashed()
    n+=1 ; VBO_hexagon()
    n+=1 ; VBO_sphere(16, 16, 16, 16)
    n+=1 ; VBO_cylindre(16)
    n+=1 ; VBO_circle(16)
    n+=1 ; VBO_cone(16)

    while n > 0:
        n -= 1
        Definitions.packagePreprocess = Definitions.packagePreprocess + [[]]

opaque = 0
blending = 1
wireframe = 2
idBuffer = 3
def modelView(style = 0):
    if style == 0 or style == 3:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
    elif style == 1:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
    elif style == 2:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)


#def bindTexture(textureData, width, height):
#    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
#                 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
#
#    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
#    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
#    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
#    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
#
#
#def loadTexture(texture = 'Textures/awesomeface.png'):
#    textureSurface = pygame.image.load(texture)
#    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
#    width = textureSurface.get_width()
#    height = textureSurface.get_height()
#
#    glEnable(GL_TEXTURE_2D)
#    texid = glGenTextures(1)
#
#    glBindTexture(GL_TEXTURE_2D, texid)
#
#    return [textureData, width, height]
