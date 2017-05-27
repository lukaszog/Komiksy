import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import urllib2
import os
import glob
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

BASE_URL = "http://xkcd.com"

class MainWindow:

    def __init__(self):
        self.surl = "http://xkcd.com"
        self.maxNumber = ""
        self.window = Gtk.Window()  # A gtk window
        self.window.set_title('xkcd')
        self.window.connect("delete-event", Gtk.main_quit)

        self.box = Gtk.VBox(False, 0)
        self.labelNumber = Gtk.Label()
        self.labelNumber.set_text("Number")
        self.labelNumber.show()
        self.box.pack_start(self.labelNumber, False, False, 3)
        self.labelTitle = Gtk.Label()
        self.labelTitle.set_markup("<b>Title</b>")
        self.labelTitle.show()
        self.box.pack_start(self.labelTitle, False, False, 3)
        self.searchbox = Gtk.HBox(False, 0)
        self.searchLabel = Gtk.Label("Podaj numer: ")
        self.searchLabel.show()
        self.searchbox.pack_start(self.searchLabel, True, True, 3)
        self.searchEntry = Gtk.Entry()
        self.searchEntry.show()
        self.searchbox.pack_start(self.searchEntry, True, True, 3)
        self.searchBtn = Gtk.Button("Search")
        self.searchBtn.show()
        self.searchBtn.connect("clicked", self.searchImage)
        self.searchbox.pack_start(self.searchBtn, True, True, 3)
        self.searchbox.show()
        self.window.add(self.box)
        self.box.show()
        self.box.pack_start(self.searchbox, False, False, 3)
        self.hbox = Gtk.HBox(False, 0)  # A horizontal box to pack buttons
        self.box.pack_start(self.hbox, False, False, 3)
        self.hbox.show()

        self.prevBtn = Gtk.Button("previous")  # Button for previous
        self.prevBtn.show()
        self.prevBtn.connect("clicked", self.preImage)
        self.hbox.pack_start(self.prevBtn, True, True, 0)

        self.randBtn = Gtk.Button("random")  # Button for random
        self.randBtn.show()
        self.randBtn.connect("clicked", self.randImage)
        self.hbox.pack_start(self.randBtn, True, True, 0)

        self.nextBtn = Gtk.Button("next")  # Button for next
        self.nextBtn.show()
        self.nextBtn.connect("clicked", self.nextImage)
        self.hbox.pack_start(self.nextBtn, True, True, 0)

        self.imgbox = Gtk.HBox(False, 0)  # Horizontal Box to pack image

        self.image = Gtk.Image()  # A gtk.Image object
        self.imgbox.pack_start(self.image, True, True, 0)
        self.img_file = ""
        self.image.set_from_file(self.img_file)
        self.image.show()

        self.box.pack_start(self.imgbox, False, False, 0)
        self.imgbox.show()
        url, title, number = self.getImage("")
        self.maxNumber = number
        self.showImage("")

        self.window.show()

    def searchImage(self, button):
        if int(self.searchEntry.get_text()) <= int(self.maxNumber):
            self.surl = BASE_URL + '/' + self.searchEntry.get_text()
            self.showImage(self.searchEntry.get_text())
        else:
            self.searchEntry.set_text("Too big number")

    def preImage(self, button):
        soup = self.getSoup(self.surl)
        u = soup.find("a", {"href": True, "accesskey": "p"})["href"]
        self.surl = BASE_URL + u
        image_number = self.surl.split('//')[1].split('/')[1]
        self.showImage(image_number)

    def randImage(self, button):
        response = urllib2.urlopen("https://c.xkcd.com/random/comic/")
        self.surl = response.geturl()
        image_number = self.surl.split('//')[1].split('/')[1]
        self.showImage(image_number)

    def nextImage(self, button):
        soup = self.getSoup(self.surl)
        u = soup.find("a", {"href": True, "accesskey": "n"})["href"]
        if u == "#":
            return None
        self.surl = BASE_URL + u
        image_number = self.surl.split('//')[1].split('/')[1]
        self.showImage(image_number)

    def getSoup(self, url = BASE_URL):

        self.currentUrl = url
        page = requests.get(url).content
        soup = BeautifulSoup(page, 'lxml')

        return soup

    def showImage(self, number):

        url, title, number = self.getImage(number)
        self.labelTitle.set_markup("<b>" + title + "</b>")
        self.labelNumber.set_text(number)

        imageExist = ""
        filename = ""

        for f in os.listdir('cache'):
            if os.path.isfile(os.path.join('cache', f)):
                if f.split("_")[0] == number:
                    imageExist = 1
                    filename = f

        if imageExist == 1:
            imagePath = os.path.join('cache', filename)
            self.img_file = imagePath
            self.image.set_from_file(self.img_file)
        else:
            self.saveImage(url, number)
            response = urllib2.urlopen(str(url))
            loader = GdkPixbuf.PixbufLoader()
            loader.write(response.read())
            loader.close()
            self.image.set_from_pixbuf(loader.get_pixbuf())

        self.image.show()

    def getImage(self, number):
        soup = self.getSoup(BASE_URL + '/' + number)
        if isinstance(soup, BeautifulSoup):
            title = soup.find("div", {"id": "ctitle"})

            for br in soup.findAll('br'):
                next_s = br.nextSibling
                if not (next_s and isinstance(next_s, NavigableString)):
                    continue
                next2_s = next_s.nextSibling
                if next2_s and isinstance(next2_s, Tag) and next2_s.name == 'br':
                    text = str(next_s).strip()
                    if text:
                        imageNumber = next_s.split('//')[1].split('/')[1]

            imageUrl = soup.find("img", {"src": True, "alt": True, "title": True})["src"]
            return 'http:' + imageUrl, title.text, imageNumber

    def saveImage(self, url, number):

        try:
            page = urllib2.urlopen(url)
        except urllib2.HTTPError:
            return None
        image_name = url.split('//')[1].split('/')[2]
        save_file = open(os.path.join("cache", number+"_"+image_name), "wb")
        save_file.write(page.read())
        save_file.close()


if __name__ == "__main__":
    try:
        os.mkdir("cache")
    except OSError:
        print "cache exists"
    MainWindow()
    Gtk.main()