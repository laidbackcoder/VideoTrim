import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
import subprocess
import os
import cv2
from PIL import Image, ImageTk


class VideoTrimmerApp(ttk.Window):
    def __init__(self):
        super().__init__(themename='darkly')
        self.title("Video Trimmer")
        self.geometry("1000x400")

        # Variables for slider values
        self.start_time = tk.DoubleVar(value=0)
        self.end_time = tk.DoubleVar()

        # Button to start encoding
        self.encode_button = tk.Button(
            self, text="Start Encoding", command=self.trim_video
        )
        self.encode_button.pack(side=tk.RIGHT, anchor='n')

        # Button to choose file
        self.choose_button = tk.Button(
            self, text="Choose File", command=self.choose_file
        )
        self.choose_button.pack(side=tk.RIGHT, anchor='n')

        # Frame for start preview
        self.start_frame_group = tk.Frame(self)
        self.start_frame_group.pack(side="left", padx=50)

        # Buttons to adjust start time
        self.start_dec_button = tk.Button(
            self.start_frame_group, text="<", command=self.decrease_start_time
        )
        self.start_dec_button.grid(row=0, column=0)

        self.start_time_label = tk.Label(
            self.start_frame_group, text="Start: 0:00"
            )
        self.start_time_label.grid(row=0, column=1)

        self.start_slider = ttk.Scale(
            self.start_frame_group,
            from_=0,
            to=0,
            length=220,
            orient="horizontal",
            variable=self.start_time,
            command=self.load_previews,
        )
        self.start_slider.grid(row=1, column=0, columnspan=3, pady=10)

        self.start_inc_button = tk.Button(
            self.start_frame_group, text=">", command=self.increase_start_time
        )
        self.start_inc_button.grid(row=0, column=2)

        self.preview_label_start = tk.Label(self.start_frame_group)
        self.preview_label_start.grid(row=2, column=0, columnspan=3)

        # Frame for end preview
        self.end_frame_group = tk.Frame(self)
        self.end_frame_group.pack(side="right", padx=50)

        # Buttons to adjust end time
        self.end_dec_button = tk.Button(
            self.end_frame_group, text="<", command=self.decrease_end_time
        )
        self.end_dec_button.grid(row=0, column=0)

        self.end_time_label = tk.Label(self.end_frame_group, text="End: 0:00")
        self.end_time_label.grid(row=0, column=1)

        self.end_slider = ttk.Scale(
            self.end_frame_group,
            from_=0,
            to=0,
            length=220,
            orient="horizontal",
            variable=self.end_time,
            command=self.load_previews,
        )
        self.end_slider.grid(row=1, column=0, columnspan=3, pady=10)

        self.end_inc_button = tk.Button(
            self.end_frame_group, text=">", command=self.increase_end_time
        )
        self.end_inc_button.grid(row=0, column=2)

        self.preview_label_end = tk.Label(self.end_frame_group)
        self.preview_label_end.grid(row=2, column=0, columnspan=3)

        # Video capture objects
        self.video_capture_start = None
        self.video_capture_end = None
        self.total_frames = 0

    def choose_file(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[
                ('Video files', '*.mp4'),
                ('Video files', '*.m4v'),
                ('Video files', '*.ts')]
        )
        if self.file_path:
            self.video_capture_start = cv2.VideoCapture(self.file_path)
            self.video_capture_end = cv2.VideoCapture(self.file_path)
            self.total_frames = int(
                self.video_capture_start.get(cv2.CAP_PROP_FRAME_COUNT)
            )
            video_length = int(
                self.total_frames / self.video_capture_start.get(
                    cv2.CAP_PROP_FPS
                    )
            )
            self.start_time.set(0)
            self.end_time.set(video_length)
            self.start_slider.config(from_=0, to=video_length)
            self.end_slider.config(from_=0, to=video_length)
            self.load_previews()

    def load_previews(self):
        start_time_sec = int(self.start_time.get())
        end_time_sec = int(self.end_time.get())

        self.video_capture_start.set(
            cv2.CAP_PROP_POS_MSEC, start_time_sec * 1000
            )
        success_start, frame_start = self.video_capture_start.read()
        if success_start:
            frame_start = Image.fromarray(
                cv2.cvtColor(frame_start, cv2.COLOR_BGR2RGB)
                )
            frame_start = frame_start.resize((300, 169))
            frame_start = ImageTk.PhotoImage(frame_start)
            self.preview_label_start.configure(image=frame_start)
            self.preview_label_start.image = frame_start
            self.start_time_label.config(
                text=f"Start: {start_time_sec//60}:{start_time_sec%60:02d}"
            )

        self.video_capture_end.set(cv2.CAP_PROP_POS_MSEC, end_time_sec * 1000)
        success_end, frame_end = self.video_capture_end.read()
        if success_end:
            frame_end = Image.fromarray(
                cv2.cvtColor(frame_end, cv2.COLOR_BGR2RGB)
                )
            frame_end = frame_end.resize((300, 169))
            frame_end = ImageTk.PhotoImage(frame_end)
            self.preview_label_end.configure(image=frame_end)
            self.preview_label_end.image = frame_end
            self.end_time_label.config(
                text=f"End: {end_time_sec//60}:{end_time_sec%60:02d}"
            )

    def decrease_start_time(self):
        current_start_time = self.start_time.get()
        if current_start_time > 0:
            self.start_time.set(current_start_time - 1)
        self.load_previews()

    def increase_start_time(self):
        current_start_time = self.start_time.get()
        self.start_time.set(current_start_time + 1)
        self.load_previews()

    def decrease_end_time(self):
        current_end_time = self.end_time.get()
        if current_end_time > 0:
            self.end_time.set(current_end_time - 1)
        self.load_previews()

    def increase_end_time(self):
        current_end_time = self.end_time.get()
        self.end_time.set(current_end_time + 1)
        self.load_previews()

    def trim_video(self):
        start_time_sec = int(self.start_time.get())
        end_time_sec = int(self.end_time.get())

        # Get filename without extension
        output_file_name, output_file_extension = os.path.splitext(
            os.path.basename(self.file_path)
            )
        output_path = os.path.splitext(
            os.path.dirname(self.file_path)
            )[0]
        output_file = (
            f'{output_path}/{output_file_name}'
            f'_trimmed{output_file_extension}'
        )

        # Execute FFMPEG command for trimming
        command = (
            f'ffmpeg -i "{self.file_path}" '
            f'-ss {start_time_sec} -to {end_time_sec} '
            f'-c:v copy -c:a copy "{output_file}" -y'
        )
        subprocess.call(command, shell=True)

        messagebox.showinfo("Success", "Video trimmed successfully!")


if __name__ == "__main__":
    app = VideoTrimmerApp()
    app.mainloop()
