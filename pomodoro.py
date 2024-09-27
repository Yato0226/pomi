import tkinter as tk
from tkinter import messagebox
import threading
import speech_recognition as sr
import pyaudio
from datetime import datetime, timedelta
import time
import random
import pyttsx3

class PomiBot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pomi Bot")

        # Chat interface
        self.chatbox = tk.Text(self.root, height=15, width=50)
        self.chatbox.pack(pady=10)

        # Initialize PomodoroTimer
        self.work_duration = 25  # minutes
        self.break_duration = 5  # minutes
        self.current_end_time = None
        self.is_work_session = True
        self.timer_thread = None
        self.speaker = pyttsx3.init()

        # Speech recognizer
        self.recognizer = sr.Recognizer()

        # Start listening in a separate thread
        threading.Thread(target=self.listen_for_wake_word, daemon=True).start()

    def listen_for_wake_word(self):
        self.chatbox.insert(tk.END, "Listening for wake word 'Pomi'...\n")
        self.chatbox.yview(tk.END)
        
        microphone = sr.Microphone()  # Create a new Microphone object
        
        while True:
            with microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                    command = self.recognizer.recognize_google(audio).lower()
                    self.chatbox.insert(tk.END, f"Detected: {command}\n")
                    self.chatbox.yview(tk.END)

                    # Apply a simple mapping for similar words
                    if self.is_wake_word(command):
                        self.chatbox.insert(tk.END, "Wake word detected. Asking for help...\n")
                        self.chatbox.yview(tk.END)
                        self.speak("What can I help you with?")
                        self.listen_for_commands()
                except sr.WaitTimeoutError:
                    continue  # Retry listening
                except sr.UnknownValueError:
                    continue  # Retry listening
                except sr.RequestError:
                    self.chatbox.insert(tk.END, "AI: Error with speech recognition service.\n")
                    self.chatbox.yview(tk.END)

    def is_wake_word(self, command):
        # Check for the exact wake word or similar variants
        wake_word_variants = ["pomi", "omi", "pommie","mommy","tommy"]
        return any(variant in command for variant in wake_word_variants)

    def listen_for_commands(self):
        self.chatbox.insert(tk.END, "Listening for commands...\n")
        self.chatbox.yview(tk.END)
        
        microphone = sr.Microphone()  # Create a new Microphone object
        
        while True:
            with microphone as source:
                try:
                    audio = self.recognizer.listen(source, timeout=10)
                    command = self.recognizer.recognize_google(audio).lower()
                    self.chatbox.insert(tk.END, f"Voice Command: {command}\n")
                    self.chatbox.yview(tk.END)
                    response = self.process_command(command)
                    self.chatbox.insert(tk.END, f"AI: {response}\n")
                    self.chatbox.yview(tk.END)
                except sr.WaitTimeoutError:
                    continue  # Retry listening
                except sr.UnknownValueError:
                    self.chatbox.insert(tk.END, "AI: Sorry, I did not understand that.\n")
                    self.chatbox.yview(tk.END)
                except sr.RequestError:
                    self.chatbox.insert(tk.END, "AI: Error with speech recognition service.\n")
                    self.chatbox.yview(tk.END)

    def process_command(self, command):
        if "start" in command:
            self.start_pomodoro()
            return f"Pomodoro started! Work for {self.work_duration} minutes."
        elif "stop" in command:
            self.stop_pomodoro()
            return "Pomodoro stopped."
        elif "status" in command:
            return self.get_status()
        elif "motivation" in command:
            self.provide_motivation()
            return "Here's a motivational quote for you!"
        elif "time" in command:
            return f"Time remaining: {self.get_time_remaining()}"
        elif "set work time" in command:
            minutes = self.extract_minutes(command, "work")
            if minutes:
                self.work_duration = minutes
                return f"Work duration set to {minutes} minutes."
            return "Sorry, I didn't catch the work duration."
        elif "set break time" in command:
            minutes = self.extract_minutes(command, "break")
            if minutes:
                self.break_duration = minutes
                return f"Break duration set to {minutes} minutes."
            return "Sorry, I didn't catch the break duration."
        else:
            return "I didn't understand that command. Try 'start', 'stop', 'status', 'motivation', 'time', 'set work time', or 'set break time'."

    def extract_minutes(self, command, duration_type):
        import re
        pattern = re.compile(rf" set {duration_type} time to (\d+) minutes?")
        match = pattern.search(command)
        if match:
            return int(match.group(1))
        return None

    def speak(self, text):
        self.speaker.say(text)
        self.speaker.runAndWait()

    def start_pomodoro(self):
        self.current_end_time = datetime.now() + timedelta(minutes=self.work_duration)
        self.is_work_session = True
        if self.timer_thread:
            self.timer_thread.join()
        self.timer_thread = threading.Thread(target=self.run_timer)
        self.timer_thread.start()
        self.speak(f"Pomodoro started! Work for {self.work_duration} minutes.")

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
                minutes, seconds = divmod(int(time_remaining.total_seconds()), 60)
                self.chatbox.insert(tk.END, f"Time remaining: {minutes:02d}:{seconds:02d}\n")
                self.chatbox.yview(tk.END)
                time.sleep(1)  # Update every second

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

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    bot = PomiBot()
    bot.run()