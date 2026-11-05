import datetime
import itertools
import logging
import os
import queue
import threading
import time
import textwrap
import winsound
from fpdf import FPDF
import pyttsx3
import pythoncom

logger = logging.getLogger(__name__)


class Tool:
    def __init__(self):
        self.active_reminders = []          # list of (time_str, task)
        self.triggered_reminders = set()    # reminders that already fired today
        self.reminder_lock = threading.Lock()

        self.speech_queue = queue.PriorityQueue()
        self.speech_sequence = itertools.count()
        self.running = True

        threading.Thread(target=self._process_speech_queue, daemon=True).start()
        threading.Thread(target=self._watch_reminders, daemon=True).start()

    # ------------------------------------------------------------------ speech
    def speak_text(self, text_to_speak: str) -> dict:
        """Public entry point: queue text for background text-to-speech."""
        self._queue_speech(text_to_speak)
        return {"status": "success", "message": "Speech queued successfully"}

    def _queue_speech(self, text, repetitions=1, priority=10, alert=False):
        """Split text into chunks and enqueue one item per chunk per repetition."""
        chunks = textwrap.wrap(text, width=200) or [text]
        for rep in range(repetitions):
            for i, chunk in enumerate(chunks):
                is_alert = alert and rep == 0 and i == 0
                self.speech_queue.put(
                    (priority, next(self.speech_sequence), chunk, is_alert)
                )

    def _process_speech_queue(self):
        """Background worker. Creates a fresh pyttsx3 engine per utterance.

        pyttsx3's SAPI5 driver leaves the engine in a dead state after the
        first runAndWait(), so reusing one engine causes the 2nd+ call to
        go silent. Creating a fresh engine each time fixes this.
        """
        pythoncom.CoInitialize()
        while True:
            _, _, text_to_speak, alert = self.speech_queue.get()
            try:
                if alert:
                    try:
                        winsound.Beep(3000, 1000)
                    except Exception:
                        logger.exception("Reminder alert failed")

                engine = pyttsx3.init()
                try:
                    engine.say(text_to_speak)
                    engine.runAndWait()
                finally:
                    # Release the engine so the next fresh init isn't
                    # blocked by a lingering SAPI handle.
                    del engine
            except Exception:
                logger.exception("Speech playback failed")
            finally:
                self.speech_queue.task_done()

    # --------------------------------------------------------------- reminders
    def add_reminder(self, reminder_time: str, task: str = "Reminder") -> dict:
        try:
            parsed_time = datetime.datetime.strptime(reminder_time, "%H:%M:%S").time()
        except ValueError:
            return {"status": "error",
                    "message": "Reminder time must use HH:MM:SS format."}

        now = datetime.datetime.now()
        scheduled_at = datetime.datetime.combine(now.date(), parsed_time)
        seconds_past_due = (now - scheduled_at).total_seconds()
        trigger_now = 0 <= seconds_past_due <= 60

        with self.reminder_lock:
            if any(t == reminder_time for t, _ in self.active_reminders):
                return {"status": "ignored",
                        "message": f"Reminder for {reminder_time} is already active."}
            self.active_reminders.append((reminder_time, task))
            if trigger_now:
                self.triggered_reminders.add((reminder_time, task))

        if trigger_now:
            self._queue_speech(task, repetitions=3, priority=0, alert=True)
            message = f"Reminder for {reminder_time} was just due, so it is ringing now."
        elif seconds_past_due > 60:
            message = (f"Reminder time {reminder_time} has passed today; "
                       "it will ring tomorrow.")
        else:
            message = f"Reminder successfully set for {reminder_time}"

        return {"status": "success", "message": message,
                "reminder_time": reminder_time, "task": task}

    def remove_reminder(self, reminder_time: str, task: str) -> dict:
        reminder = (reminder_time, task)
        with self.reminder_lock:
            if reminder not in self.active_reminders:
                return {"status": "not_found",
                        "message": "The selected reminder is no longer active."}
            self.active_reminders.remove(reminder)
            self.triggered_reminders.discard(reminder)
        return {"status": "success",
                "message": f"Reminder for {reminder_time} was deleted."}

    def _watch_reminders(self):
        """Poll for reminders whose time passed since the last check.

        Every active reminder fires once per calendar day until removed.
        At each day boundary `triggered_reminders` is cleared so all active
        reminders become eligible again.
        """
        last_checked = datetime.datetime.now() - datetime.timedelta(seconds=1)

        while self.running:
            now = datetime.datetime.now()
            due = []

            with self.reminder_lock:
                # New calendar day → re-arm every active reminder.
                if last_checked.date() != now.date():
                    self.triggered_reminders.clear()

                for reminder in self.active_reminders:
                    if reminder in self.triggered_reminders:
                        continue

                    r_time = datetime.datetime.strptime(reminder[0], "%H:%M:%S").time()
                    # Check both yesterday's and today's slot so a fire is
                    # never missed when the poll straddles midnight.
                    for day in {last_checked.date(), now.date()}:
                        scheduled = datetime.datetime.combine(day, r_time)
                        if last_checked <= scheduled <= now:
                            due.append(reminder)
                            break

                self.triggered_reminders.update(due)

            last_checked = now
            for _, task in due:
                self._queue_speech(task, repetitions=3, priority=0, alert=True)
            time.sleep(0.25)

    # --------------------------------------------------------------- documents
    def create_document(
        self,
        text: str,
        file_format: str = ".txt",
        filename: str = "my_file",
        directory: str = r"C:\Users\Faisal Imtiaz\Documents",
    ) -> dict:
        if not file_format.startswith("."):
            file_format = f".{file_format}"

        try:
            os.makedirs(directory, exist_ok=True)
            full_filepath = os.path.join(directory, f"{filename}{file_format}")

            if file_format in (".txt", ".md"):
                with open(full_filepath, "w", encoding="utf-8") as f:
                    f.write(text)
            elif file_format == ".pdf":
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("helvetica", size=12)
                pdf.multi_cell(0, 10, text)
                pdf.output(full_filepath)
            else:
                return {"status": "error",
                        "message": f"Unsupported format '{file_format}'. Use .txt, .md, or .pdf."}

            return {"status": "success",
                    "message": f"Successfully created: {full_filepath}",
                    "filename": full_filepath}
        except Exception as e:
            return {"status": "error", "message": f"Error creating file: {e}"}