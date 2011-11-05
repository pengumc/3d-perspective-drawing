#vectors, matrices and rotations
import math

class Vector:


    def __init__(self, x, y, z, name=""):
        self.x = x
        self.y = y
        self.z = z
        self.name = name

    def get_length(self):
        return(math.sqrt(
            math.pow(self.x, 2)+
            math.pow(self.y, 2)+
            math.pow(self.z, 2)))

    def add_vector(self, vector):
        self.x = self.x + vector.x
        self.y = self.y + vector.y
        self.z = self.z + vector.z

    def substract_vector(self, vector):
        self.x = self.x - vector.x
        self.y = self.y - vector.y
        self.z = self.z - vector.z
        
    def copy_from(self, vector):
        self.x = vector.x
        self.y = vector.y
        self.z = vector.z

    def display(self):
        print("vector {0}: [{1:.3f}, {2:.3f}, {3:.3f}]".format(
            self.name, self.x, self.y, self.z))



class Matrix:

    
    def __init__(self, name=""):
        self.array = [0 for i in range(0,9)]
        self.inverse = [0 for i in range(0,9)]
        self.name = name
        self.base_angles = Vector(0,0,0,"base")

    def update_with_angles(self, v):
        self.base_angles.add_vector(v)
        self.create_from_angles(self.base_angles)

    def create_from_angles(self, v):
        self.base_angles.copy_from(v)
        ctheta = math.cos(v.x)
        cpsi = math.cos(v.y)
        cphi = math.cos(v.z)
        stheta = math.sin(v.x)
        spsi = math.sin(v.y)
        sphi = math.sin(v.z)
        self.array[0] = cphi * cpsi
        self.array[1] = -cpsi * sphi
        self.array[2] = -spsi
        self.array[3] = ctheta * sphi - cphi * stheta * spsi
        self.array[4] = ctheta * cphi + stheta * sphi * spsi
        self.array[5] = -cpsi * stheta
        self.array[6] = stheta * sphi + ctheta * cphi * spsi
        self.array[7] = cphi * stheta - ctheta * sphi * spsi
        self.array[8] = ctheta * cpsi
        self._generate_inverse()

    def display(self):
        print(("matrix {}:\n[{:+.3f}, {:+.3f}, {:+.3f}]\n" + 
            "[{:+.3f}, {:+.3f}, {:+.3f}]\n" + 
            "[{:+.3f}, {:+.3f}, {:+.3f}]").format(self.name,
                self.array[0], self.array[1], self.array[2],
                self.array[3], self.array[4], self.array[5],
                self.array[6], self.array[7], self.array[8]))

    def _generate_inverse(self):
        A = (self.array[4] * self.array[8] -
            self.array[5]*self.array[7])
        B = (self.array[5] * self.array[6] -
            self.array[3]*self.array[8])
        C = (self.array[3] * self.array[7] -
            self.array[4]*self.array[6])
        D = (self.array[2] * self.array[7] -
            self.array[1]*self.array[8])
        E = (self.array[0] * self.array[8] -
            self.array[2]*self.array[6])
        F = (self.array[6] * self.array[1] -
            self.array[0]*self.array[7])
        G = (self.array[1] * self.array[5] -
            self.array[2]*self.array[4])
        H = (self.array[2] * self.array[3] -
            self.array[0]*self.array[5])
        I = (self.array[0] * self.array[4] -
            self.array[1]*self.array[3])
        det_reciproke = 1.0 / (self.array[0] * A + self.array[1] * B 
            + self.array[2] * C)
        self.inverse[0] = A * det_reciproke
        self.inverse[1] = D * det_reciproke
        self.inverse[2] = G * det_reciproke
        self.inverse[3] = B * det_reciproke
        self.inverse[4] = E * det_reciproke
        self.inverse[5] = H * det_reciproke
        self.inverse[6] = C * det_reciproke
        self.inverse[7] = F * det_reciproke
        self.inverse[8] = I * det_reciproke
        

    def invert(self):
        temp = self.array
        self.array = self.inverse
        self.inverse = temp

    def dot_product(self, v):
        x = (self.array[0] * v.x + self.array[1] * v.y + self.array[2] * v.z)
        y = (self.array[3] * v.x + self.array[4] * v.y + self.array[5] * v.z)
        z = (self.array[6] * v.x + self.array[7] * v.y + self.array[8] * v.z)
        return(Vector(x, y, z, v.name + " * " + self.name))

    def dot_product_inverse(self, v):
        x = (self.inverse[0] * v.x + self.inverse[1] * v.y 
            + self.inverse[2] * v.z)
        y = (self.inverse[3] * v.x + self.inverse[4] * v.y 
            + self.inverse[5] * v.z)
        z = (self.inverse[6] * v.x + self.inverse[7] * v.y 
            + self.inverse[8] * v.z)
        return(Vector(x, y, z, v.name + " * " + self.name))
    
