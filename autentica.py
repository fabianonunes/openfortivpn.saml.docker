#!/usr/bin/env python3
import argparse
import os
import signal
from os import path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gio, Gtk, WebKit2  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--host", required=True)
parser.add_argument("--image", default="ghcr.io/fabianonunes/saml-vpn:0.0.2")
args, mass = parser.parse_known_args()


class Browser:
    window = None
    cookie_manager = None
    cookie = None
    container = None

    def run(self):
        Gtk.init(None)
        self.window = Gtk.Window()
        self.window.set_title("VPN")
        self.window.set_default_icon_name("network-vpn")
        self.window.connect("delete-event", self.quit)
        self.window.resize(500, 570)

        ctx = WebKit2.WebContext.get_default()
        cookie_storage_path = path.expanduser("~/.cache/openfortivpn.cookies")

        self.cookie_manager = ctx.get_cookie_manager()
        self.cookie_manager.set_persistent_storage(
            cookie_storage_path, WebKit2.CookiePersistentStorage.TEXT
        )

        web_view = WebKit2.WebView()
        web_view.connect("load-changed", self.page_changed)
        web_view.load_uri(f"https://{args.host}")

        self.window.add(web_view)
        self.window.show_all()

        return self

    def page_changed(self, webview, event=None):
        if event != WebKit2.LoadEvent.FINISHED:
            return
        mr = webview.get_main_resource()
        uri = mr.get_uri()
        self.cookie_manager.get_cookies(uri, None, self.on_receive_cookie)

    def on_receive_cookie(self, cookie_manager, result):
        if self.cookie:
            return
        f = cookie_manager.get_cookies_finish(result)
        cookies = {c.name: c.value for c in f}
        cookie_name = "SVPNCOOKIE"
        if cookie_name in cookies:
            self.cookie = f"{cookie_name}={cookies[cookie_name]}"
            self.connect()

    def quit(self, _a=None, _b=None):
        self.window.destroy()
        Gtk.main_quit()
        while Gtk.events_pending():
            Gtk.main_iteration()
        self.stop_container()

    def stop_container(self):
        self.container.send_signal(signal.SIGTERM)
        self.container.wait()

    def connect(self):
        command = (
            f"pkexec -u {os.getlogin()} docker run --network=host --device=/dev/ppp "
            f"--cap-add=NET_ADMIN --volume /etc/resolv.conf:/etc/resolv.conf --rm "
            f"-i {args.image} {args.host} --svpn-cookie {self.cookie} {' '.join(mass)}"
        )
        self.container = Gio.Subprocess.new(
            command.strip().split(" "), Gio.SubprocessFlags.NONE
        )
        self.container.wait_async(None, self.container_exit)

    def container_exit(self, _process: Gio.Subprocess, _task: Gio.Task):
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Container encerrado inesperadamente. Execute o programa novamente.",
        )
        dialog.set_title("Conexão interrompida")
        dialog.present()
        dialog.run()
        self.quit()


if __name__ == "__main__":
    b = Browser().run()
    signal.signal(signal.SIGINT, b.quit)
    Gtk.main()
