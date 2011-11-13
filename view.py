import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

class Screen:


    def __init__(self):
        self.window = gtk.Window()
        self.window.connect("delete-event", gtk.main_quit)
        self.drawing_area = DrawArea()
        self.window.add(self.drawing_area)
        self.window.set_size_request(300,300)
        self.window.show_all()
        
        
    def start(self):
        self.window.present()
    
    def redraw(self, pointdict):
        cr = self.drawing_area.get_cr()
        self.drawing_area.draw(cr, pointdict, *self.window.get_size())
    
        
class DrawArea(gtk.DrawingArea):


    def __init__(self):
        gtk.DrawingArea.__init__(self);
        self.pointdict = dict()
        
        
    def get_cr(self, event=None):
        cr = self.window.cairo_create()
        if event:
            cr.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
            cr.clip()
        return(cr)
        
    def draw(self, cr, pointdict, width, height):
        #clear
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        if pointdict:
            self.draw_from_dict(cr, width/2, height/2, pointdict)

    def draw_from_dict(self, cr, midx, midy, pointdict):        
        for key in pointdict:
            p = pointdict[key]
            cr.set_source_rgb(p.color[0], p.color[1], p.color[2])
            if p.connected is None:
                continue
            connected = p.connected.split(',')
            for c in connected:
                p2 = pointdict[c]
                cr.move_to(midx + p.x, midy+ p.y)
                cr.line_to(midx + p2.x, midy + p2.y)
                cr.stroke()

    
        
