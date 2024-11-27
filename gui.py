import os
import threading
import tkinter as tk
from time import sleep
from tkinter import ttk, messagebox

import requests

from core import add_metronome_to_audio, restore_backup, parse_general_section


class MetronomeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.progress_label = None
        self.progress_bar = None
        self.progress_frame = None
        self.restore_button = None
        self.close_program_button = None
        self.apply_button = None
        self.gain_slider = None
        self.music_slider = None
        self.map_label = None
        self.header = None
        self.title("osu! Metronome")
        self.configure(bg="#1e1e1e")
        self.geometry("500x425")
        self.iconbitmap("./assets/icon/icon.ico")
        self.osu_path = None
        self.audio_file = None
        self.gain_db = 0
        self.music_db = 0
        self.is_editor = False

        self.create_widgets()

        threading.Thread(target=self.auto_detect_map, daemon=True).start()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 10), padding=5)

        self.header = tk.Label(
            self,
            text="osu! Metronome",
            font=("Helvetica", 16, "bold"),
            bg="#1e1e1e",
            fg="#ffffff",
        )
        self.header.pack(pady=10)

        self.map_label = tk.Label(
            self,
            text="No map detected",
            font=("Helvetica", 12),
            bg="#1e1e1e",
            fg="#bbbbbb",
            wraplength=400,
        )
        self.map_label.pack(pady=5)

        tk.Label(
            self,
            text="Metronome Gain (dB) ↓ (higher is louder)",
            font=("Helvetica", 10),
            bg="#1e1e1e",
            fg="#ffffff",
        ).pack(pady=5)

        self.gain_slider = tk.Scale(
            self,
            from_=-10,
            to=10,
            orient="horizontal",
            bg="#3e3e3e",
            fg="#ffffff",
            troughcolor="#555555",
            highlightthickness=0,
        )
        self.gain_slider.set(self.gain_db)
        self.gain_slider.pack(pady=5)

        tk.Label(
            self,
            text="Music Gain (dB) ↓ (higher is louder)",
            font=("Helvetica", 10),
            bg="#1e1e1e",
            fg="#ffffff",
        ).pack(pady=5)

        self.music_slider = tk.Scale(
            self,
            from_=-50,
            to=0,
            orient="horizontal",
            bg="#3e3e3e",
            fg="#ffffff",
            troughcolor="#555555",
            highlightthickness=0,
        )
        self.music_slider.set(self.music_db)
        self.music_slider.pack(pady=5)

        button_frame = tk.Frame(self, bg="#1e1e1e")
        button_frame.pack(pady=10)

        self.apply_button = tk.Button(
            button_frame,
            text="Apply Metronome",
            bg="#4CAF50",
            fg="#ffffff",
            activebackground="#45a049",
            command=self.apply_metronome,
            width=15,
        )
        self.apply_button.grid(row=0, column=0, padx=5)

        self.restore_button = tk.Button(
            button_frame,
            text="Restore Backup",
            bg="#FF9800",
            fg="#ffffff",
            activebackground="#FB8C00",
            command=self.restore_map,
            width=15,
        )
        self.restore_button.grid(row=0, column=1, padx=5)

        self.close_program_button = tk.Button(
            self,
            text="Close Program",
            bg="#f44336",
            fg="#ffffff",
            activebackground="#e53935",
            command=self.quit,
            width=15,
        )
        self.close_program_button.pack(pady=10)

        self.progress_frame = tk.Frame(self, bg="#1e1e1e")
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode="determinate", length=300)
        self.progress_label = tk.Label(self.progress_frame, text="Progress: 0%", bg="#1e1e1e", fg="#ffffff")
        self.progress_frame.pack(pady=10)
        self.progress_bar.pack(side="left", padx=5)
        self.progress_label.pack(side="left")
        self.progress_frame.pack_forget()

    def auto_detect_map(self):
        """Continuously check for the active map and state."""
        while True:
            try:
                url = "http://127.0.0.1:24050/json"
                response = requests.get(url).json()

                songs_folder = response["settings"]["folders"]["songs"]
                bm_folder = response["menu"]["bm"]["path"]["folder"]
                bm_file = response["menu"]["bm"]["path"]["file"]
                metadata = response["menu"]["bm"]["metadata"]
                song_title = metadata["title"] + " (" + metadata["mapper"] + ")" + " [" + metadata["difficulty"] + "]"
                self.osu_path = os.path.join(songs_folder, bm_folder, bm_file)
                if response["client"] == "lazer":
                    self.map_label.config(
                        text=f"This program won't work on lazer",
                        fg="#ff5252",
                    )
                    return
                else:
                    self.is_editor = response["menu"]["state"] == 1

                self.audio_file = parse_general_section(self.osu_path)
                self.map_label.config(
                    text=f"Loaded: {song_title}",
                    fg="#76ff03" if self.is_editor else "#ff5252",
                )

            except Exception:
                pass

            sleep(2)

    def apply_metronome(self):
        if not self.osu_path:
            messagebox.showerror("Error", "No map detected!")
            return

        if not self.is_editor:
            messagebox.showerror("Error", "You must be in the editor to apply the metronome.")
            return

        self.gain_db = self.gain_slider.get()
        self.music_db = self.music_slider.get()
        audio_path = os.path.join(os.path.dirname(self.osu_path), self.audio_file)

        backup_path = audio_path + ".backup1"
        if os.path.exists(backup_path):
            try:
                restore_backup(audio_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore backup: {str(e)}")
                return

        self.progress_frame.pack(pady=10)
        self.progress_bar["value"] = 0
        self.progress_label["text"] = "Progress: 0%"

        def progress_callback(progress):
            self.progress_bar["value"] = progress * 100
            self.progress_label["text"] = f"Progress: {progress * 100:.2f}%"
            self.update_idletasks()

        def run_metronome():
            try:
                add_metronome_to_audio(
                    self.osu_path,
                    "assets/sounds/strong_beat.wav",
                    "assets/sounds/weak_beat.wav",
                    gain_db=self.gain_db,
                    music_db=self.music_db,
                    progress_callback=progress_callback,
                )
                messagebox.showinfo("Success", "Metronome applied successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.progress_frame.pack_forget()

        threading.Thread(target=run_metronome).start()

    def _process_metronome(self):
        try:
            add_metronome_to_audio(
                self.osu_path,
                "assets/sounds/strong_beat.wav",
                "assets/sounds/weak_beat.wav",
                gain_db=self.gain_slider.get(),
                music_db=self.music_slider.get(),
                progress_callback=self.update_progress,
            )
            messagebox.showinfo("Success", f"Metronome applied to {os.path.basename(self.osu_path)}!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.progress_frame.pack_forget()

    def update_progress(self, progress):
        self.progress_bar["value"] = progress * 100
        self.progress_label.config(text=f"Progress: {progress * 100:.1f}%")

    def restore_map(self):
        if not self.is_editor:
            messagebox.showerror("Error", "You must be in the editor to restore the map!")
            return

        if not self.audio_file:
            messagebox.showerror("Error", "Audio file not found for the loaded map!")
            return

        try:
            audio_path = os.path.join(os.path.dirname(self.osu_path), self.audio_file)
            restore_backup(audio_path)
            messagebox.showinfo("Success", f"Backup restored for {os.path.basename(audio_path)}!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = MetronomeApp()
    app.mainloop()
