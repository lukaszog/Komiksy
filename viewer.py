# coding=utf-8
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import urllib2
import os
import glob
from BeautifulSoup import BeautifulSoup, NavigableString, Tag

# adres strony, z ktorej beda pobierane obrazki
URL = "http://xkcd.com"
# katalog do zapisu obrazkow
DIR = "cache"


class Main(Gtk.Window):
    """Glowna klasa widoku aplikacji, klasa rysuje obiekty GTK.
     
    - pole do wpisania numeru.
    - obrazek.
    - przyciski.
    - suwak do skali.
    """

    def __init__(self):
        """Konstruktor klasy dziedziczy po Gtk.Window - glowna klasa oplikacji.
        
        Zadaniem klasy jest przygotowanie okna, w ktorym wyswietla sie obrazek wraz z przyciskami nawigacyjnymi.
        """

        Gtk.Window.__init__(self)
        self.set_title("XKCD viewer")
        self.set_size_request(500, 300)
        # glowny kontener
        self.box = Gtk.VBox()
        self.add(self.box)
        self.box.show()
        # kontener dla obrazka
        self.image_box = Gtk.VBox()
        self.hbox = Gtk.HBox()
        # kontener dla nawigacji
        self.navi_box = Gtk.HBox()
        # kontener dla tytulu
        self.title_box = Gtk.VBox(spacing=10)
        self.box.pack_start(self.hbox, False, False, 0)
        self.hbox.show()
        # bufor dla obrazka
        self.pic = GdkPixbuf.Pixbuf()
        # scroll window, w ktorym bedzie obrazek
        self.scroll_window = Gtk.ScrolledWindow()
        self.scroll_window.set_size_request(800, 500)
        # obiekt dla obrazka
        self.image = Gtk.Image()
        self.title_label = Gtk.Label()
        self.number_label = Gtk.Label()
        self.title_box.add(self.number_label)
        self.title_box.add(self.title_label)
        self.image_box.add(self.image)
        self.image_box.show()
        self.box.add(self.title_box)
        self.scroll_window.add(self.image_box)
        self.box.add(self.scroll_window)
        self.box.pack_start(self.navi_box, False, False, 0)
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

        # stworzenie skali do regulacji rozmiarem obrazka
        adjustment = Gtk.Adjustment(40, 40, 200, 20, 20, 0)
        self.h_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
        self.h_scale.set_digits(0)
        self.h_scale.set_hexpand(True)
        self.h_scale.set_valign(Gtk.Align.START)
        self.h_scale.connect("value-changed", self.scale_moved)
        self.box.add(self.h_scale)

        self.navi_box.add(self.previous_button)
        self.navi_box.add(self.random_button)
        self.navi_box.add(self.next_button)

        # pokazanie najnowszego obrazka przy starcie
        self.show_image("")
        self.show()
        self.connect('destroy', Gtk.main_quit)
        # parsowanie strony glownej
        self.soup = XKCD.load_soup(URL)

    def scale_moved(self, event):
        """Funkcja dokonuje przeskalowania obrazku, wedlug parametru scale."""

        # obliczanie skali
        scale = int(self.h_scale.get_value()) / 100.0
        self.image.set_from_pixbuf(self.pic.scale_simple(self.pic.get_width() * scale,
                                                         self.pic.get_height() * scale, 2))

    def show_image(self, number):
        """Funkcja odpowiedzialna za wyswietlenie obrazka w oknie."""

        # pobranie obrazka
        url, title, number = XKCD.get_image(number)

        is_image, filename = "", ""
        # sprawdzenie czy obrazek ktory chcemy wyswietlic znajduje sie w katalogu
        for f in glob.glob('cache/' + number + "_*.png"):
            is_image = 1
            filename = f
        # jezeli obrazek zostal znaleziony w katalogu jest wyswietlany
        if is_image == 1:
            image_path = filename
            self.pic = self.pic.new_from_file(image_path)
            self.image.set_from_pixbuf(self.pic)
        else:
            # w przeciwnym wypadku pobieramy obrazek z sieci
            XKCD.save_image(url, number)
            response = urllib2.urlopen(str(url))
            loader = GdkPixbuf.PixbufLoader()
            loader.write(response.read())
            loader.close()
            self.image.set_from_pixbuf(loader.get_pixbuf())

        self.set_title(title)
        self.number_label.set_markup('Numer obrazka: ' + number)
        self.title_label.set_markup('Tytul: <b>' + title + '</b>')
        # update aktualnej strony
        self.soup = XKCD.load_soup(URL + '/' + number)
        self.image.show()

    def show_image_direction(self, move):
        """Pobranie obrazka w zaleznosci od kliknietego przycisku {Nastepnny, Losowy, Poprzedni}."""

        image_url = XKCD.get_image_direction(self.soup, move)

        if image_url is None:
            return
        image_number = image_url.split('//')[1].split('/')[1]
        print image_url
        self.soup = XKCD.load_soup(image_url)
        # wyswietlenie obrazka
        self.show_image(image_number)


class XKCD:
    """Klasa odpowiedzialna za pobieranie danych ze strony xkcd.com.
    
    Zdecydowalem sie na uzycie metod statycznych, poniewaz chce traktowac klase jako biblioteke
    """

    def __init__(self):
        """Pusty konstruktor klasy."""

        pass

    @staticmethod
    def get_image_direction(soup, move):
        """Pobranie danych o obrazku w zaleznosci od kliknietego przycisku.
         
        Dane dla soup sa podawane na podstawie kodu HTML strony.
        """

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

    @staticmethod
    def save_image(url, number):
        """Funkcja, ktora pobiera obrazek do katalogu cache."""

        try:
            page = urllib2.urlopen(url)
        except urllib2.HTTPError:
            return None

        if not os.path.exists(DIR):
            os.makedirs(DIR)

        image_number = url.split('//')[1].split('/')[2]
        # zapisanie obrazka do katalogu
        with open(os.path.join(DIR, number + "_" + image_number), "wb") as f:
            f.write(page.read())
            f.close()
        print "Zapisuje plik o numerze: {} i tytule {}".format(number, image_number)

    @staticmethod
    def get_image(number):
        """Funkcja, ktora pobiera obrazek z danego adresu url."""

        soup = XKCD.load_soup(URL + '/' + number)
        if isinstance(soup, BeautifulSoup):
            image_title = soup.find("div", {"id": "ctitle"})

            # wyszukiwanie numeru obrazka glownego
            for br in soup.findAll('br'):
                next_br_tag = br.nextSibling
                if not (next_br_tag and isinstance(next_br_tag, NavigableString)):
                    continue
                next2_s = next_br_tag.nextSibling
                if next2_s and isinstance(next2_s, Tag) and next2_s.name == 'br':
                    text = str(next_br_tag).strip()
                    if text:
                        image_number = next_br_tag.split('//')[1].split('/')[1]

            image_url = soup.find("img", {"src": True, "alt": True, "title": True})["src"]
            print image_url
            return 'http:' + image_url, image_title.text, image_number

    @staticmethod
    def load_soup(url):
        """Funkcja odpowiedzialna za przygotowanie danej strony do parsowania przez BeautyfoulSoup."""

        try:
            page = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            # W razie zapytania o strone ktora nie istnieje zwracany jest error 404
            print "Error"
            print e
            if e.code == 403:
                print "Sproboj pozniej"
            if e.code == 404:
                print "Blad 404"
                dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,
                                           Gtk.ButtonsType.OK, "Nie ma takiego obrazka")
                dialog.format_secondary_text(
                    "Podaj inny numer")
                dialog.run()
                dialog.destroy()
                return
            return
        # parsowanie bierzacej strony
        soup = BeautifulSoup(page.read())
        return soup

if __name__ == "__main__":
    # uruchomienie aplikacji
    win = Main()
    win.show_all()
    Gtk.main()
