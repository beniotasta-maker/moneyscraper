import json
import os
import threading
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(APP_DIR, "app_settings.json")
STORE = JsonStore(SETTINGS_PATH)


def load_setting(key, default=""):
    if STORE.exists(key):
        return STORE.get(key).get("value", default)
    return default


def save_setting(key, value):
    STORE.put(key, value=value)


def parse_links(page_url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    seen = set()

    for anchor in soup.find_all("a", href=True):
        text = anchor.get_text(" ", strip=True) or "[No Text]"
        href = urljoin(page_url, anchor["href"])
        key = (text, href)
        if key in seen:
            continue
        seen.add(key)
        links.append({"text": text, "href": href})

    return links


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        root.add_widget(Label(text="Trend Cashout", font_size="28sp", size_hint_y=None, height=dp(48)))
        root.add_widget(Label(text="Scrape pages, inspect links, and send cashout actions to your backend from one app.", halign="left", valign="middle"))

        buttons = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        buttons.bind(minimum_height=buttons.setter("height"))

        scrape_button = Button(text="Scrape Links", size_hint_y=None, height=dp(52))
        cashout_button = Button(text="Cashout Center", size_hint_y=None, height=dp(52))
        settings_button = Button(text="App Settings", size_hint_y=None, height=dp(52))

        scrape_button.bind(on_release=lambda *_: self.manager.transition_to("scrape"))
        cashout_button.bind(on_release=lambda *_: self.manager.transition_to("cashout"))
        settings_button.bind(on_release=lambda *_: self.manager.transition_to("settings"))

        buttons.add_widget(scrape_button)
        buttons.add_widget(cashout_button)
        buttons.add_widget(settings_button)

        root.add_widget(buttons)
        self.add_widget(root)


class ScrapeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        root.add_widget(Label(text="Scrape Links", font_size="24sp", size_hint_y=None, height=dp(42)))
        self.url_input = TextInput(text="https://example.com", multiline=False, hint_text="Enter a URL")
        self.status_label = Label(text="Ready", size_hint_y=None, height=dp(28))
        self.results_label = Label(text="", markup=True, halign="left", valign="top", size_hint_y=None)
        self.results_label.bind(texture_size=self._sync_label_height)

        button_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        run_button = Button(text="Fetch Links")
        back_button = Button(text="Back")
        run_button.bind(on_release=lambda *_: self.start_fetch())
        back_button.bind(on_release=lambda *_: self.manager.transition_to("home"))
        button_row.add_widget(run_button)
        button_row.add_widget(back_button)

        root.add_widget(self.url_input)
        root.add_widget(button_row)
        root.add_widget(self.status_label)

        scroll = ScrollView()
        scroll.add_widget(self.results_label)
        root.add_widget(scroll)
        self.add_widget(root)

    def _sync_label_height(self, *_):
        self.results_label.height = max(self.results_label.texture_size[1], dp(200))
        self.results_label.text_size = (self.width - dp(32), None)

    def start_fetch(self):
        url = self.url_input.text.strip()
        if not url.startswith(("http://", "https://")):
            self.status_label.text = "Please include http:// or https://"
            return

        self.status_label.text = "Loading..."
        self.results_label.text = ""
        threading.Thread(target=self._fetch_links, args=(url,), daemon=True).start()

    def _fetch_links(self, url):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
            )
        }
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            links = parse_links(url, response.text)
            message = [f"Found {len(links)} links\n"]
            for item in links[:100]:
                message.append(f"- {item['text']}\n  {item['href']}")
        except Exception as exc:
            message = [f"Fetch failed: {exc}"]

        def update_ui(_dt):
            self.status_label.text = "Done"
            self.results_label.text = "\n\n".join(message)

        Clock.schedule_once(update_ui)


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        root.add_widget(Label(text="App Settings", font_size="24sp", size_hint_y=None, height=dp(42)))
        root.add_widget(Label(text="These values are stored locally on the device.", size_hint_y=None, height=dp(24)))

        self.backend_url_input = TextInput(text=load_setting("backend_url", "http://10.0.2.2:8000"), multiline=False, hint_text="Backend URL")
        self.api_token_input = TextInput(text=load_setting("api_token", ""), multiline=False, password=True, hint_text="API token")

        buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        save_button = Button(text="Save")
        back_button = Button(text="Back")
        save_button.bind(on_release=lambda *_: self.save_settings())
        back_button.bind(on_release=lambda *_: self.manager.transition_to("home"))
        buttons.add_widget(save_button)
        buttons.add_widget(back_button)

        self.status_label = Label(text="", size_hint_y=None, height=dp(28))

        root.add_widget(Label(text="Backend URL", size_hint_y=None, height=dp(24)))
        root.add_widget(self.backend_url_input)
        root.add_widget(Label(text="API Token", size_hint_y=None, height=dp(24)))
        root.add_widget(self.api_token_input)
        root.add_widget(buttons)
        root.add_widget(self.status_label)
        self.add_widget(root)

    def save_settings(self):
        save_setting("backend_url", self.backend_url_input.text.strip())
        save_setting("api_token", self.api_token_input.text.strip())
        self.status_label.text = "Saved"


class CashoutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        root.add_widget(Label(text="Cashout Center", font_size="24sp", size_hint_y=None, height=dp(42)))
        root.add_widget(Label(text="Cashouts are routed through your backend so the APK does not need your Stripe secret key.", halign="left", valign="middle"))

        self.amount_input = TextInput(text="1499.00", multiline=False, hint_text="Amount")
        self.method_input = TextInput(text="standard", multiline=False, hint_text="standard or instant")
        self.description_input = TextInput(text="Trend Data Payout", multiline=False, hint_text="Description")
        self.status_label = Label(text="Ready", size_hint_y=None, height=dp(28))
        self.response_label = Label(text="", markup=True, halign="left", valign="top", size_hint_y=None)
        self.response_label.bind(texture_size=self._sync_label_height)

        button_grid = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        balance_button = Button(text="Check Balance")
        cashout_button = Button(text="Request Cashout")
        back_button = Button(text="Back")
        balance_button.bind(on_release=lambda *_: self._run_backend_action("balance"))
        cashout_button.bind(on_release=lambda *_: self._run_backend_action("cashout"))
        back_button.bind(on_release=lambda *_: self.manager.transition_to("home"))
        button_grid.add_widget(balance_button)
        button_grid.add_widget(cashout_button)
        button_grid.add_widget(back_button)

        root.add_widget(self.amount_input)
        root.add_widget(self.method_input)
        root.add_widget(self.description_input)
        root.add_widget(button_grid)
        root.add_widget(self.status_label)

        scroll = ScrollView()
        scroll.add_widget(self.response_label)
        root.add_widget(scroll)
        self.add_widget(root)

    def _sync_label_height(self, *_):
        self.response_label.height = max(self.response_label.texture_size[1], dp(200))
        self.response_label.text_size = (self.width - dp(32), None)

    def _backend_base(self):
        return load_setting("backend_url", "http://10.0.2.2:8000").rstrip("/")

    def _api_token(self):
        return load_setting("api_token", "")

    def _run_backend_action(self, action):
        threading.Thread(target=self._backend_worker, args=(action,), daemon=True).start()

    def _backend_worker(self, action):
        base_url = self._backend_base()
        if not base_url:
            Clock.schedule_once(lambda _dt: self._set_response("Set a backend URL in App Settings first."))
            return

        headers = {}
        token = self._api_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            if action == "balance":
                response = requests.get(f"{base_url}/balance", headers=headers, timeout=20)
            else:
                payload = {
                    "amount": self.amount_input.text.strip(),
                    "method": self.method_input.text.strip() or "standard",
                    "description": self.description_input.text.strip() or "Trend Data Payout",
                }
                response = requests.post(f"{base_url}/cashout", json=payload, headers=headers, timeout=20)

            response.raise_for_status()
            body = response.json()
            text = json.dumps(body, indent=2)
        except Exception as exc:
            text = f"Request failed: {exc}"

        Clock.schedule_once(lambda _dt: self._set_response(text))

    def _set_response(self, text):
        self.status_label.text = "Done"
        self.response_label.text = text


class TrendCashoutApp(App):
    def build(self):
        self.title = "Trend Cashout"
        manager = ScreenManager(transition=SlideTransition(duration=0.2))
        manager.transition_to = self._transition_to.__get__(manager, ScreenManager)
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(ScrapeScreen(name="scrape"))
        manager.add_widget(CashoutScreen(name="cashout"))
        manager.add_widget(SettingsScreen(name="settings"))
        return manager

    def _transition_to(self, screen_name):
        self.current = screen_name


if __name__ == "__main__":
    TrendCashoutApp().run()
