import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import pointcloud
import view
import math
usbdev_failed = False
try:
    import usbdev 
except Exception as e:
    print(e)
    usbdev_failed = True

#there are some function that require/use gtk, they're marked
#with #GTK

USB_TIMEOUT = 50

class Controller:


    def __init__(self, accelerometer=False):
        self.accelerometer = accelerometer
        if accelerometer:
            if usbdev_failed:
                print('failed to load usb module, exiting...')
                exit()
            self.usbdev = usbdev.UsbDev()
        self.point_cloud = pointcloud.PointCloud("points.xml")
        self.gui = view.Screen()
        self.connect_signals()
        self.acc_point_list = [
            pointcloud.Point(0, 0, 0, "Acc0", "AccX,AccY,AccZ", [1,0,0]),
             pointcloud.Point(0, 0, 0, "AccX"),
             pointcloud.Point(0, 0, 0, "AccY"),
             pointcloud.Point(0, 0, 0, "AccZ"),
             pointcloud.Point(0, 0, 0, "AccVector", "Acc0", [0,0.5,0.5])]
   
    def connect_signals(self):
        self.connect_inputdev()
        #GTK        
        if self.accelerometer:
            #timeout is for accelerometer stuff only
            gobject.timeout_add(USB_TIMEOUT, self.timeout)
        
    def timeout(self):
        #sample new values
        self.usbdev.update_adc()
        adc = self.usbdev.get_adc_int()
        x = adc[0] - usbdev.UsbDev.ADC_MID
        y = adc[2] - usbdev.UsbDev.ADC_MID
        z = adc[1] - usbdev.UsbDev.ADC_MID
        #set points for accelerometer output drawing
        self.acc_point_list[1].x = x
        self.acc_point_list[2].y = y
        self.acc_point_list[3].z = z
        self.acc_point_list[4].x = x
        self.acc_point_list[4].y = y
        self.acc_point_list[4].z = z
        #get orientation and rotate the pointcloud accordingly
        ori = self.usbdev.get_orientation()
        self.point_cloud.rotate_abs(ori[0], ori[1], ori[2])
        self.redraw()
        #draw some text and add the accelerometer drawing
        self.gui.draw_text("{:.3f}, {:.3f}, {:.3f}".format(
            ori[0], ori[1], ori[2]))
        self.gui.add_to_drawing(self.point_cloud.get_transformed_point_dict(
            self.acc_point_list))
        return(True)
        
    def run(self):
        self.gui.start()
        #GTK
        gtk.main()

    def redraw(self):
        self.gui.redraw(self.point_cloud.transformed)

    #GTK    
    def do_keyboard(self, widget, event, data=None):
        key = gtk.gdk.keyval_name(event.keyval)
        speed = math.pi/20
        if key == "Up":
            self.rotate(speed, 0.0, 0.0)
        elif key == "Down":
            self.rotate(-speed, 0.0, 0.0)
        elif key == "Right":
            self.rotate(0.0, speed, 0.0)
        elif key == "Left":
            self.rotate(0.0, -speed, 0.0)
        elif key == "Page_Up":
            self.rotate(0.0, 0.0, speed)
        elif key == "Page_Down":
            self.rotate(0.0, 0.0, -speed)
        elif key == "Home":
            self.point_cloud.reset_rotation()
            self.redraw()
        

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
        #GTK 
        self.gui.window.add_events(gtk.gdk.SCROLL_MASK | gtk.gdk.KEY_PRESS)
        self.gui.window.connect("scroll-event", self.do_scroll)
        self.gui.window.connect("key-press-event", self.do_keyboard)
        self.gui.drawing_area.connect(
            "expose_event", self.do_expose)
        



