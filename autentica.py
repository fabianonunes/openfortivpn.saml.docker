#!/usr/bin/env python3
import signal
import time
from os import path
import argparse
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gtk, WebKit2

parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--cookie', default='SVPNCOOKIE')
args = parser.parse_args()


class Browser:
    window = None
    cookie_manager = None

    def run(self):
        Gtk.init(None)
        self.window = Gtk.Window()
        self.window.set_title("Login")
        self.window.connect("delete-event", Gtk.main_quit)
        self.window.resize(475, 680)

        ctx = WebKit2.WebContext.get_default()
        cookie_storage_path = path.expanduser("~/.cache/openfortivpn-2fa")

        self.cookie_manager = ctx.get_cookie_manager()
        self.cookie_manager.set_accept_policy(WebKit2.CookieAcceptPolicy.ALWAYS)
        self.cookie_manager.set_persistent_storage(
            cookie_storage_path, WebKit2.CookiePersistentStorage.TEXT
        )

        web_view = WebKit2.WebView()
        web_view.set_zoom_level(1.2)
        web_view.connect("load-changed", self.page_changed)
        web_view.load_uri(args.url)

        self.window.add(web_view)

        signal.signal(signal.SIGALRM, self.show)
        signal.alarm(3)

    def show(self, _signun, _stack):
        self.window.show_all()

    def page_changed(self, webview, event=None):
        if event != WebKit2.LoadEvent.FINISHED:
            return
        mr = webview.get_main_resource()
        uri = mr.get_uri()
        self.cookie_manager.get_cookies(uri, None, on_get_cookie)


def on_get_cookie(cookie_manager, result):
    f = cookie_manager.get_cookies_finish(result)
    cookies = {c.name: c.value for c in f}
    if args.cookie in cookies:
        print("{}={}".format(args.cookie, cookies[args.cookie]))
        Gtk.main_quit()


if __name__ == "__main__":
    start = time.time()
    Browser().run()
    Gtk.main()
