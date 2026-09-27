
import ast
import json
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

# Safe Hardware Imports (Plyer)
try:
    from plyer import battery, call, flash, stt, tts, vibrator
except Exception:
    stt = None
    tts = None
    call = None
    battery = None
    vibrator = None
    flash = None

# PC Fallback TTS
try:
    import pyttsx3

    engine = pyttsx3.init()
except Exception:
    engine = None

# -----------------------------
# SAFE CALCULATOR LOGIC
# -----------------------------
OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}


def safe_calculate(expression):
    def calculate(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Invalid number")

        if isinstance(node, ast.BinOp):
            left = calculate(node.left)
            right = calculate(node.right)
            operator = OPERATORS[type(node.op)]
            return operator(left, right)

        if isinstance(node, ast.UnaryOp):
            return OPERATORS[type(node.op)](calculate(node.operand))

        raise ValueError("Invalid expression")

    tree = ast.parse(expression, mode="eval")
    return calculate(tree.body)


# -----------------------------
# ZOYA SMART ASSISTANT APP
# -----------------------------
class ZoyaApp(App):

    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.08, 1)

        self.password = "imran273304"
        self.alarm_time = None
        self.alarm_event = None
        self.todo_list = []
        self.flash_state = False

        # Main Layout Scrollable
        main_scroll = ScrollView()
        root = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=8,
            size_hint_y=None,
        )
        root.bind(minimum_height=root.setter("height"))

        # App Title
        title = Label(
            text="ZOYA",
            font_size=28,
            bold=True,
            size_hint_y=None,
            height=40,
            color=(0.3, 0.7, 1, 1),
        )
        root.add_widget(title)

        # Greeting & Thought
        self.status = Label(
            text="Assalamualaikum! Main Zoya hoon.\nThought: Always speak the truth and stay kind.",
            font_size=13,
            text_size=(Window.width - 30, None),
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=50,
        )
        root.add_widget(self.status)

        # 1. Ask AI Query Box
        search_box = BoxLayout(
            orientation="horizontal", spacing=5, size_hint_y=None, height=45
        )
        self.search_input = TextInput(
            hint_text="Ask Zoya anything...", multiline=False
        )
        search_btn = Button(text="ASK AI", size_hint_x=None, width=80)
        search_btn.bind(on_press=self.perform_search)
        search_box.add_widget(self.search_input)
        search_box.add_widget(search_btn)
        root.add_widget(search_box)

        # 2. Call & Phone Features
        phone_box = BoxLayout(
            orientation="horizontal", spacing=5, size_hint_y=None, height=45
        )
        self.phone_input = TextInput(
            hint_text="Enter Phone Number...", multiline=False
        )
        call_btn = Button(text="CALL", size_hint_x=None, width=80)
        call_btn.bind(on_press=self.make_call)
        phone_box.add_widget(self.phone_input)
        phone_box.add_widget(call_btn)
        root.add_widget(phone_box)

        # 3. Hardware Shortcuts (Battery, Vibrate, Torch)
        hw_actions = BoxLayout(
            orientation="horizontal", spacing=5, size_hint_y=None, height=40
        )
        bat_btn = Button(text="BATTERY")
        bat_btn.bind(on_press=self.get_battery_status)

        vibe_btn = Button(text="VIBRATE")
        vibe_btn.bind(on_press=self.trigger_vibrate)

        torch_btn = Button(text="TORCH")
        torch_btn.bind(on_press=self.toggle_flashlight)

        hw_actions.add_widget(bat_btn)
        hw_actions.add_widget(vibe_btn)
        hw_actions.add_widget(torch_btn)
        root.add_widget(hw_actions)

        # 4. Quick Web Shortcuts (YouTube, Google, INSTAGRAM)
        web_box = BoxLayout(
            orientation="horizontal", spacing=5, size_hint_y=None, height=40
        )
        yt_btn = Button(text="YOUTUBE")
        yt_btn.bind(on_press=lambda x: webbrowser.open("https://youtube.com"))

        goog_btn = Button(text="GOOGLE")
        goog_btn.bind(
            on_press=lambda x: webbrowser.open("https://google.com")
        )

        insta_btn = Button(text="INSTAGRAM")
        insta_btn.bind(on_press=self.open_instagram)

        web_box.add_widget(yt_btn)
        web_box.add_widget(goog_btn)
        web_box.add_widget(insta_btn)
        root.add_widget(web_box)

        # 5. Instagram AI Tool Button
        insta_tool_btn = Button(
            text="INSTA HASHTAGS & BIO GENERATOR",
            size_hint_y=None,
            height=40,
        )
        insta_tool_btn.bind(on_press=self.open_insta_popup)
        root.add_widget(insta_tool_btn)

        # 6. Calculator
        self.calc_input = TextInput(
            hint_text="Enter calculation e.g. 25*4+10",
            multiline=False,
            size_hint_y=None,
            height=45,
        )
        root.add_widget(self.calc_input)

        calc_button = Button(text="CALCULATE", size_hint_y=None, height=40)
        calc_button.bind(on_press=self.calculate)
        root.add_widget(calc_button)

        # 7. Utilities (To-Do List & Alarm)
        util_box = BoxLayout(
            orientation="horizontal", spacing=5, size_hint_y=None, height=40
        )
        todo_btn = Button(text="TO-DO LIST")
        todo_btn.bind(on_press=self.open_todo_popup)

        alarm_btn = Button(text="SET ALARM")
        alarm_btn.bind(on_press=self.open_alarm_popup)

        util_box.add_widget(todo_btn)
        util_box.add_widget(alarm_btn)
        root.add_widget(util_box)

        # 8. Password Lock, Voice Command, Help
        lock_button = Button(
            text="PASSWORD LOCK", size_hint_y=None, height=40
        )
        lock_button.bind(on_press=self.open_lock)
        root.add_widget(lock_button)

        voice_button = Button(
            text="VOICE COMMAND", size_hint_y=None, height=40
        )
        voice_button.bind(on_press=self.voice_command)
        root.add_widget(voice_button)

        help_button = Button(text="HELP", size_hint_y=None, height=40)
        help_button.bind(on_press=self.help)
        root.add_widget(help_button)

        main_scroll.add_widget(root)
        return main_scroll

    # -------------------------
    # INSTAGRAM FEATURES
    # -------------------------
    def open_instagram(self, instance):
        try:
            # Direct App Intent via Web Browser URL scheme
            webbrowser.open("instagram://app")
            self.status.text = "Instagram App Khola Ja Raha Hai..."
        except Exception:
            webbrowser.open("https://instagram.com")
            self.status.text = "Instagram Web Page Khola Ja Raha Hai..."

    def open_insta_popup(self, instance):
        layout = BoxLayout(orientation="vertical", padding=15, spacing=10)
        topic_input = TextInput(
            hint_text="Topic daalein (e.g. Photography, Fitness, Fashion)...",
            multiline=False,
        )
        gen_btn = Button(text="GENERATE HASHTAGS")

        layout.add_widget(Label(text="ZOYA INSTA HELPER"))
        layout.add_widget(topic_input)
        layout.add_widget(gen_btn)

        popup = Popup(
            title="Instagram Assistant",
            content=layout,
            size_hint=(0.85, 0.45),
        )

        def generate_action(inst):
            topic = topic_input.text.strip()
            if topic:
                tags = f"#{topic} #{topic}Life #{topic}Daily #{topic}Love #Trending #Viral #ExplorePage"
                self.status.text = f"Suggested Hashtags:\n{tags}"
                popup.dismiss()

        gen_btn.bind(on_press=generate_action)
        popup.open()

    # -------------------------
    # HARDWARE & PHONE ACTIONS
    # -------------------------
    def make_call(self, instance):
        num = self.phone_input.text.strip()
        if not num:
            self.status.text = "Kripya call karne ke liye number daalein."
            return

        if call is not None:
            try:
                call.makecall(num=num)
                self.status.text = f"Calling {num}..."
            except Exception as e:
                self.status.text = f"Call Error: {str(e)}"
        else:
            self.status.text = f"Calling {num}..."

    def get_battery_status(self, instance):
        if battery is not None:
            try:
                status = battery.status
                pct = status.get("percentage", "Unknown")
                is_charging = status.get("is_charging", False)
                charging_str = (
                    "Charging" if is_charging else "Not Charging"
                )

                res = f"Battery Level: {pct}% ({charging_str})"
                self.status.text = res
                self.speak(f"Battery level is {pct} percent.")
            except Exception:
                self.status.text = "Battery Status phone par hi mil sakta hai."
        else:
            self.status.text = "Battery module simulation mode me hai."

    def trigger_vibrate(self, instance):
        if vibrator is not None:
            try:
                vibrator.vibrate(0.5)
                self.status.text = "Phone Vibrating..."
            except Exception:
                self.status.text = "Vibration allowed nahi hai."
        else:
            self.status.text = "Vibration triggered."

    def toggle_flashlight(self, instance):
        if flash is not None:
            try:
                if not self.flash_state:
                    flash.on()
                    self.flash_state = True
                    self.status.text = "Torch ON"
                else:
                    flash.off()
                    self.flash_state = False
                    self.status.text = "Torch OFF"
            except Exception:
                self.status.text = "Flashlight feature support nahi karta."
        else:
            self.status.text = "Flashlight triggered."

    # -------------------------
    # TTS SPEAK HELPER
    # -------------------------
    def speak(self, text):
        if tts is not None:
            try:
                tts.speak(text)
            except Exception:
                pass
        elif engine is not None:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass

    # -------------------------
    # AI SEARCH & DIALOGUES
    # -------------------------
    def perform_search(self, instance):
        query = self.search_input.text.strip()
        if not query:
            self.status.text = "Kripya koi sawal likhein."
            return

        lower_q = query.lower()

        if "battery" in lower_q:
            self.get_battery_status(None)
            return
        elif "vibrate" in lower_q:
            self.trigger_vibrate(None)
            return
        elif (
            "assalam" in lower_q
            or "hello" in lower_q
            or "hi" in lower_q
        ):
            res = "Walaikum Assalam! Main Zoya hoon."
            self.status.text = res
            self.speak(res)
            return
        elif "who are you" in lower_q or "kaun ho" in lower_q:
            res = "Main Zoya hoon, aapki Smart AI Assistant."
            self.status.text = res
            self.speak(res)
            return

        self.status.text = "Zoya soch rahi hai..."
        threading.Thread(target=self.fetch_ai_response, args=(query,)).start()

    def fetch_ai_response(self, query):
        try:
            clean_query = (
                query.lower()
                .replace("kya hai", "")
                .replace("kya hota hai", "")
                .replace("what is", "")
                .strip()
            )

            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(clean_query)}&format=json&no_html=1"
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode("utf-8"))
                abstract = data.get("AbstractText", "")

                if abstract:
                    answer = f"Zoya: {abstract}"
                else:
                    related = data.get("RelatedTopics", [])
                    if related and "Text" in related[0]:
                        answer = f"Zoya: {related[0]['Text']}"
                    else:
                        answer = f"Zoya: '{query}' ke baare me jankari khoj li gayi hai."

        except Exception:
            answer = "Zoya: Kripya apna internet connection check karein."

        Clock.schedule_once(lambda dt: self.update_ai_ui(answer), 0)

    def update_ai_ui(self, answer):
        self.status.text = answer
        self.speak(answer[:100])

    def calculate(self, instance):
        expression = self.calc_input.text.strip()
        if not expression:
            self.status.text = "Please enter a calculation."
            return

        try:
            result = safe_calculate(expression)
            self.status.text = f"Result: {result}"
        except Exception:
            self.status.text = "Invalid calculation."

    # -------------------------
    # POPUPS (TO-DO, ALARM, LOCK, HELP)
    # -------------------------
    def open_todo_popup(self, instance):
        layout = BoxLayout(orientation="vertical", padding=15, spacing=10)
        task_input = TextInput(
            hint_text="Enter new task...", multiline=False
        )
        task_label = Label(
            text="\n".join(self.todo_list)
            if self.todo_list
            else "No tasks added yet.",
            font_size=12,
        )

        add_btn = Button(text="ADD TASK")
        clear_btn = Button(text="CLEAR ALL")

        layout.add_widget(Label(text="YOUR TO-DO LIST"))
        layout.add_widget(task_label)
        layout.add_widget(task_input)
        layout.add_widget(add_btn)
        layout.add_widget(clear_btn)

        popup = Popup(
            title="To-Do Manager", content=layout, size_hint=(0.85, 0.6)
        )

        def add_task_action(inst):
            txt = task_input.text.strip()
            if txt:
                self.todo_list.append(f"• {txt}")
                task_label.text = "\n".join(self.todo_list)
                task_input.text = ""

        def clear_task_action(inst):
            self.todo_list.clear()
            task_label.text = "No tasks added yet."

        add_btn.bind(on_press=add_task_action)
        clear_btn.bind(on_press=clear_task_action)
        popup.open()

    def open_alarm_popup(self, instance):
        layout = BoxLayout(orientation="vertical", padding=15, spacing=10)
        alarm_input = TextInput(
            hint_text="Enter time (HH:MM) e.g. 06:30", multiline=False
        )
        set_btn = Button(text="SET ALARM")

        layout.add_widget(Label(text="SET ALARM TIME"))
        layout.add_widget(alarm_input)
        layout.add_widget(set_btn)

        popup = Popup(
            title="Alarm Clock", content=layout, size_hint=(0.85, 0.45)
        )

        def set_alarm_action(inst):
            time_str = alarm_input.text.strip()
            try:
                datetime.strptime(time_str, "%H:%M")
                self.alarm_time = time_str
                self.status.text = f"Alarm set for {self.alarm_time}"

                if self.alarm_event:
                    self.alarm_event.cancel()
                self.alarm_event = Clock.schedule_interval(self.check_alarm, 1)

                popup.dismiss()
            except ValueError:
                self.status.text = "Invalid time format! Use HH:MM"

        set_btn.bind(on_press=set_alarm_action)
        popup.open()

    def check_alarm(self, dt):
        now = datetime.now().strftime("%H:%M")
        if self.alarm_time and now == self.alarm_time:
            msg = "Aapka alarm baj raha hai!"
            self.status.text = msg
            self.speak(msg)
            if self.alarm_event:
                self.alarm_event.cancel()
            self.alarm_time = None

    def open_lock(self, instance):
        layout = BoxLayout(orientation="vertical", padding=15, spacing=10)
        password_input = TextInput(
            hint_text="Enter password", password=True, multiline=False
        )
        unlock_button = Button(text="UNLOCK")

        layout.add_widget(Label(text="ZOYA PASSWORD LOCK"))
        layout.add_widget(password_input)
        layout.add_widget(unlock_button)

        popup = Popup(title="Password", content=layout, size_hint=(0.85, 0.45))

        def check_password(inst):
            if password_input.text == self.password:
                self.status.text = "Password accepted."
                popup.dismiss()
            else:
                self.status.text = "Wrong password."

        unlock_button.bind(on_press=check_password)
        popup.open()

    def voice_command(self, instance):
        if stt is not None:
            try:
                stt.start()
                self.status.text = "Listening... Speak now."
            except Exception as e:
                self.status.text = f"STT Error: {str(e)}"
        else:
            self.status.text = "Voice module active on Android APK build."

    def help(self, instance):
        message = """ZOYA ALL-IN-ONE ASSISTANT

1. Ask AI: Instant answers to any query.
2. Call & Torch: Quick phone controls.
3. Battery & Vibrate: Live status & feedback.
4. Shortcuts: One-tap YouTube, Google & INSTAGRAM access.
5. Instagram Tool: Generate hashtags for posts.
6. Utilities: Safe Calculator, To-Do List, & Alarm.
"""
        Popup(
            title="Zoya Help",
            content=Label(text=message),
            size_hint=(0.9, 0.65),
        ).open()


if __name__ == "__main__":
    ZoyaApp().run()
