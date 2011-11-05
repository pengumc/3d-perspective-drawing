#! /usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import rotation
import math
import xml.etree.ElementTree as ElementTree

def dummy(x):
    return(x)


class Screen(gtk.DrawingArea):


    __gsignals__ = { "expose-event": "override" }

    def do_expose_event(self, event):
        cr = self.window.cairo_create()
        cr.rectangle(event.area.x, event.area.y,
            event.area.width, event.area.height)
        cr.clip()
        self.draw(cr, *self.window.get_size())

    def do_zoom(self, widget, event, data=None):
        if event.direction == gtk.gdk.SCROLL_UP:
            #zoom in
            self.plane.z = self.plane.z + self.scale
        else:
            #zoom out       
            self.plane.z = self.plane.z - self.scale
        cr = self.window.cairo_create()            
        self.draw(cr, 300,300)
            
    def __init__(self):
        gtk.DrawingArea.__init__(self);
        self.scale = 0
        self.points = []
        self.camera = Point(0, 0, 0, "camera", None)
        self.plane = Point(0,0,0,"viewplane", None)
        #start_angles = rotation.Vector(-3*math.pi/4, -math.pi/4, 0.0)
        start_angles = rotation.Vector(0.0, 0.0, 0.0)
        self.R = rotation.Matrix()
        self.R.create_from_angles(start_angles)
        self.base_R = rotation.Matrix()
        self.base_R.create_from_angles(start_angles)


    def draw_axis(self,cr, color, midx, midy, fixed=True):
        axis_length = 2
        if fixed:
            rot = self.base_R.dot_product
        else:
            rot = dummy
        cr.set_source_rgb(color[0], color[1], color[2])
        p = self.transform_to_2d(rot(Point(axis_length,0,0)), not fixed)
        cr.move_to(midx, midy)
        cr.rel_line_to(p.x * self.scale, p.y * self.scale)
        cr.stroke()
        cr.move_to(midx + p.x * self.scale - 5, midy+p.y * self.scale -10)
        cr.set_source_rgb(color[0], color[1], color[2])
        cr.show_text("x")
        cr.stroke()
        p = self.transform_to_2d(rot(Point(0,axis_length,0)), not fixed)
        cr.move_to(midx, midy)
        cr.rel_line_to(p.x * self.scale, p.y * self.scale)
        cr.stroke()
        cr.move_to(midx + p.x * self.scale - 5, midy+p.y * self.scale -10)
        cr.set_source_rgb(color[0], color[1], color[2])
        cr.show_text("y")
        cr.stroke()
        p = self.transform_to_2d(rot(Point(0,0,axis_length)), not fixed)
        cr.move_to(midx, midy)
        cr.rel_line_to(p.x * self.scale, p.y * self.scale)
        cr.stroke()
        cr.move_to(midx + p.x * self.scale - 5, midy+p.y * self.scale -10)
        cr.set_source_rgb(color[0], color[1], color[2])
        cr.show_text("z")
        cr.stroke()
        
    def draw(self, cr, width, height):
        #clear
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        cr.set_source_rgb(0,0,0)
        cr.move_to(20,20)
        text = "viewplane z: {:.0f}".format(self.plane.z)
        cr.show_text(text)
        text = "angles: {:.2f}, {:.2f}, {:.2f}".format(
                self.R.base_angles.x, self.R.base_angles.y, 
                self.R.base_angles.z)
        cr.move_to(20,30)
        cr.show_text(text)
        if self.points is None:
            return()
        midx = width/2
        midy = height/2
        #draw axis, fixed/non-fixed
        self.draw_axis(cr, (0,0,1), midx, midy, True)
        self.draw_axis(cr, (0,0.9,0), midx, midy, False)
        #loop through points
        #first transform all points to the view plane
        transformed = self.get_transformed_point_dict()
        #now connect the points
        cr.set_source_rgb(0,0,0)
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
    
    def get_transformed_point_dict(self):
        transformed = dict()
        for point in self.points:
            p = self.transform_to_2d(point)
            transformed[point.name] = p
        return(transformed)

    def loadPoints(self, filename):
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
            new_point = Point(x, y, z, name, connected)
            self.points.append(new_point)
            
    def set_camera(self, x, y, z):
        self.camera.x = x
        self.camera.y = y
        self.camera.z = z
        print("camera set to [{:.1f}, {:.1f}, {:.1f}]".format(
            self.camera.x, self.camera.y, self.camera.z))

    def transform_to_2d(self, point, rotate=True):
        #transform with perspective
        name = point.name
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
        dydz = (y - self.camera.y) / (z - self.camera.z)
        y = self.camera.y + dydz * -(self.camera.z - self.plane.z)
        dxdz = (x - self.camera.x) / (z - self.camera.z)
        x = self.camera.x + dxdz * -(self.camera.z - self.plane.z)
        return(Point(x ,y, 0.0,
             "2d " + name, connected))        
             
    def set_timer(self, interval):
        gobject.timeout_add(interval, self.rotate)
        
    def do_rotate(self, widget, event, data=None):
        key = gtk.gdk.keyval_name(event.keyval)
        speed = math.pi/20
        if key == "Up":
            self.rotate(speed, 0.0, 0.0)
        elif key == "Down":
            self.rotate(-speed, 0.0, 0.0)
        if key == "Right":
            self.rotate(0.0, speed, 0.0)
        elif key == "Left":
            self.rotate(0.0, -speed, 0.0)
        if key == "Page_Up":
            self.rotate(0.0, 0.0, speed)
        elif key == "Page_Down":
            self.rotate(0.0, 0.0, -speed)

    def rotate(self, x, y, z):
        self.R.update_with_angles(rotation.Vector(x,y,z))
        cr = self.window.cairo_create()
        self.draw(cr, 300,300)
        return(True)
        
        

class Point(rotation.Vector):


    def __init__(self, x, y, z, name="", connected=None):
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
#    widget.set_timer(50)

    window.add_events(gtk.gdk.SCROLL_MASK | gtk.gdk.KEY_PRESS)
    window.connect("scroll-event", widget.do_zoom)
    window.connect("key-press-event", widget.do_rotate)
    window.add(widget)
    window.present()
    
    gtk.main()

if __name__ == "__main__":
    print("## z axis points out of screen ##")
    run(Screen)

