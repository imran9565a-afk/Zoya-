import ast
import json
import math
import operator as op
import threading
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

try:
    from plyer import battery, call, flash, vibrator, tts
except Exception:
    battery = call = flash = vibrator = tts = None

# Only explicitly permitted arithmetic AST nodes are evaluated.
_BINARY = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
           ast.Div: op.truediv, ast.FloorDiv: op.floordiv,
           ast.Mod: op.mod, ast.Pow: op.pow}
_UNARY = {ast.UAdd: op.pos, ast.USub: op.neg}
MAX_EXPR_LEN = 120
MAX_ABS_RESULT = 10 ** 100

def safe_calculate(expression):
    if not expression or len(expression) > MAX_EXPR_LEN:
        raise ValueError("Expression is empty or too long")
    tree = ast.parse(expression, mode="eval")
    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Exponent too large")
            value = _BINARY[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
            value = _UNARY[type(node.op)](visit(node.operand))
        else:
            raise ValueError("Unsupported expression")
        if not isinstance(value, (int, float)) or not math.isfinite(value) or abs(value) > MAX_ABS_RESULT:
            raise ValueError("Result out of range")
        return value
    return visit(tree)

class ZoyaApp(App):
    title = "ZOYA Smart Assistant"

    def build(self):
        Window.clearcolor = (0.04, 0.05, 0.09, 1)
        self.alarm_time = None
        self.alarm_event = None
        self.todo_list = []
        self.flash_state = False
        self.password = "imran273304"  # Change this in your own private build.

        scroll = ScrollView()
        root = BoxLayout(orientation="vertical", padding=12, spacing=8,
                         size_hint_y=None)
        root.bind(minimum_height=root.setter("height"))
        scroll.add_widget(root)

        root.add_widget(Label(text="[b]ZOYA[/b]", markup=True, font_size=28,
                              color=(0.25, 0.7, 1, 1), size_hint_y=None, height=48))
        self.status = Label(
            text="Assalamualaikum! Main Zoya hoon.\nInternet answers need a connection.",
            halign="center", valign="middle", size_hint_y=None, height=72)
        self.status.bind(width=lambda w, v: setattr(w, "text_size", (v - 12, None)))
        root.add_widget(self.status)

        row = self.row(root, 46)
        self.search_input = TextInput(hint_text="Ask a question...", multiline=False)
        self.search_input.bind(on_text_validate=self.perform_search)
        row.add_widget(self.search_input)
        self.add_button(row, "ASK", self.perform_search, 78)

        row = self.row(root, 44)
        self.phone_input = TextInput(hint_text="Phone number", multiline=False,
                                     input_filter="int")
        row.add_widget(self.phone_input)
        self.add_button(row, "CALL", self.make_call, 78)

        row = self.row(root, 42)
        self.add_button(row, "BATTERY", self.get_battery_status)
        self.add_button(row, "VIBRATE", self.trigger_vibrate)
        self.add_button(row, "TORCH", self.toggle_flashlight)

        row = self.row(root, 42)
        self.add_button(row, "YOUTUBE", lambda *_: self.open_url("https://www.youtube.com"))
        self.add_button(row, "GOOGLE", lambda *_: self.open_url("https://www.google.com"))
        self.add_button(row, "INSTAGRAM", lambda *_: self.open_url("https://www.instagram.com"))

        self.add_button(root, "HASHTAG & BIO HELPER", self.open_insta_popup, height=42)
        self.calc_input = TextInput(hint_text="Calculator: 300*500/1000 or (25+5)*4",
                                    multiline=False, size_hint_y=None, height=46)
        self.calc_input.bind(on_text_validate=self.calculate)
        root.add_widget(self.calc_input)
        self.add_button(root, "CALCULATE", self.calculate, height=42)

        row = self.row(root, 42)
        self.add_button(row, "TO-DO LIST", self.open_todo_popup)
        self.add_button(row, "SET ALARM", self.open_alarm_popup)
        self.add_button(root, "PASSWORD CHECK", self.open_lock, height=42)
        self.add_button(root, "VOICE / HELP", self.help, height=42)
        return scroll

    def row(self, parent, height):
        box = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=height)
        parent.add_widget(box)
        return box

    def add_button(self, parent, text, callback, width=None, height=None):
        kwargs = {"text": text}
        if width is not None:
            kwargs["size_hint_x"] = None
            kwargs["width"] = width
        if height is not None:
            kwargs["size_hint_y"] = None
            kwargs["height"] = height
        button = Button(**kwargs)
        button.bind(on_press=callback)
        parent.add_widget(button)
        return button

    def set_status(self, message):
        self.status.text = str(message)

    def speak(self, message):
        if tts is not None:
            try:
                tts.speak(message[:250])
            except Exception:
                pass

    def open_url(self, url):
        try:
            webbrowser.open(url)
            self.set_status("Opening website: " + url)
        except Exception as exc:
            self.set_status("Could not open website: " + str(exc))

    def open_insta_popup(self, *_):
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        topic = TextInput(hint_text="Topic (e.g. fitness, shayari)", multiline=False)
        kind = TextInput(hint_text="Optional bio idea", multiline=False)
        result = TextInput(text="", readonly=True, multiline=True)
        layout.add_widget(Label(text="Instagram content helper"))
        layout.add_widget(topic)
        layout.add_widget(kind)
        layout.add_widget(result)
        popup = Popup(title="ZOYA Insta Helper", content=layout, size_hint=(0.9, 0.7))
        def generate(*_):
            words = topic.text.strip().replace("#", "").split()
            if not words:
                result.text = "Please enter a topic."
                return
            tag = "".join(words)
            result.text = ("Suggested tags (check relevance before posting):\n"
                           + " ".join("#" + t for t in [tag, tag+"Life", tag+"Daily",
                                                       "Trending", "ExplorePage"])
                           + "\n\nBio idea: " + (kind.text.strip() or "Creating moments, one post at a time."))
        self.add_button(layout, "GENERATE", generate, height=42)
        popup.open()

    def make_call(self, *_):
        number = self.phone_input.text.strip()
        if not number or len(number) < 5:
            self.set_status("Enter a valid phone number.")
            return
        if call is None:
            self.set_status("Calling is unavailable: Android Plyer call support is not loaded.")
            return
        try:
            call.makecall(num=number)
            self.set_status("Call action requested for " + number)
        except Exception as exc:
            self.set_status("Call failed. Check permissions and device support: " + str(exc))

    def get_battery_status(self, *_):
        if battery is None:
            self.set_status("Battery status unavailable on this build/device.")
            return
        try:
            info = battery.status
            pct = info.get("percentage", "Unknown")
            charging = info.get("is_charging", False)
            message = f"Battery: {pct}% | " + ("Charging" if charging else "Not charging")
            self.set_status(message)
            self.speak(message)
        except Exception as exc:
            self.set_status("Battery status unavailable: " + str(exc))

    def trigger_vibrate(self, *_):
        if vibrator is None:
            self.set_status("Vibration unavailable on this build/device.")
            return
        try:
            vibrator.vibrate(0.5)
            self.set_status("Vibration requested.")
        except Exception as exc:
            self.set_status("Vibration failed: " + str(exc))

    def toggle_flashlight(self, *_):
        if flash is None:
            self.set_status("Torch unavailable on this build/device.")
            return
        try:
            if self.flash_state:
                flash.off()
                self.flash_state = False
                self.set_status("Torch OFF")
            else:
                flash.on()
                self.flash_state = True
                self.set_status("Torch ON")
        except Exception as exc:
            self.set_status("Torch failed. Check hardware/permissions: " + str(exc))

    def perform_search(self, *_):
        query = self.search_input.text.strip()
        if not query:
            self.set_status("Please type a question first.")
            return
        lower = query.lower()
        if any(greet in lower for greet in ("assalam", "hello", "hi")):
            answer = "Walaikum Assalam! Main Zoya hoon, aapki assistant."
            self.set_status(answer); self.speak(answer); return
        if "who are you" in lower or "kaun ho" in lower:
            answer = "Main Zoya hoon, aapki smart assistant."
            self.set_status(answer); self.speak(answer); return
        if "battery" in lower:
            self.get_battery_status(); return
        if "vibrate" in lower:
            self.trigger_vibrate(); return
        self.set_status("Searching the web for a short answer...")
        threading.Thread(target=self.fetch_answer, args=(query,), daemon=True).start()

    def fetch_answer(self, query):
        answer = ""
        try:
            url = "https://api.duckduckgo.com/?" + urllib.parse.urlencode(
                {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"})
            req = urllib.request.Request(url, headers={"User-Agent": "ZOYA-Assistant/1.0"})
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))
            answer = data.get("AbstractText") or ""
            if not answer:
                for item in data.get("RelatedTopics", []):
                    if isinstance(item, dict) and item.get("Text"):
                        answer = item["Text"]
                        break
            if not answer:
                answer = "No short answer was returned. Try opening Google for more results."
        except Exception:
            answer = "Could not fetch an answer. Check your internet connection and try again."
        Clock.schedule_once(lambda dt: self.set_status("ZOYA: " + answer), 0)

    def calculate(self, *_):
        try:
            result = safe_calculate(self.calc_input.text.strip())
            self.set_status("Result: " + format(result, ".12g"))
        except ZeroDivisionError:
            self.set_status("Cannot divide by zero.")
        except Exception:
            self.set_status("Invalid calculation. Use numbers and + - * / // % ** ( ).")

    def open_todo_popup(self, *_):
        layout = BoxLayout(orientation="vertical", padding=10, spacing=8)
        entry = TextInput(hint_text="Enter a task", multiline=False)
        listing = Label(text="\n".join(self.todo_list) or "No tasks yet.",
                        size_hint_y=None, height=100)
        layout.add_widget(listing)
        layout.add_widget(entry)
        row = self.row(layout, 42)
        def refresh():
            listing.text = "\n".join(self.todo_list) or "No tasks yet."
            listing.height = max(100, 28 * len(self.todo_list))
        def add(*_):
            task = entry.text.strip()
            if task:
                self.todo_list.append("• " + task)
                entry.text = ""
                refresh()
        def clear(*_):
            self.todo_list.clear()
            refresh()
        self.add_button(row, "ADD TASK", add)
        self.add_button(row, "CLEAR ALL", clear)
        Popup(title="To-Do List (temporary)", content=layout, size_hint=(0.9, 0.55)).open()

    def open_alarm_popup(self, *_):
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        entry = TextInput(hint_text="24-hour time HH:MM, e.g. 06:30", multiline=False)
        layout.add_widget(Label(text="In-app alarm only; app must remain open."))
        layout.add_widget(entry)
        popup = Popup(title="Set in-app alarm", content=layout, size_hint=(0.9, 0.4))
        def set_alarm(*_):
            try:
                datetime.strptime(entry.text.strip(), "%H:%M")
                self.alarm_time = entry.text.strip()
                if self.alarm_event:
                    self.alarm_event.cancel()
                self.alarm_event = Clock.schedule_interval(self.check_alarm, 1)
                self.set_status("In-app alarm set for " + self.alarm_time)
                popup.dismiss()
            except ValueError:
                self.set_status("Invalid time. Use HH:MM, e.g. 06:30.")
        self.add_button(layout, "SET ALARM", set_alarm, height=42)
        popup.open()

    def check_alarm(self, _dt):
        if self.alarm_time and datetime.now().strftime("%H:%M") == self.alarm_time:
            message = "Your in-app alarm time has arrived."
            self.set_status(message); self.speak(message)
            self.alarm_time = None
            if self.alarm_event:
                self.alarm_event.cancel()
                self.alarm_event = None

    def open_lock(self, *_):
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        entry = TextInput(hint_text="Enter password", password=True, multiline=False)
        layout.add_widget(entry)
        popup = Popup(title="ZOYA password check", content=layout, size_hint=(0.9, 0.35))
        def check(*_):
            if entry.text == self.password:
                self.set_status("Password accepted.")
                popup.dismiss()
            else:
                self.set_status("Incorrect password.")
        self.add_button(layout, "CHECK PASSWORD", check, height=42)
        popup.open()

    def help(self, *_):
        message = ("ZOYA HELP\n\n"
                   "• Ask: searches DuckDuckGo Instant Answer API; not a full AI chatbot.\n"
                   "• Calculator: supports basic arithmetic and parentheses.\n"
                   "• Call, battery, vibration and torch depend on Android permissions and device support.\n"
                   "• Alarm runs only while this app is alive; it is not a system alarm.\n"
                   "• To-do items are temporary and reset when the app restarts.\n"
                   "• Voice recognition is not implemented in this build.")
        Popup(title="Help", content=Label(text=message), size_hint=(0.9, 0.7)).open()

    def on_stop(self):
        if self.alarm_event:
            self.alarm_event.cancel()
        if self.flash_state and flash is not None:
            try:
                flash.off()
            except Exception:
                pass

if __name__ == "__main__":
    ZoyaApp().run()
