import qrcode
import slide
from pyzbar.pyzbar import decode

# Constants for slide sizes
SLIDE_SIZE = 40  # Total size of each slide
CONTENT_SIZE = SLIDE_SIZE - 2  # Size available for actual content


class FileTransferStatus:
    """Helper class to manage file transfer statuses."""
    READY = "Ready to transfer"
    WAITING_PROMO = "Waiting for receiver to acknowledge file details"
    SENDING = "Sending slide {current}/{total}"
    WAITING_CONFIRM = "Waiting for confirmation of slide {current}/{total}"
    COMPLETED = "Transfer completed"
    ERROR = "Error: {message}"


class File:
    """
    Represents the file being transferred, managing its name, content,
    and logic for dividing content into slides.
    """
    def __init__(self, path):
        self.path = path
        self.name = self.get_name_from_path()  # Extract the file name from the path
        with open(self.path, 'r', encoding='utf-8') as file:
            self.content = file.read()  # Read the file content

        # Calculate the number of slides required, rounding up
        self.amount_of_slides = ((len(self.content) + 2 * SLIDE_SIZE) // SLIDE_SIZE) + \
                                (((len(self.content) + SLIDE_SIZE) % SLIDE_SIZE) > 0)
        self.slide_index = 0  # Current slide index

    def get_name_from_path(self):
        """
        Extracts the file name from the file path.
        Assumes the path separator is '/'.
        """
        for i in range(len(self.path)):
            if self.path[-i] == '/':
                return self.path[-i + 1:]

    def get_title_slide_content(self):
        """Returns the title slide containing file metadata."""
        return slide.Slide('T', file_name=self.name)

    def get_next_content_slide(self):
        """
        Returns the next content slide based on the current index.
        Increments the slide index for the next call.
        """
        self.slide_index += 1

        if self.slide_index >= self.amount_of_slides:
            return None  # No more slides available

        # Slice the content for the current slide
        return slide.Slide('D', index=self.slide_index,
                           text=self.content[(self.slide_index - 1) * CONTENT_SIZE: self.slide_index * CONTENT_SIZE])

    @staticmethod
    def get_end_slide():
        """Returns the end slide indicating transfer completion."""
        return slide.Slide('E', end_marker='X')


class Sender:
    """
    Handles the logic for sending slides in a file transfer,
    including status updates, QR code generation, and frame analysis.
    """
    def __init__(self):
        self.file = None
        self.current_slide_index = 0  # Index of the current slide being sent
        self.transfer_completed = False  # Whether the transfer is complete
        self.waiting_for_confirmation = False  # Waiting for receiver's confirmation
        self._status = FileTransferStatus.READY  # Default status

    @property
    def status(self):
        """
        Returns the current transfer status.
        Dynamically updates based on the state of the transfer.
        """
        if self.file is None:
            return FileTransferStatus.READY

        if self.transfer_completed:
            return FileTransferStatus.COMPLETED

        if self.waiting_for_confirmation:
            return FileTransferStatus.WAITING_CONFIRM.format(
                current=self.current_slide_index + 1,
                total=self.file.amount_of_slides
            )

        return FileTransferStatus.SENDING.format(
            current=self.current_slide_index + 1,
            total=self.file.amount_of_slides
        )

    def start_transfer(self, file_path):
        """
        Initializes a new file transfer by creating a file object
        and preparing the title slide.
        """
        try:
            self.file = File(file_path)
            self.current_slide_index = 0
            self.transfer_completed = False
            self.waiting_for_confirmation = True

            # Generate QR code for the title slide
            title_data = self.file.get_title_slide_content()
            return self.generate_qr_code(title_data.to_string())

        except Exception as e:
            self._status = FileTransferStatus.ERROR.format(message=str(e))
            return None

    def analyze_frame(self, frame):
        """
        Decodes a frame to extract QR code data.
        Returns the decoded data or None if decoding fails.
        """
        try:
            decoded = decode(frame)
            qr_data = decoded[0].data.decode('utf-8') if decoded else None
            return qr_data

        except Exception as e:
            self._status = FileTransferStatus.ERROR.format(message=str(e))
            return None

    def handle_confirmation(self, confirmation_data):
        """
        Handles receiver's confirmation, generates the next QR code,
        and determines whether the transfer is complete.
        """
        try:
            confirmation = slide.Slide.from_string(confirmation_data)

            if confirmation.type == 'C' and \
                    confirmation.index == self.current_slide_index % 10:

                self.current_slide_index += 1
                self.waiting_for_confirmation = False

                if self.current_slide_index >= self.file.amount_of_slides - 1:
                    # Send end slide if all slides are sent
                    self.transfer_completed = True
                    next_slide = self.file.get_end_slide()
                    return self.generate_qr_code(next_slide.to_string())

                # Send next content slide
                next_slide = self.file.get_next_content_slide()
                self.waiting_for_confirmation = True
                return self.generate_qr_code(next_slide.to_string())

        except Exception as e:
            self._status = FileTransferStatus.ERROR.format(message=str(e))

        return None

    def generate_qr_code(self, data):
        """
        Generates a QR code from the provided data.
        Returns a resized QR image.
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            return qr.make_image(fill_color="black", back_color="white").resize((200, 200))

        except Exception as e:
            self._status = FileTransferStatus.ERROR.format(message=str(e))
            return None
