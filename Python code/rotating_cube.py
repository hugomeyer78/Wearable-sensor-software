"""
 Simulation of a rotating 3D Cube
 Developed by Leonel Machava <leonelmachava@gmail.com>

 http://codeNtronix.com
"""
import pygame
from operator import itemgetter
from pyquaternion import Quaternion
import numpy as np


class Point3D:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x, self.y, self.z = float(x), float(y), float(z)
 
    def project(self, win_width, win_height, fov, viewer_distance):
        """ Transforms this 3D point to 2D using a perspective projection. """
        factor = fov / (viewer_distance + self.z)
        x = self.x * factor + win_width / 2
        y = -self.y * factor + win_height / 2
        return Point3D(x, y, self.z)

    def rotateQuater(self, q):
        correction1 = Quaternion(w=1, x=1, y=0, z=0)
        correction2 = Quaternion(w=1, x=0, y=1, z=0)# w=0 -> no drift anticipate, w=1 anticipate
        new_pt = q.rotate(np.array([self.x, self.y, self.z]))
        new_pt = correction1.rotate(np.array(new_pt))
        new_pt = correction2.rotate(np.array(new_pt))
        return Point3D(new_pt[0], new_pt[1], new_pt[2])

class Simulation:
    def __init__(self, win_width = 640, win_height = 480):
        pygame.init()

        self.screen = pygame.display.set_mode((win_width, win_height))
        pygame.display.set_caption("Simulation of a rotating 3D Cube")
        
        self.clock = pygame.time.Clock()

        self.vertices = [
            Point3D(-1,1,-0.5),
            Point3D(1,1,-0.5),
            Point3D(1,-1,-0.5),
            Point3D(-1,-1,-0.5),
            Point3D(-1,1,0.5),
            Point3D(1,1,0.5),
            Point3D(1,-1,0.5),
            Point3D(-1,-1,0.5)
            ]
     
        # Define the vertices that compose each of the 6 faces. These numbers are
        # indices to the vertices list defined above.
        self.faces  = [(0,1,2,3),(1,5,6,2),(5,4,7,6),(4,0,3,7),(0,4,5,1),(3,2,6,7)]

        # Define colors for each face
        self.colors = [(255,0,255),(255,0,0),(0,255,0),(0,0,255),(0,255,255),(255,255,0)]

        self.quaternion = Quaternion()
        
    def update_angles(self, q):
        self.quaternion = Quaternion(w=q[0], x=q[1], y=q[2], z=q[3])  
        

        
    def run(self):
        """ Main Loop """
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    #sys.exit()
        except SystemExit:
            pygame.quit()
            
        self.clock.tick(50)
        self.screen.fill((0,32,0))

        # It will hold transformed vertices.
        t = []
        
        for v in self.vertices:
            # Rotate the point with quaternion.
            r = v.rotateQuater(self.quaternion)
            # Transform the point from 3D to 2D
            p = r.project(self.screen.get_width(), self.screen.get_height(), 256, 4)
            # Put the point in the list of transformed vertices
            t.append(p)

        # Calculate the average Z values of each face.
        avg_z = []
        i = 0
        for f in self.faces:
            z = (t[f[0]].z + t[f[1]].z + t[f[2]].z + t[f[3]].z) / 4.0
            avg_z.append([i,z])
            i = i + 1

        # Draw the faces using the Painter's algorithm:
        # Distant faces are drawn before the closer ones.
        for tmp in sorted(avg_z,key=itemgetter(1),reverse=True):
            face_index = tmp[0]
            f = self.faces[face_index]
            pointlist = [(t[f[0]].x, t[f[0]].y), (t[f[1]].x, t[f[1]].y),
                         (t[f[1]].x, t[f[1]].y), (t[f[2]].x, t[f[2]].y),
                         (t[f[2]].x, t[f[2]].y), (t[f[3]].x, t[f[3]].y),
                         (t[f[3]].x, t[f[3]].y), (t[f[0]].x, t[f[0]].y)]
           
            #return self.colors[face_index], pointlist
            pygame.draw.polygon(self.screen,self.colors[face_index],pointlist)
            pygame.display.flip()
            

#if __name__ == "__main__":
    #cube = Simulation()
    
   # while 1:
   #     cube.run()
    #    cube.update_angles(0, 1, 0)