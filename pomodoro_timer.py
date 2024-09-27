from datetime import datetime, timedelta
import threading
import time
import random
import pyttsx3

class PomodoroTimer:
    def __init__(self):
        self.work_duration = 25  # minutes
        self.break_duration = 5  # minutes
        self.current_end_time = None
        self.is_work_session = True
        self.timer_thread = None
        self.speaker = pyttsx3.init()

    def set_work_duration(self, minutes):
        self.work_duration = minutes

    def set_break_duration(self, minutes):
        self.break_duration = minutes

    def start_pomodoro(self):
        self.current_end_time = datetime.now() + timedelta(minutes=self.work_duration)
        self.is_work_session = True
        if self.timer_thread:
            self.timer_thread.join()
        self.timer_thread = threading.Thread(target=self.run_timer)
        self.timer_thread.start()

    def stop_pomodoro(self):
        self.current_end_time = None

    def run_timer(self):
        while self.current_end_time:
            time_remaining = self.current_end_time - datetime.now()
            if time_remaining.total_seconds() <= 0:
                if self.is_work_session:
                    self.is_work_session = False
                    self.current_end_time = datetime.now() + timedelta(minutes=self.break_duration)
                    self.provide_motivation()
                else:
                    self.is_work_session = True
                    self.current_end_time = datetime.now() + timedelta(minutes=self.work_duration)
                    self.provide_motivation()
            else:
                time.sleep(60)  # Update every minute

    def get_status(self):
        if self.current_end_time:
            status = "Work session" if self.is_work_session else "Break session"
            return f"{status}. Time remaining: {self.get_time_remaining()}"
        else:
            return "Pomodoro is not active."

    def provide_motivation(self):
        motivational_quotes = [
            "Stay focused and stay positive!",
            "Consistency is the key to success!",
            "Small progress is still progress.",
            "Keep going, you're doing great!",
            "Remember why you started this journey."
        ]
        self.speak(random.choice(motivational_quotes))

    def get_time_remaining(self):
        if self.current_end_time:
            time_remaining = self.current_end_time - datetime.now()
            minutes, seconds = divmod(int(time_remaining.total_seconds()), 60)
            return f"{minutes:02d}:{seconds:02d}"
        else:
            return "00:00"

    def speak(self, text):
        self.speaker.say(text)
        self.speaker.runAndWait()