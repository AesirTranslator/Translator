import signal
import subprocess
import webbrowser
from gi.repository import GLib
import gi
import requests
from Xlib import display
import cairo

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gdk, GdkPixbuf
from gi.repository import Gtk
from gi.repository import AppIndicator3 as appindicator
from bs4 import BeautifulSoup
from parameters import *

from gi.repository import Notify


from Xlib import display

import time



class aesirBallonNotifier(Gtk.Window):

    def timeout(self):
        self.destroy()

    def __init__(self):
        Gtk.Window.__init__(self )
        data = display.Display().screen().root.query_pointer()._data
        self.move(data["root_x"], data["root_y"])
        self.connect("draw", self.expose)
        GLib.timeout_add_seconds (1, self.timeout)
        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        if self.visual != None and self.screen.is_composited():
            self.set_visual(self.visual)
        self.set_size_request(250,30)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_app_paintable(True)
        signal.signal(signal.SIGINT, signal.SIG_DFL)  # listen to quit signal
        self.show_all()

    def expose (self,widget,cr):

        cr.set_source_rgba(.2, .2, .2, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.set_source_rgb (255, .2, .2 )
        w, h = self.get_size()

        cr.select_font_face("Courier", cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(20)

        (x, y, width, height, dx, dy) = cr.text_extents("ZetCode")

        cr.move_to(0 , h/2)
        cr.show_text("Translating!")


class aesirNotifier():
    # Define a callback function

    def callbackFunction(self, notification, signal_text):

        if signal_text == "open-text":
            temp_dir, temp_file = returnTempDirectoryAndFile()

            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            fd = open(temp_dir + temp_file, 'w+')
            fd.write(self.text)
            fd.close()
            proc = subprocess.Popen(['gedit', temp_file])
        elif signal_text == "open-url":
            webbrowser.open(self.url)  # Go to example.com

    def init(self):
        Notify.init(self.application)
        self.notification = Notify.Notification.new("AESIR Translator", "Result has been copied to clipboard")
        image = GdkPixbuf.Pixbuf.new_from_file(returnIconPath("indicator-disable"))
        self.notification.set_icon_from_pixbuf(image)

        signal.signal(signal.SIGINT, signal.SIG_DFL)  # listen to quit signal

    def show(self):
        self.notification.show()

    def __init__(self, id, url, text):

        self.application = id
        self.url = url
        self.text = text
        self.init()
        self.addAction()
        self.show()

    def addAction(self):
        self.notification.add_action(
            "open-text",
            "Open in Text Editor!",
            self.callbackFunction,

        )

        self.notification.add_action(
            "open-url",
            "Open in Google",
            self.callbackFunction,

        )


class aesirGoogleTranslator:
    def __init__(self, api_url):
        self.api_url = api_url
        self.api_url_dummy = api_url
        self.current_url = None

    def request(self, source, target, text):
        self.api_url = self.api_url_dummy
        self.api_url = self.api_url.replace("%hl", source)
        self.api_url = self.api_url.replace("%sl", target)
        self.api_url = self.api_url.replace("%q", text)
        x = requests.post(self.api_url)
        source = BeautifulSoup(x.content, "html.parser")
        result = source.find_all(attrs={'dir': 'ltr', 'class': ['t0']})
        self.current_url = self.api_url
        return result[0].text

    def returnCurrentUrl(self):
        return self.current_url


class aesirTranslator:

    def compareText(self, first, second):
        if first == second:
            return True
        else:
            return False


    def processing_finished(self):
        self.showTranslatorWidget()

    def clipboardEventCB(self, *args):
        if len(self.clipboardArray) >= 1:
            self.clipboardArray.append(self.clipboardItem.wait_for_text())
            if self.compareText(self.clipboardArray[0], self.clipboardArray[1]):
                self.ballonNotifier = aesirBallonNotifier();

                if not have_internet():
                    notifySystem("Aesir Translator", "Seems like you are not connected to internet!")
                    return False

                query_text = self.clipboardArray[0]
                result = self.googleTranslator.request("%hl", "%sl", query_text)

                if result is not None:
                    self.indicator.set_status(appindicator.IndicatorStatus.ATTENTION)
                    self.clipboardItem.set_text(result, -1)
                    aesirNotifier("Translate completed!", self.googleTranslator.returnCurrentUrl(), result)

                    GLib.timeout_add_seconds (1, self.processing_finished)
                    self.openTranslatorWidget(query_text,result)
                self.clipboardArray.clear()
            else:
                self.clipboardArray.clear()
        else:
            self.clipboardArray.append(self.clipboardItem.wait_for_text())

    def checkClickEvent(self, status):
        print("abab")

    def startClickEvent(self, status):
        print("anan")

    def clickExitCB(self, widget):
        Gtk.main_quit()

    def clickCheckUpdatesCB(self, widget):
        pass

    def aboutClickEvent(self, widget):
        pass

    def settingClickEvent(self, widget):
        pass

    def activatorClickEvent(self, widget):
        self.service_status ^=True
        status_text = "Aesir Translator Service Now: ";

        if self.service_status:
            status_text += "Enable"
            self.indicator.set_status(appindicator.IndicatorStatus.ATTENTION)
        else:
            status_text += "Disable"
            self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        notifySystem("Aesir Translator", status_text)

    def __init__(self):
        self.init()

    def init(self):

        self.clipboardArray = []
        self.clipboardIndex = 0
        self.service_status = True
        self.googleTranslator = aesirGoogleTranslator(CONF_FILE_INSTANCE["googletranslatelink"])
        self.clipboardItem = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.clipboardItem.connect('owner-change', self.clipboardEventCB)
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID,
                                                    returnIconPath("indicator-disable"),
                                                    appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_attention_icon(returnIconPath("indicator-active"))
        self.indicator.set_status(appindicator.IndicatorStatus.ATTENTION)
        self.indicator.set_menu(self.getIndicatorMenu())
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def translateButtonCB(self,x, *args):
        translator = aesirGoogleTranslator(CONF_FILE_INSTANCE["googletranslatelink"])
        resultTextBuffer = self.originalView.get_buffer()
        start_iter = resultTextBuffer.get_start_iter()
        end_iter = resultTextBuffer.get_end_iter()
        text = resultTextBuffer.get_text(start_iter, end_iter, True)
        result = translator.request("%hl", "%sl", text)
        if result is not None:
            TextBuffer = Gtk.TextBuffer()

            TextBuffer.set_text(result)

            self.resultView.set_buffer( TextBuffer)



    def saveButtonCB(self , *args):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.translatorWindow,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
        dialog.set_current_name("Result.txt")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:


                fd = open(dialog.get_filename(), 'w+')
                resultTextBuffer = self.resultView.get_buffer()
                start_iter = resultTextBuffer.get_start_iter()
                end_iter = resultTextBuffer.get_end_iter()
                text = resultTextBuffer.get_text(start_iter, end_iter, True)
                fd.write(text)
                fd.close()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()
        print("Hello World!")

    def exitButtonCB(self , *args):
        self.translatorWindow.destroy()

    def showTranslatorWidget(self):
        self.translatorWindow.show_all()

    def openTranslatorWidget(self, original, translated):
        builder = Gtk.Builder()
        builder.add_from_file("resultViewer.glade")

        originalTextBuffer = Gtk.TextBuffer()
        translatedTextBuffer = Gtk.TextBuffer()
        originalTextBuffer.set_text(original)
        translatedTextBuffer.set_text(translated)

        self.originalView = builder.get_object("originalTextView")
        self.originalView.set_buffer(originalTextBuffer)

        self.resultView = builder.get_object("resultTextView")
        self.resultView.set_buffer(translatedTextBuffer)

        self.translatorWindow = builder.get_object("resultViewer")
        self.translatorWindow.set_size_request(400,400 )
        self.translatorWindow.set_keep_above(True)

        self.translatorWindow.set_title("Aesir Translator Dialog")
        builder.connect_signals(self)

    def getIndicatorMenu(self):
        mainmenu = Gtk.Menu()

        for item in CONF_FILE_INSTANCE["IndicatorAPPMenuItems"]:
            properties = item.split("=")

            if "Gtk.MenuItem" == properties[0]:
                if properties[1] == "NONE":
                    menu_item = Gtk.MenuItem()
                    self.indicator.set_secondary_activate_target(menu_item)
                else:
                    menu_item = Gtk.MenuItem(properties[1])

                menu_item.connect(properties[3], getattr(self, properties[2]))
                mainmenu.append(menu_item)

            elif "Gtk.CheckMenuItem" == properties[0]:
                menu_item = Gtk.CheckMenuItem(properties[1])
                menu_item.connect(properties[3], getattr(self, properties[2]))
                menu_item.set_active(properties[4] == "True")
                mainmenu.append(menu_item)

        mainmenu.show_all()
        return mainmenu







def main():
    aesirTranslator()
    Gtk.main()


if __name__ == "__main__":
    main()
