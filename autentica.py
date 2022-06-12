#!/usr/bin/env python3
import argparse
import signal
import time
from os import path
from subprocess import run

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gtk, WebKit2  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--host", required=True)
parser.add_argument("--image", default="localhost/openfortivpn-2fa")
parser.add_argument("--cookie", default="SVPNCOOKIE")
args = parser.parse_args()


class Browser:
    window = None
    cookie_manager = None
    cookie = None

    def run(self):
        Gtk.init(None)
        self.window = Gtk.Window()
        self.window.set_title("Login")
        self.window.connect("delete-event", self.quit)
        self.window.resize(450, 560)

        ctx = WebKit2.WebContext.get_default()
        cookie_storage_path = path.expanduser("~/.cache/openfortivpn-2fa")

        self.cookie_manager = ctx.get_cookie_manager()
        self.cookie_manager.set_accept_policy(WebKit2.CookieAcceptPolicy.ALWAYS)
        self.cookie_manager.set_persistent_storage(
            cookie_storage_path, WebKit2.CookiePersistentStorage.TEXT
        )

        web_view = WebKit2.WebView()
        web_view.connect("load-changed", self.page_changed)
        web_view.load_uri(f"https://{args.host}")

        self.window.add(web_view)

        signal.signal(signal.SIGALRM, self.show)
        signal.alarm(2)

        return self

    def show(self, _signun, _stack):
        self.window.show_all()

    def page_changed(self, webview, event=None):
        if event != WebKit2.LoadEvent.FINISHED:
            return
        mr = webview.get_main_resource()
        uri = mr.get_uri()
        self.cookie_manager.get_cookies(uri, None, self.on_get_cookie)

    def on_get_cookie(self, cookie_manager, result):
        if self.cookie:
            return
        f = cookie_manager.get_cookies_finish(result)
        cookies = {c.name: c.value for c in f}
        if args.cookie in cookies:
            self.cookie = f"{args.cookie}={cookies[args.cookie]}"
            self.quit()

    def quit(self, _a=None, _b=None):
        self.window.destroy()
        Gtk.main_quit()
        while Gtk.events_pending():
            Gtk.main_iteration()

    def connect(self):
        command = (
            "sudo docker run --name vpn --network=host --device=/dev/ppp --cap-add=NET_ADMIN "
            f"--volume /etc/resolv.conf:/etc/resolv.conf --rm -i {args.image} {args.host} "
            f"--svpn-cookie {self.cookie}"
        )
        run(command.split(" "))


if __name__ == "__main__":
    start = time.time()
    b = Browser().run()
    Gtk.main()
    b.connect()
