import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

class ScaleImage:
    def __init__(self):
        self.temp_height = 0
        self.temp_width = 0

        window = Gtk.Window()
        image = Gtk.Image()
        image.set_from_file('cache/730_circuit_diagram.png')
        self.pixbuf = image.get_pixbuf()
        drawing_area = Gtk.DrawingArea()
        drawing_area.set_size_request(300, 300)
        drawing_area.connect('expose-event', self.expose)

        box = Gtk.ScrolledWindow()
        box.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
        box.add(image)

        window.add(drawing_area)
        window.add(box)
        window.set_size_request(300, 300)
        window.show_all()

    def expose(self, widget, event, window):
        allocation = widget.get_allocation()
        if self.temp_height != allocation.height or self.temp_width != allocation.width:
            self.temp_height = allocation.height
            self.temp_width = allocation.width
            pixbuf = self.pixbuf.scale_simple(allocation.width, allocation.height, Gtk.gdk.INTERP_BILINEAR)
            widget.set_from_pixbuf(pixbuf)

    def close_application(self, widget, event, data=None):
        Gtk.main_quit()
        return False

if __name__ == "__main__":
    ScaleImage()
    Gtk.main()