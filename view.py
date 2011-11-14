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
        self.drawing_area.draw(cr, pointdict, True,*self.window.get_size())
    
    def add_to_drawing(self, pointdict):
        cr = self.drawing_area.get_cr()
        self.drawing_area.draw(cr, pointdict, False, *self.window.get_size())
        
    def draw_text(self, text):
        cr = self.drawing_area.get_cr()
        self.drawing_area.draw_text(cr, text)
        
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
        
    def draw(self, cr, pointdict, clear, width, height):
        if clear:
            cr.set_source_rgb(1, 1, 1)
            cr.rectangle(0, 0, width, height)
            cr.fill()
        if pointdict:
            self.draw_from_dict(cr, width/2, height/2, pointdict)

    def draw_from_dict(self, cr, midx, midy, pointdict):        
        for key in pointdict:
            p = pointdict[key]
            cr.set_source_rgb(p.color[0], p.color[1], p.color[2])
            if p.connected is None or p.connected == "":
                continue
            connected = p.connected.split(',')
            for c in connected:
                p2 = pointdict[c]
                cr.move_to(midx + p.x, midy+ p.y)
                cr.line_to(midx + p2.x, midy + p2.y)
                cr.stroke()

    
    def draw_text(self, cr, text):
        cr.rectangle(0, 0, 150, 40)
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.fill()
        cr.set_source_rgb(0,0,0)
        cr.move_to(0,22)
        cr.show_text(text)

