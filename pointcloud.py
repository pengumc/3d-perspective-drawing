import rotation
import math
import xml.etree.ElementTree as ElementTree

class PointCloud:
    
    
    def __init__(self, filename):
        self.points = []
        self.scale = 0
        self.camera = rotation.Vector(0,0,500,"camera")
        self.plane = rotation.Vector(0,0,0,"viewplane")
        start_angles = rotation.Vector(0.0, 0.0, 0.0)
        self.R = rotation.Matrix("R")
        self.R.create_from_angles(start_angles)
        self.transformed = dict()
        self.load_from_file(filename)
        
    def load_from_file(self, filename):
        tree = ElementTree.parse(filename)
        p = tree.getroot().findall("point")
        scale = float(tree.find("scale").text)
        self.scale = scale
        for point in p:
            #mandatory elements
            x = float(point.find("x").text)*scale
            y = float(point.find("y").text)*scale
            z = float(point.find("z").text)*scale
            #optional
            name = point.find("name")
            if name is not None:
                name = name.text
            else:
                name = ""
            connected = point.find("connected")
            if connected is not None:
                connected = connected.text
            else:
                connected = ""
            color = point.find("color")
            if color is not None:
                color = color.text.split(',')
                for i in range(len(color)):
                    color[i] = float(color[i])
            else:
                color = None
            new_point = Point(x, y, z, name, connected, color)
            self.points.append(new_point)
        self.transformed = self.get_transformed_point_dict()

    def set_camera(self, x, y, z):
        self.camera.x = x
        self.camera.y = y
        self.camera.z = z
        print("camera set to [{:.1f}, {:.1f}, {:.1f}]".format(
            self.camera.x, self.camera.y, self.camera.z))
        self.transformed = self.get_transformed_point_dict()            
        
    def zoom(self, zoom_in=True):
        if zoom_in:
            self.plane.z = self.plane.z + self.scale
        else:
            self.plane.z = self.plane.z - self.scale        
        self.transformed = self.get_transformed_point_dict()
    
    #return a the point transformed to the 2d viewplane    
    def transform_to_2d(self, point, rotate=True):
        #transform with perspective
        name = point.name
        color = point.color
        if hasattr(point, "connected"):
            connected = point.connected
        else:
            connected = ""
        if rotate:
            point = self.R.dot_product(point)
        x = point.x
        y = point.y
        z = point.z
        #let's keep the viewplane parallel with the z axis
        #it's makes things easier
        dz = z - self.camera.z
        if dz == 0: dz = 0.001
        dydz = (y - self.camera.y) / (dz)
        y = self.camera.y + dydz * -(self.camera.z - self.plane.z)
        dxdz = (x - self.camera.x) / (dz)
        x = self.camera.x + dxdz * -(self.camera.z - self.plane.z)
        return(Point(x ,y, 0.0,
             "2d " + name, connected, color))        
    
    #return a dict with pairs: point.name = transformed point
    def get_transformed_point_dict(self, pointlist=None):
        transformed = dict()
        if pointlist == None: pointlist = self.points
        for point in pointlist:
            p = self.transform_to_2d(point)
            transformed[point.name] = p
        return(transformed)

    #change the 3d rotation of the point cloud by x y z
    def rotate(self, x, y, z):
        self.R.update_with_angles(rotation.Vector(x,y,z))
        self.transformed = self.get_transformed_point_dict()        
        return(True)

    #return rotation to 0
    def reset_rotation(self):
        self.R.create_from_angles(rotation.Vector(0,0,0))
        self.transformed = self.get_transformed_point_dict()        
    
    #set rotation to x y z
    def rotate_abs(self, x, y, z):
        self.R.create_from_angles(rotation.Vector(x,y,z))
        self.transformed = self.get_transformed_point_dict()        
        return(True)


class Point(rotation.Vector):


    def __init__(self, x, y, z, name="", connected=None, color=None):
        rotation.Vector.__init__(self, x, y, z, name)
        self.connected = connected
        if color:
            self.color = color
        else:
            self.color = [0,0,0]


