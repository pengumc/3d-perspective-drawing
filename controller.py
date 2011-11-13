import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import pointcloud
import view
import math

class Controller:


    def __init__(self):
        self.point_cloud = pointcloud.PointCloud("points.xml")
        self.gui = view.Screen()
        self.connect_signals()
        
    def connect_signals(self):
        self.connect_inputdev()

    def run(self):
        self.gui.start()
        gtk.main()

    def redraw(self):
        self.gui.redraw(self.point_cloud.transformed)

    def do_keyboard(self, widget, event, data=None):
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
        self.point_cloud.rotate(x, y, z)
        self.redraw()
        
    def do_scroll(self, widget, event, data=None):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.point_cloud.zoom(True)
        else:
            self.point_cloud.zoom(False)
        self.redraw()

    def do_expose(self, event, data=None):
        self.redraw()
    
    def connect_inputdev(self):
        self.gui.window.add_events(gtk.gdk.SCROLL_MASK | gtk.gdk.KEY_PRESS)
        self.gui.window.connect("scroll-event", self.do_scroll)
        self.gui.window.connect("key-press-event", self.do_keyboard)
        self.gui.drawing_area.connect(
            "expose_event", self.do_expose)
        



