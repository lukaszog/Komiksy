import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import urllib2
import os
import glob
from BeautifulSoup import BeautifulSoup, NavigableString, Tag

URL = "http://xkcd.com"


class Main(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_title("XKCD viewer")
        self.box = Gtk.VBox()
        self.add(self.box)
        self.box.show()

        self.image_box = Gtk.VBox()

        self.hbox = Gtk.HBox()
        self.navi_box = Gtk.HBox()
        self.navi_box.set_size_request(300, 50)
        self.title_box = Gtk.VBox(spacing=10)
        self.box.pack_start(self.hbox, False, False, 0)
        self.box.add(self.navi_box)
        self.box.add(self.title_box)
        self.hbox.show()
        self.image = Gtk.Image()
        self.title_label = Gtk.Label()
        self.number_label = Gtk.Label()
        self.title_box.add(self.number_label)
        self.title_box.add(self.title_label)
        self.image_box.add(self.image)
        self.image_box.show()
        self.box.add(self.image_box)
        self.num_label = Gtk.Label("Podaj numer: ")
        self.num_entry = Gtk.Entry()
        self.go_button = Gtk.Button("Pokaz")
        self.go_button.show()
        self.go_button.connect('clicked', lambda x: self.show_image(self.num_entry.get_text()))
        self.hbox.add(self.num_label)
        self.hbox.add(self.num_entry)
        self.hbox.add(self.go_button)

        self.previous_button = Gtk.Button('Poprzedni')
        self.previous_button.set_size_request(100, 50)
        self.previous_button.connect('clicked', lambda x: self.show_image_direction('prev'))
        self.random_button = Gtk.Button('Losowy')
        self.random_button.set_size_request(100, 50)
        self.random_button.connect('clicked', lambda x: self.show_image_direction('random'))
        self.next_button = Gtk.Button('Nastepny')
        self.next_button.set_size_request(100, 50)
        self.next_button.connect('clicked', lambda x: self.show_image_direction('next'))
        self.navi_box.add(self.previous_button)
        self.navi_box.add(self.random_button)
        self.navi_box.add(self.next_button)

        self.show_image("")
        self.show()
        self.connect('destroy', Gtk.main_quit)

        self.soup = self.load_soup(URL)
        self.random_limit = ""

    def show_image(self, number):

        url, title, number = self.get_image(number)

        is_image = ""
        filename = ""
        for file in glob.glob('cache\\' + number + "_*.png"):
            is_image = 1
            filename = file

        if is_image == 1:
            image_path = filename
            self.image.set_from_file(image_path)
            print "Wyswietlam: {}".format(image_path)
        else:
            print "Obrazek jest pobierany..."
            self.save_image(url, number)
            response = urllib2.urlopen(str(url))
            loader = GdkPixbuf.PixbufLoader()
            loader.write(response.read())
            loader.close()
            self.image.set_from_pixbuf(loader.get_pixbuf())

        self.set_title(title)
        self.number_label.set_markup('Numer obrazka: ' + number)
        self.title_label.set_markup('Tytul: <b>' + title + '</b>')
        self.image.show()

    def show_image_direction(self, move):

        image_url = self.get_image_direction(self.soup, move)

        print image_url
        if image_url is None:
            return
        image_number = image_url.split('//')[1].split('/')[1]
        self.soup = self.load_soup(image_url)
        self.show_image(image_number)

    def get_image_direction(self, soup, move):

        if move == 'prev':
            image_url = soup.find("a", {"href": True, "accesskey": "p"})["href"]
        elif move == 'next':
            image_url = soup.find("a", {"href": True, "accesskey": "n"})["href"]
        elif move == 'random':
            response = urllib2.urlopen("https://c.xkcd.com/random/comic/")
            image_url = response.geturl()

        if image_url == "#":
            return None
        if move == 'random':
            previous_image = image_url
        else:
            previous_image = URL + image_url
        return previous_image

    def save_image(self, url, number):

        print "Url do zapisu {}".format(url)

        try:
            page = urllib2.urlopen(url)
        except urllib2.HTTPError:
            return None
        image_number = url.split('//')[1].split('/')[2]
        save_file = open(os.path.join("cache", number+"_"+image_number), "wb")
        save_file.write(page.read())
        save_file.close()

        print "Zapisuje plik o numerze: {} i tytule {}".format(number, image_number)

        #return os.pardir.join("cache", image_number + ".png")

    def get_image(self, number):
        soup = self.load_soup(URL + '/' + number)
        if isinstance(soup, BeautifulSoup):
            image_title = soup.find("div", {"id": "ctitle"})

            for br in soup.findAll('br'):
                next_s = br.nextSibling
                if not (next_s and isinstance(next_s, NavigableString)):
                    continue
                next2_s = next_s.nextSibling
                if next2_s and isinstance(next2_s, Tag) and next2_s.name == 'br':
                    text = str(next_s).strip()
                    if text:
                        image_number = next_s.split('//')[1].split('/')[1]

            image_url = soup.find("img", {"src": True, "alt": True, "title": True})["src"]
            print image_url
            return 'http:' + image_url, image_title.text, image_number

    def load_soup(self, URL):
        try:
            page = urllib2.urlopen(URL)
        except urllib2.HTTPError as e:
            print "Error"
            print e
            if e.code == 403:
                print "Try again later"
            if e.code == 404:
                print "Blad 404"
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                           Gtk.ButtonsType.OK, "Nie ma takiego obrazka")
                dialog.format_secondary_text(
                    "Podaj inny numer")
                dialog.run()
                dialog.destroy()
            return
        soup = BeautifulSoup(page.read())
        return soup

if __name__ == "__main__":
    win = Main()
    win.show_all()
    Gtk.main()
