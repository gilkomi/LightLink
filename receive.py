import cv2
import numpy as np
import qrcode
from pyzbar.pyzbar import decode

import slide


class FileReceiverStatus:
    """Class for managing file reception status messages."""
    READY = "Ready to receive"
    WAITING_FILE = "Waiting for file details"
    RECEIVING = "File: {filename} \nReceiving  slide number {current}"
    # SENDING_CONFIRM = "Sending confirmation for slide {current}/{total}"
    COMPLETED = "Transfer completed \nFile saved in \"{path}\""
    ERROR = "Error: {message}"


class ReceivedFile:
    """Class to manage details of a file being received."""
    def __init__(self, filename):
        self.filename = filename
        self.current_slide_index = 0
        self.content = ""

    def sum_content(self, content):
        """Add received content to the file."""
        self.content += content

    def save_to_file(self):
        """Save the complete file to disk."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write(''.join(self.content))
            return True

        except (PermissionError, FileNotFoundError, IOError):
            return False


class Receiver:
    """Handles QR-based data reception and processing."""
    def __init__(self):
        self.current_file = None
        self.transfer_completed = False
        self._status = FileReceiverStatus.READY
        self.confirmation_qr = None

    @property
    def status(self):
        """Return the current reception status."""
        if self.current_file is None:
            return FileReceiverStatus.WAITING_FILE

        if self.transfer_completed:
            return FileReceiverStatus.COMPLETED.format(
                path=self.current_file.filename)

        return FileReceiverStatus.RECEIVING.format(
            filename=self.current_file.filename,
            current=self.current_file.current_slide_index
        )

    def analyze_frame(self, frame):
        """Analyze a frame for QR codes and return the processed frame and extracted data."""
        try:
            processed_frame = frame.copy()
            qr_data = None

            # Scan for QR codes
            qr_codes = decode(frame)
            for qr in qr_codes:
                # Extract data from the QR code
                qr_data = qr.data.decode()

                # Draw a polygon around the detected QR code
                points = np.array([qr.polygon], np.int32)
                points = points.reshape((-1, 1, 2))
                cv2.polylines(processed_frame, [points], True, (255, 0, 0), 2)

            if qr_data:
                self.confirmation_qr = self.handle_received_data(qr_data)

            return processed_frame, qr_data

        except Exception as e:
            self._status = FileReceiverStatus.ERROR.format(message=str(e))
            return frame, None

    def get_confirmation_qr(self):
        """Return the QR code for the current confirmation."""
        return self.confirmation_qr

    def handle_received_data(self, qr_data):
        """Process data received from a QR code and generate confirmation QR if needed."""
        try:
            data = slide.Slide.from_string(qr_data)

            # Handle file details (promo slide)
            match data.type:
                case 'T':
                    self.current_file = ReceivedFile(
                        filename=data.file_name
                    )
                    self._status = self.status

                    # Generate confirmation QR for the first slide
                    self.confirmation_qr = self.generate_confirmation_qr(self.current_file.current_slide_index)
                    return self.confirmation_qr

                # Handle file content slide
                case 'D':
                    if self.current_file is None:
                        return None

                    slide_index = data.index
                    content = data.text

                    # Verify the slide index is correct and update the file
                    if slide_index == (self.current_file.current_slide_index + 1) % 10:
                        self.current_file.sum_content(content)
                        self.current_file.current_slide_index += 1

                        # Generate confirmation QR for the next slide
                        self.confirmation_qr = self.generate_confirmation_qr(slide_index)
                        return self.confirmation_qr

                # Handle end-of-file slide
                case 'E':
                    if self.current_file is not None:
                        self.transfer_completed = True
                    return None

        except Exception as e:
            self._status = FileReceiverStatus.ERROR.format(message=str(e))

        return None

    @staticmethod
    def generate_confirmation_qr(slide_index):
        """Generate a QR code to confirm receipt of a slide."""
        confirmation_data = slide.Slide('C', index=slide_index)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(confirmation_data.to_string())
        qr.make(fit=True)

        return qr.make_image(fill_color="black", back_color="white").resize((150, 150))
