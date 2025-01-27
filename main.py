import tkinter as tk
from tkinter import ttk, filedialog
import cv2
from PIL import Image, ImageTk
from receive import Receiver
from send import Sender


class CameraManager:
    def __init__(self):
        self.capture = None
        self.is_capturing = False
        self.current_user = None  # 'send' or 'receive'

    def start_camera(self):
        if self.capture is None:
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                print("Error: Could not open camera")
                return False
        self.is_capturing = True
        return True

    def stop_camera(self):
        self.is_capturing = False
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def get_frame(self):
        if self.capture is not None and self.is_capturing:
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.flip(frame, 1)  # הפוך את התמונה במישור האופקי
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return frame
        return None

    def set_current_user(self, user):
        if self.current_user != user:
            self.current_user = user
            self.stop_camera()


class SendTab:
    def __init__(self, parent, camera_manager):
        self.frame = ttk.Frame(parent)
        self.backend = Sender()
        self.camera_manager = camera_manager

        # Initialize UI elements as instance attributes within __init__
        self.button_containers = None
        self.browse_button = None
        self.startover_button = None
        self.status_label = None
        self.qr_label = None
        self.camera_label = None

        self._initialize_ui()

    def _initialize_ui(self):
        self.button_containers = ttk.Frame(self.frame)
        self.button_containers.pack(pady=10)

        self.browse_button = ttk.Button(
            self.button_containers,
            text="Select File",
            command=self.browse_file
        )
        self.browse_button.pack(side='left', padx=5)  # ממורכז למעלה ומשמאל

        self.startover_button = ttk.Button(
            self.button_containers,
            text="Start Over",
            command=self.startover,
            state=tk.DISABLED
        )
        self.startover_button.pack(side='left', padx=5)  # ממורכז למעלה ומשמאל

        self.status_label = ttk.Label(
            self.frame,
            text=self.backend.status
        )
        self.status_label.pack(side='top', pady=10)

        self.qr_label = ttk.Label(self.frame)
        self.qr_label.pack(expand=True, side='left', padx=10)

        self.camera_label = ttk.Label(self.frame)
        self.camera_label.pack(side='left', padx=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")]
        )
        if not file_path:
            return

        initial_qr = self.backend.start_transfer(file_path)
        if initial_qr:
            self.display_qr(initial_qr)
            self.start_capture()
            self.browse_button.config(text=f"Selected File: {self.backend.file.name}", state=tk.DISABLED)
            self.startover_button.config(state=tk.NORMAL)

    def update_frame(self):
        if self.camera_manager.is_capturing:
            frame = self.camera_manager.get_frame()
            if frame is not None:
                self.display_camera_frame(frame)

                # העבר לבאקאנד רק את הפריים לניתוח
                qr_data = self.backend.analyze_frame(frame)

                if qr_data:
                    next_qr = self.backend.handle_confirmation(qr_data)
                    if next_qr:
                        self.display_qr(next_qr)
                    elif self.backend.transfer_completed:
                        self.stop_capture()

                self.status_label.config(text=self.backend.status)

                self.frame.after(100, self.update_frame)

    def display_qr(self, qr_image):
        qr_image = qr_image.resize((400, 400))
        photo = ImageTk.PhotoImage(qr_image)
        self.qr_label.config(image=photo)
        self.qr_label.image = photo

    def display_camera_frame(self, frame):
        image = Image.fromarray(frame)
        image = image.resize((533, 400))
        photo = ImageTk.PhotoImage(image)
        self.camera_label.config(image=photo)
        self.camera_label.image = photo

    def startover(self):
        self.stop_capture()
        self.qr_label.config(image="")
        self.browse_button.config(text="Select File", state=tk.NORMAL)
        self.startover_button.config(state=tk.DISABLED)
        self.backend = Sender()
        self.status_label.config(text=self.backend.status)

    def start_capture(self):
        self.camera_manager.set_current_user('send')
        if self.camera_manager.start_camera():
            self.update_frame()

    def stop_capture(self):
        self.camera_manager.stop_camera()
        self.camera_label.config(image="")

    def get_frame(self):
        return self.frame


class ReceiveTab:
    def __init__(self, parent, camera_manager):
        self.frame = ttk.Frame(parent)
        self.backend = Receiver()
        self.camera_manager = camera_manager

        # Initialize instance attributes
        self.status_label = None
        self.confirmation_qr_label = None
        self.video_label = None
        self.startover_button = None

        self._initialize_ui()

    def _initialize_ui(self):
        self.status_label = ttk.Label(
            self.frame,
            text=self.backend.status,
            font=('Arial', 12)
        )
        self.status_label.pack(side='top', pady=10)

        self.confirmation_qr_label = ttk.Label(self.frame)
        self.confirmation_qr_label.pack(side='left', padx=10)

        self.video_label = ttk.Label(self.frame)
        self.video_label.pack(expand=True, side='left')

        self.startover_button = ttk.Button(
            self.frame,
            text="Start Over",
            command=self.startover,
            state=tk.DISABLED
        )

    def update_frame(self):
        if not self.camera_manager.is_capturing:
            return

        frame = self.camera_manager.get_frame()
        if frame is not None:
            processed_frame, qr_data = self.backend.analyze_frame(frame)
            if qr_data is not None:
                print(qr_data)

            display_frame = processed_frame if processed_frame is not None else frame
            display_frame = cv2.resize(display_frame, (533, 400))
            photo = ImageTk.PhotoImage(Image.fromarray(display_frame))
            self.video_label.config(image=photo)
            self.video_label.image = photo

            if qr_data:
                confirmation_qr = self.backend.get_confirmation_qr()
                if confirmation_qr:
                    confirmation_qr = confirmation_qr.resize((400, 400))
                    confirmation_photo = ImageTk.PhotoImage(confirmation_qr)
                    self.confirmation_qr_label.config(image=confirmation_photo)
                    self.confirmation_qr_label.image = confirmation_photo

            self.status_label.config(text=self.backend.status)

            if self.backend.transfer_completed:
                self.stop_capture()
                self.startover_button.config(state=tk.NORMAL)
                self.startover_button.pack(side='top', pady=10, ipadx=10)

                save_folder_path = self.browse_save_folder_path()
                self.backend.current_file.filename = save_folder_path + "\\" + self.backend.current_file.filename
                self.backend.current_file.save_to_file()
                self.status_label.config(text=self.backend.status)
                self.backend.transfer_completed = False

        self.frame.after(100, self.update_frame)

    @staticmethod
    def browse_save_folder_path():
        save_folder_path = filedialog.askdirectory()
        if not save_folder_path:
            return

        return save_folder_path

    def startover(self):
        self.backend = Receiver()
        self.start_capture()
        self.startover_button.pack_forget()
        self.startover_button.config(state=tk.DISABLED)

    def start_capture(self):
        self.camera_manager.set_current_user('receive')
        if self.camera_manager.start_camera():
            # self.start_button.config(state='disabled')
            # self.stop_button.config(state='normal')
            self.update_frame()

    def stop_capture(self):
        self.camera_manager.stop_camera()
        # self.start_button.config(state='normal')
        # self.stop_button.config(state='disabled')
        self.video_label.config(image='')
        self.confirmation_qr_label.config(image='')

    def get_frame(self):
        return self.frame


class QRScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Application")
        self.camera_manager = CameraManager()

        # Initialize UI elements as attributes
        self.notebook = None
        self.send_tab = None
        self.receive_tab = None

        self.initialize_ui()

    def initialize_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)

        self.send_tab = SendTab(self.notebook, self.camera_manager)
        self.receive_tab = ReceiveTab(self.notebook, self.camera_manager)

        self.notebook.add(self.send_tab.get_frame(), text='Send')
        self.notebook.add(self.receive_tab.get_frame(), text='Receive')

        # Bind focus change instead of tab change

        self.send_tab.get_frame().bind(
            "<FocusIn>",
            lambda event: self.send_tab.start_capture()
            if str(self.send_tab.startover_button['state']) == tk.NORMAL
            else None)
        self.receive_tab.get_frame().bind(
            "<FocusIn>",
            lambda event: self.receive_tab.start_capture()
            if str(self.receive_tab.startover_button['state']) == tk.DISABLED
            else None)

        self.send_tab.get_frame().bind("<FocusOut>", lambda event: self.send_tab.stop_capture())
        self.receive_tab.get_frame().bind("<FocusOut>", lambda event: self.receive_tab.stop_capture())


def main():
    root = tk.Tk()
    root.geometry("1200x650")
    QRScannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
