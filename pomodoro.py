import tkinter as tk
from tkinter import messagebox
import threading
import speech_recognition as sr
import pyaudio
from pomodoro_timer import PomodoroTimer

class PomiBot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pomi Bot")

        # Chat interface
        self.chatbox = tk.Text(self.root, height=15, width=50)
        self.chatbox.pack(pady=10)

        # Initialize PomodoroTimer
        self.timer = PomodoroTimer()

        # Speech recognizer and text-to-speech
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Start listening in a separate thread
        threading.Thread(target=self.listen_for_wake_word, daemon=True).start()

    def listen_for_wake_word(self):
        self.chatbox.insert(tk.END, "Listening for wake word 'Pomi'...\n")
        self.chatbox.yview(tk.END)
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=10)
                    command = self.recognizer.recognize_google(audio).lower()
                    if "pomi" in command:
                        self.chatbox.insert(tk.END, "Wake word detected. Asking for help...\n")
                        self.chatbox.yview(tk.END)
                        self.speak("What can I help you with?")
                        self.listen_for_commands()
                except sr.WaitTimeoutError:
                    continue  # Retry listening
                except sr.UnknownValueError:
                    continue  # Retry listening
                except sr.RequestError:
                    self.chatbox.insert(tk.END, "AI: Sorry, there was an error with the speech recognition service.\n")
                    self.chatbox.yview(tk.END)

    def listen_for_commands(self):
        self.chatbox.insert(tk.END, "Listening for commands...\n")
        self.chatbox.yview(tk.END)
        with self.microphone as source:
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=10)
                    command = self.recognizer.recognize_google(audio).lower()
                    self.chatbox.insert(tk.END, f"Voice Command: {command}\n")
                    response = self.process_command(command)
                    self.chatbox.insert(tk.END, f"AI: {response}\n")
                    self.chatbox.yview(tk.END)
                except sr.WaitTimeoutError:
                    continue  # Retry listening
                except sr.UnknownValueError:
                    self.chatbox.insert(tk.END, "AI: Sorry, I did not understand that.\n")
                    self.chatbox.yview(tk.END)
                except sr.RequestError:
                    self.chatbox.insert(tk.END, "AI: Sorry, there was an error with the speech recognition service.\n")
                    self.chatbox.yview(tk.END)

    def process_command(self, command):
        if "start" in command:
            self.timer.start_pomodoro()
            return "Pomodoro started! Work for 25 minutes."
        elif "stop" in command:
            self.timer.stop_pomodoro()
            return "Pomodoro stopped."
        elif "status" in command:
            return self.timer.get_status()
        elif "motivation" in command:
            return self.timer.provide_motivation()
        elif "time" in command:
            return self.timer.get_time_remaining()
        elif "set work time" in command:
            minutes = self.extract_minutes(command, "work")
            if minutes:
                self.timer.set_work_duration(minutes)
                return f"Work duration set to {minutes} minutes."
            return "Sorry, I didn't catch the work duration."
        elif "set break time" in command:
            minutes = self.extract_minutes(command, "break")
            if minutes:
                self.timer.set_break_duration(minutes)
                return f"Break duration set to {minutes} minutes."
            return "Sorry, I didn't catch the break duration."
        else:
            return "I didn't understand that command. Try 'start', 'stop', 'status', 'motivation', 'time', 'set work time', or 'set break time'."

    def extract_minutes(self, command, duration_type):
        import re
        pattern = re.compile(rf"set {duration_type} time to (\d+) minutes?")
        match = pattern.search(command)
        if match:
            return int(match.group(1))
        return None

    def speak(self, text):
        self.timer.speak(text)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    bot = PomiBot()
    bot.run()
