import ast
import json
import os
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
from kivy.uix.image import Image as KivyImage

try:
    from plyer import stt, filechooser
except Exception:
    stt = filechooser = None

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
    title = "ZOYA AI Assistant"

    def build(self):
        Window.clearcolor = (0.04, 0.05, 0.09, 1)
        self.alarm_time = None
        self.alarm_event = None
        self.todo_list = []
        self.flash_state = False
        self.password = "imran273304"  # Change this in your own private build.
        self.chat_history = []
        self.attached_image = None
        self.api_key = ""
        try:
            with open(os.path.join(self.user_data_dir, "zoya_settings.json"), "r", encoding="utf-8") as settings_file:
                self.api_key = json.load(settings_file).get("gemini_api_key", "")
        except Exception:
            pass

        scroll = ScrollView()
        root = BoxLayout(orientation="vertical", padding=12, spacing=8,
                         size_hint_y=None)
        root.bind(minimum_height=root.setter("height"))
        scroll.add_widget(root)

        root.add_widget(Label(text="[b]ZOYA AI[/b]", markup=True, font_size=30,
                              color=(0.25, 0.7, 1, 1), size_hint_y=None, height=52))
        self.add_button(root, "GEMINI / GOOGLE SEARCH SETTINGS", self.set_api_key, height=42)
        media_row = self.row(root, 42)
        self.add_button(media_row, "ATTACH PHOTO", self.pick_image)
        self.add_button(media_row, "VOICE INPUT", self.voice_input)
        self.add_button(media_row, "GENERATE IMAGE", self.generate_image)
        self.status = Label(
            text="Assalamualaikum! Main Zoya hoon.\nInternet answers need a connection.",
            halign="center", valign="middle", size_hint_y=None, height=72)
        self.status.bind(width=lambda w, v: setattr(w, "text_size", (v - 12, None)))
        root.add_widget(self.status)

        row = self.row(root, 46)
        self.search_input = TextInput(hint_text="Ask ZOYA anything...", multiline=False)
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

    def set_api_key(self, *_):
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        entry = TextInput(text=self.api_key, hint_text="Paste your Google Gemini API key",
                          password=True, multiline=False)
        layout.add_widget(Label(text="Get a key from Google AI Studio. It is stored privately on this device."))
        layout.add_widget(entry)
        popup = Popup(title="ZOYA AI connection", content=layout, size_hint=(0.92, 0.48))
        def save(*_):
            key = entry.text.strip()
            if not key:
                self.set_status("Please enter a Gemini API key.")
                return
            try:
                os.makedirs(self.user_data_dir, exist_ok=True)
                with open(os.path.join(self.user_data_dir, "zoya_settings.json"), "w", encoding="utf-8") as settings_file:
                    json.dump({"gemini_api_key": key}, settings_file)
                self.api_key = key
                self.chat_history = []
                self.set_status("Gemini connected. Ask ZOYA anything.")
                popup.dismiss()
            except Exception as exc:
                self.set_status("Could not save settings: " + str(exc))
        self.add_button(layout, "SAVE & CONNECT", save, height=44)
        popup.open()

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
        self.set_status("ZOYA is thinking...")
        threading.Thread(target=self.fetch_answer, args=(query, self.attached_image), daemon=True).start()

    def fetch_answer(self, query, image_path=None):
        if not self.api_key:
            Clock.schedule_once(lambda dt: self.set_status("Connect Gemini first in settings and add your Google AI Studio API key."), 0)
            return
        answer = ""
        try:
            history = []
            for item in self.chat_history[-8:]:
                history.append({"role": "user", "parts": [{"text": item["user"]}]})
                history.append({"role": "model", "parts": [{"text": item["assistant"]}]})
            parts = [{"text": query}]
            if image_path:
                import base64, mimetypes
                with open(image_path, "rb") as img:
                    raw = img.read()
                mime = mimetypes.guess_type(image_path)[0] or "image/jpeg"
                parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(raw).decode("ascii")}})
            contents = history + [{"role": "user", "parts": parts}]
            payload = {
                "system_instruction": {"parts": [{"text": "You are ZOYA, a helpful, accurate multilingual AI assistant. Reply in the user's language. Explain clearly, admit uncertainty, and use Google Search for current facts. If an image is attached, describe and analyze it carefully."}]},
                "contents": contents,
                "tools": [{"google_search": {}}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1800}
            }
            req = urllib.request.Request(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key},
                method="POST")
            with urllib.request.urlopen(req, timeout=90) as response:
                data = json.loads(response.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                answer = "\n".join(p.get("text", "") for p in candidates[0].get("content", {}).get("parts", []) if p.get("text")).strip()
            grounding = candidates[0].get("groundingMetadata", {}) if candidates else {}
            chunks = grounding.get("groundingChunks", [])
            links = []
            for chunk in chunks:
                web = chunk.get("web", {})
                if web.get("uri"):
                    links.append((web.get("title") or "Source") + ": " + web["uri"])
            if links:
                answer += "\n\nSources:\n" + "\n".join(dict.fromkeys(links)[:5])
            if not answer:
                answer = "Gemini returned no text. Please try again."
            self.chat_history.append({"user": query, "assistant": answer})
            self.chat_history = self.chat_history[-8:]
            self.attached_image = None
        except Exception as exc:
            answer = "AI connection failed: " + str(exc) + "\nCheck API key, internet and Google AI Studio quota."
        Clock.schedule_once(lambda dt: self.set_status("ZOYA: " + answer), 0)

    def pick_image(self, *_):
        if filechooser is None:
            self.set_status("Photo picker is unavailable in this build.")
            return
        try:
            filechooser.open_file(on_selection=self.image_selected, filters=["*.png", "*.jpg", "*.jpeg", "*.webp"])
            self.set_status("Choose a photo. Then type what you want ZOYA to do with it.")
        except Exception as exc:
            self.set_status("Could not open photo picker: " + str(exc))

    def image_selected(self, selection):
        if selection:
            self.attached_image = selection[0]
            self.set_status("Photo attached: " + os.path.basename(self.attached_image) + ". Now ask ZOYA about it.")

    def voice_input(self, *_):
        if stt is None:
            self.set_status("Voice recognition is unavailable in this build. Use the keyboard microphone if your Android keyboard provides it.")
            return
        try:
            stt.start()
            self.set_status("Listening... speak your question.")
        except Exception as exc:
            self.set_status("Voice input failed: " + str(exc))

    def generate_image(self, *_):
        prompt = self.search_input.text.strip()
        if not prompt:
            self.set_status("Type an image description in the question box first.")
            return
        if not self.api_key:
            self.set_status("Add your Gemini API key in settings first.")
            return
        self.set_status("Generating image... this may take a little while.")
        threading.Thread(target=self._generate_image_worker, args=(prompt,), daemon=True).start()

    def _generate_image_worker(self, prompt):
        try:
            payload = {
                "contents": [{"parts": [{"text": "Create a high-quality image based on this prompt: " + prompt}]}],
                "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
            }
            req = urllib.request.Request(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-nano-banana-2.1:generateContent",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key},
                method="POST")
            with urllib.request.urlopen(req, timeout=180) as response:
                data = json.loads(response.read().decode("utf-8"))
            saved = None
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    inline = part.get("inlineData") or part.get("inline_data")
                    if inline and inline.get("data"):
                        import base64
                        mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
                        ext = ".jpg" if "jpeg" in mime else ".png"
                        saved = os.path.join(self.user_data_dir, "zoya_generated" + ext)
                        with open(saved, "wb") as image_file:
                            image_file.write(base64.b64decode(inline["data"]))
                        break
            if saved:
                Clock.schedule_once(lambda dt: self.show_generated_image(saved), 0)
            else:
                Clock.schedule_once(lambda dt: self.set_status("No image was returned. Check model access and API quota."), 0)
        except Exception as exc:
            message = "Image generation failed: " + str(exc)
            Clock.schedule_once(lambda dt: self.set_status(message), 0)

    def show_generated_image(self, path):
        layout = BoxLayout(orientation="vertical", padding=8, spacing=8)
        layout.add_widget(KivyImage(source=path, allow_stretch=True, keep_ratio=True))
        popup = Popup(title="ZOYA generated image", content=layout, size_hint=(0.95, 0.9))
        popup.open()
        self.set_status("Image generated and saved in ZOYA's private app storage.")

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
        message = ("ZOYA AI HELP\n\n"
                   "• Ask: Gemini AI with Google Search grounding. Add your own API key in settings.\n"
                   "• Calculator: supports basic arithmetic and parentheses.\n"
                   "• Call, battery, vibration and torch depend on Android permissions and device support.\n"
                   "• Phone access is limited to features you choose; Android controls permissions.\n"
                   "• Alarm runs only while this app is alive; it is not a system alarm.\n"
                   "• To-do items are temporary and reset when the app restarts.\n"
                   "• Text chat is available; voice recognition is not implemented yet.")
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
