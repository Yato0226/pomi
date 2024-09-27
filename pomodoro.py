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
        self.waiting_for_duration = False

        # Event to stop the timer thread
        self.stop_event = threading.Event()

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
                    if self.waiting_for_duration:
                        # Handle duration response
                        time_parts = command.split()
                        if len(time_parts) == 2:
                            value = int(time_parts[0])
                            unit = time_parts[1]
                            if unit == "minutes":
                                self.work_duration = value
                                self.start_pomodoro()
                                self.waiting_for_duration = False
                                self.chatbox.insert(tk.END, f"AI: Pomodoro started! Work for {value} minutes.\n")
                                self.chatbox.yview(tk.END)
                            elif unit == "seconds":
                                self.work_duration = value // 60
                                self.start_pomodoro()
                                self.waiting_for_duration = False
                                self.chatbox.insert(tk.END, f"AI: Pomodoro started! Work for {value // 60} minutes.\n")
                                self.chatbox.yview(tk.END)
                            elif unit == "hours":
                                self.work_duration = value * 60
                                self.start_pomodoro()
                                self.waiting_for_duration = False
                                self.chatbox.insert(tk.END, f"AI: Pomodoro started! Work for {value * 60} minutes.\n")
                                self.chatbox.yview(tk.END)
                            else:
                                self.speak("Sorry, I didn't understand the time unit.")
                                self.chatbox.insert(tk.END, "AI: Sorry, I didn't understand the time unit.\n")
                                self.chatbox.yview(tk.END)
                        else:
                            self.speak("Sorry, I didn't catch the work duration.")
                            self.chatbox.insert(tk.END, "AI: Sorry, I didn't catch the work duration.\n")
                            self.chatbox.yview(tk.END)
                    else:
                        response = self.process_command(command)
                        self.chatbox.insert(tk.END, f"AI: {response}\n")
                        self.chatbox.yview(tk.END)
                except sr.UnknownValueError:
                    continue  # Retry listening
                except sr.RequestError:
                    self.chatbox.insert(tk.END, "AI: Error with speech recognition service.\n")
                    self.chatbox.yview(tk.END)

    def process_command(self, command):
        if "start" in command:
            if "for" in command:
                time_string = command.split("for ")[1]
                time_parts = time_string.split()
                if len(time_parts) == 2:
                    value = int(time_parts[0])
                    unit = time_parts[1]
                    if unit == "minutes":
                        self.work_duration = value
                        self.start_pomodoro()
                        return f"Pomodoro started! Work for {value} minutes."
                    elif unit == "seconds":
                        self.work_duration = value // 60
                        self.start_pomodoro()
                        return f"Pomodoro started! Work for {value // 60} minutes."
                    elif unit == "hours":
                        self.work_duration = value * 60
                        self.start_pomodoro()
                        return f"Pomodoro started! Work for {value * 60} minutes."
                    else:
                        return "Sorry, I didn't understand the time unit."
                else:
                    return "Sorry, I didn't catch the work duration."
            else:
                self.waiting_for_duration = True
                self.speak("How long would you like to work for?")
                return "Waiting for duration..."
        elif "stop" in command:
            self.stop_pomodoro()
            return "Pomodoro stopped."
        else:
            return "Sorry, I didn't understand the command."

    def start_pomodoro(self):
        self.is_work_session = True
        self.stop_event.clear()  # Clear the stop event
        self.current_end_time = datetime.now() + timedelta(minutes=self.work_duration)
        self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.timer_thread.start()

    def stop_pomodoro(self):
        self.is_work_session = False
        self.stop_event.set()  # Set the stop event to stop the timer thread
        if self.timer_thread is not None:
            self.timer_thread.join()  # Wait for the thread to finish

    def update_timer(self):
        while self.is_work_session and not self.stop_event.is_set():
            time_remaining = self.current_end_time - datetime.now()
            if time_remaining.total_seconds() <= 0:
                self.is_work_session = False
                self.speak("Time's up!")
                break
            minutes, seconds = divmod(time_remaining.seconds, 60)
            self.chatbox.insert(tk.END, f"Time remaining: {minutes}:{seconds:02}\n")
            self.chatbox.yview(tk.END)
            time.sleep(1)
    
    def speak(self, text):
        self.speaker.say(text)
        self.speaker.runAndWait()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    bot = PomiBot()
    bot.run()