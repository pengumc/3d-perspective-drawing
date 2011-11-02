#! /usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import rotation
import xml.etree.ElementTree as ElementTree

class Screen(gtk.DrawingArea):


    __gsignals__ = { "expose-event": "override" }

    def do_expose_event(self, event):
        cr = self.window.cairo_create()
        cr.rectangle(event.area.x, event.area.y,
            event.area.width, event.area.height)
        cr.clip()
        self.draw(cr, *self.window.get_size())

    def draw(self, cr, width, height):
        #clear
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        if self.points is None:
            return()
        
        #loop through points
        midx = width/2
        midy = height/2
        cr.set_source_rgb(0,0,0)
        cr.set_font_size(22)
        transformed = dict()
        #first transform all points to the view plane
        for point in self.points:
            p = self.transform_to_2d(point)
            cr.rectangle(midx + p.x -3, midy + p.y -3, 6, 6)
            cr.stroke()
            cr.move_to(midx + p.x-5, midy+p.y-10)
            cr.set_source_rgb(1,0,0)
            cr.show_text(point.name)
            transformed[point.name] = p
            cr.set_source_rgb(0,0,0)
        #now connect the points
        for key in transformed:
            p = transformed[key]
            if p.connected is None:
                continue
            connected = p.connected.split(',')
            for c in connected:
                p2 = transformed[c]
                cr.move_to(midx + p.x, midy+ p.y)
                cr.line_to(midx + p2.x, midy + p2.y)
                cr.stroke()


    def loadPoints(self, filename):
        tree = ElementTree.parse(filename)
        p = tree.getroot().findall("point")
        scale = float(tree.find("scale").text)
        self.points = []
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
            new_point = Point(x, y, z, name, connected)
            self.points.append(new_point)
            #TODO add camera to points.xml
            
    def set_camera(self, x, y, z):
        if not hasattr(self, "camera"):
            self.camera = Point(x, y, z, "camera", None)
        else:
            self.camera.x = x
            self.camera.y = y
            self.camera.z = z
        print("camera set to [{:.1f}, {:.1f}, {:.1f}]".format(
            self.camera.x, self.camera.y, self.camera.z))

    def transform_to_2d(self, point):
        #transform with perspective
        #remember y => -y for drawing purposes
        x = point.x
        y = point.y
        z = point.z
        #let's keep the camera x=0, y=0 to make matters easy
        dydz = (y - self.camera.y) / (z - self.camera.z)
        y = self.camera.y + dydz * -self.camera.z
        dxdz = (x - self.camera.x) / (z - self.camera.z)
        x = self.camera.x + dxdz * -self.camera.z
        return(Point(x ,y, 0.0,
             "2d " + point.name, point.connected))        
             
    def set_timer(self, interval):
        gobject.timeout_add(interval, self.rotate)

    def rotate(self):
        #rotate all points
        angles = rotation.Vector(0.02, 0.1, 0.01)
        R = rotation.Matrix()
        R.create_from_angles(angles)
        new_points = []
        for point in self.points:
            rotated = R.dot_product(point)
            new_points.append(Point(rotated.x, rotated.y, rotated.z,
                point.name, point.connected))
        self.points = new_points
        cr = self.window.cairo_create()
        self.draw(cr, 300,300)
        return(True)
        

class Point(rotation.Vector):


    def __init__(self, x, y, z, name, connected):
        rotation.Vector.__init__(self, x, y, z, name)
        self.connected = connected
        
        


def run(Widget):
    window = gtk.Window()
    window.connect("delete-event", gtk.main_quit)
    widget = Widget()
    widget.set_size_request(300,300)
    widget.show()
    widget.loadPoints("./points.xml")
    widget.set_camera(0,0, 500)
    widget.set_timer(50)
    window.add(widget)
    window.present()
    
    gtk.main()

if __name__ == "__main__":
    print("## z axis points out of screen ##")
    run(Screen)

