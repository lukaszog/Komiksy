import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import os
from random import randint
import urllib2
import os
from BeautifulSoup import BeautifulSoup
from threading import Thread
import gobject


BASE_URL = "http://xkcd.com"

proxy = {"http": "http://username:pass@proxy:port/",
         "https": "https://username:pass@proxy:port/"}

Proxy = urllib2.ProxyHandler(proxy)
opener = urllib2.build_opener(Proxy)
urllib2.install_opener(opener)


class MainWindow:
    def __init__(self):
        self.window = Gtk.Window()  # A Gtk window
        self.window.set_title('xkcd')
        self.window.connect("destroy", self.close_application)
        # self.window.set_size_request(800,600)

        self.box = Gtk.VBox(False, 0)
        self.window.add(self.box)
        self.box.show()

        self.hbox = Gtk.HBox(False, 0)  # A horizontal box to pack buttons
        self.box.pack_start(self.hbox, False, False, 3)
        self.hbox.show()

        self.but1 = Gtk.Button("previous")  # Button for previous
        self.but1.show()
        self.but1.connect("clicked", self.pre_image)
        self.hbox.pack_start(self.but1, True, True, 0)

        self.but2 = Gtk.Button("random")  # Button for random
        self.but2.show()
        self.but2.connect("clicked", self.rand_image)
        self.hbox.pack_start(self.but2, True, True, 0)

        self.but3 = Gtk.Button("next")  # Button for next
        self.but3.show()
        self.but3.connect("clicked", self.next_image)
        self.hbox.pack_start(self.but3, True, True, 0)

        self.imgbox = Gtk.HBox(False, 0)  # Horizontal Box to pack image
        # self.imgbox.set_size_request(800,550)
        # self.sw1.add(self.imgbox)
        self.box.pack_start(self.imgbox, False, False, 0)
        self.imgbox.show()

        #        self.sw1 = Gtk.ScrolledWindow()
        #        self.sw1.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
        #        self.sw1.show()
        #        self.imgbox.pack_start(self.sw1, False, False, 0)
        #        self.imgbox.add(self.sw1)

        self.image = Gtk.Image()  # A Gtk.Image object
        self.imgbox.pack_start(self.image, True, True, 0)
        # self.sw1.add(self.image)

        # self.get_first_image()

        # print self.img_file
        # print os.path.exists(self.img_file)
        # self.image.set_from_file(self.img_file)
        # self.image.set_from_file(None)
        # self.image.show()

        self.window.show()
        self.get_first_image_thread()
        """
        print self.img_file
        print os.path.exists(self.img_file)
        self.image.set_from_file(self.img_file)
        self.image.show()
        """

    def next_image(self, widget=None, data=None, index=None):
        URL = self.get_next_URL(self.soup)
        print URL, "URL"
        if URL is None:
            return
        self.soup = self.get_soup(URL)
        img_URL = self.get_image_URL(self.soup)
        print "img_URL", img_URL
        file_path = self.save_img(img_URL, URL)
        if file_path is None:
            return
        print "file_path", file_path
        self.ch_img(file_path)

    def ch_img(self, file_path):
        print "ch_img", file_path
        self.img_file = file_path
        self.image.set_from_file(self.img_file)
        self.image.show()
        title = "-".join(["xkcd", file_path.split("/")[-1]])
        self.window.set_title(title)

    def pre_image(self, widget=None, data=None):
        URL = self.get_previous_URL(self.soup)
        print URL, "URL"
        if URL is None:
            return
        self.soup = self.get_soup(URL)
        img_URL = self.get_image_URL(self.soup)
        print "img_URL", img_URL
        file_path = self.save_img(img_URL, URL)
        if file_path is None:
            return
        print "file_path", file_path
        self.ch_img(file_path)

    def rand_image(self, widget=None, data=None):
        URL = self.get_rand_URL(self.soup)
        print URL, "URL"
        if URL is None:
            return
        self.soup = self.get_soup(URL)
        img_URL = self.get_image_URL(self.soup)
        print "img_URL", img_URL
        file_path = self.save_img(img_URL, URL)
        if file_path is None:
            return
        print "file_path", file_path
        self.ch_img(file_path)

    def get_first_image_thread(self):
        Thread(target=self.get_first_image).start()

    def get_first_image(self):
        self.soup = self.get_soup(BASE_URL)
        print "soup done"
        img_URL = self.get_image_URL(self.soup)
        print img_URL
        file_path = self.save_img(img_URL, BASE_URL)
        print file_path
        self.ch_img(file_path)

    def close_application(self, widget, data=None):
        rem_dir = os.listdir(".down_xkcd")
        for dirs in rem_dir:
            os.remove(os.path.join(".down_xkcd", dirs))
        os.removedirs(".down_xkcd")
        Gtk.main_quit()

    def get_soup(self, URL):
        try:
            page = urllib2.urlopen(URL)
        except urllib2.HTTPError, e:  # Read more about catching errors
            print "Got Error"
            print e
            if "403" in e:
                print "Don't be a SPAM. Try again later."
            if "407" in e:
                print "Check your Proxy configuration"
            return
        soup = BeautifulSoup(page.read())
        return soup

    def get_next_URL(self, soup):
        """
    see the page source.
    <li><a href="/17/" accesskey="n">Next &gt;</a></li> (Line no. 83, probably)
    so to get the hyperlink,
        "href":True ==> href present
        "accesskey":n ==> accesskey="n"
        soup.find("a",{"href":True,"accesskey":"n"})["href"] will give u"/17/"
        """
        URL = soup.find("a", {"href": True, "accesskey": "n"})["href"]
        if URL == "#":
            # latest comic
            return None
        URL = BASE_URL + URL
        return URL

    def get_previous_URL(self, soup):
        """
    see the page source.
    <li><a href="/15/" accesskey="p">&lt; Prev</a></li> (Line no. 81, probably)
    so to get the hyperlink,
        "href":True ==> href present
        "accesskey":p ==> accesskey="p"
        soup.find("a",{"href":True,"accesskey":"p"})["href"] will give u"/15/"

        """
        URL = soup.find("a", {"href": True, "accesskey": "p"})["href"]
        if URL == "#":
            return None
        URL = BASE_URL + URL
        return URL

    def get_rand_URL(self, soup):
        URL = soup.find("a", {"href": True, "id": "rnd_btn_t"})["href"]
        return URL

    def get_image_URL(self, soup):
        """
    see the page source.
    <img src="http://imgs.xkcd.com/comics/monty_python.jpg" title="I went to a dinner where there was a full 10 minutes of Holy Grail quotes exchanged, with no context, in lieu of conversation.  It depressed me badly." alt="Monty Python -- Enough" />
    so to get image URL,
        Tag ==> "img"
        "img" tag must contain "src","alt","title"
        soup.find("img",{"src":True,"alt":True,"title":True})["src"] will give u"http://imgs.xkcd.com/comics/monty_python.jpg"
        """
        img_URL = soup.find("img", {"src": True, "alt": True, "title": True})["src"]
        return img_URL

    def save_img(self, img_URL, URL):
        """
    try:
        page = opener.open(img_URL) # get image page
    except urllib2.HTTPError, e:
        #print "Got Error:",e
        if "403" in e:
            print "Don't be a SPAM. Try again later."
        if "407" in e:
            print "Check your Proxy configuration"
        return
    if not URL.endswith("/"):
        URL=URL+"/"
        """
        """
    URL = "http://xkcd.com/16/"
    image_URL = "http://imgs.xkcd.com/comics/monty_python.jpg"
        """
        try:
            page = opener.open(img_URL)  # get image page
        except urllib2.HTTPError:
            self.window.set_title("xkcd-Unable to fetch comics")
            return None
        if not URL.endswith("/"):
            URL = URL + "/"

        filename = "-".join([URL.split("/")[-2], img_URL.split("/")[-1]])  # make filename - "16-monty_python.jpg"
        f = open(os.path.join(".down_xkcd", filename), "wb")  # open a file using absolute path
        f.write(page.read())  # write image
        f.close()
        print filename, "saved"
        return os.path.join(".down_xkcd", filename)


if __name__ == "__main__":
    try:
        os.mkdir(".down_xkcd")
    except OSError:
        print ".down_xkcd exists"
    MainWindow()
    Gtk.main()