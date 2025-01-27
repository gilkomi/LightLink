"""
Slide Structure Overview:
The application uses four types of slides to facilitate the transfer of files via QR codes.
Each slide has a specific purpose and a strict format:

1. **Title Slide ('T')**:
   - **Purpose**: Contains the name of the file being transmitted.
   - **Format**: `T<file_name>`
   - **Length**: Exactly 40 characters (if the file name is shorter, it is padded with spaces).
   - **Constraints**:
     - The file name must be at most 39 characters long.

2. **Confirmation Slide ('C')**:
   - **Purpose**: Acknowledges receipt of a slide or readiness for the next.
   - **Format**: `C<index>`
   - **Length**: 2 characters.
   - **Constraints**:
     - The `index` is stored as a single digit (only the unit digit is used).

3. **Content Slide ('D')**:
   - **Purpose**: Transmits a segment of the file content.
   - **Format**: `D<index><text>`
   - **Length**: Exactly 40 characters (if the content is shorter, it is padded with spaces).
   - **Constraints**:
     - The `index` is stored as a single digit (only the unit digit is used).
     - The `text` segment is up to 38 characters long.

4. **End Slide ('E')**:
   - **Purpose**: Marks the end of the file transmission.
   - **Format**: `EX`
   - **Length**: 2 characters.
   - **Constraints**:
     - The end marker is always `X`.

**General Notes**:
- This structure ensures uniformity, making it easy to parse, validate, and reconstruct files from received slides.
- Each slide's purpose and constraints are critical for maintaining data integrity and facilitating smooth transmission.
"""


class Slide:
    def __init__(self, slide_type, file_name=None, index=None, text=None, end_marker=None):
        """Initializes the slide based on its type and provided parameters, with validation."""
        self.type = slide_type

        match slide_type:
            case 'T':
                # Title slide - Validate file name length.
                if file_name is None:
                    raise ValueError("Title slide requires a file name.")
                if len(file_name) > 39:
                    raise ValueError("File name must be 39 characters or less.")
                self.file_name = file_name

            case 'C':
                # Confirmation slide - Validate that index is provided.
                if index is None:
                    raise ValueError("Content slide requires index.")
                self.index = index % 10  # Store only the unit digit for the index.

            case 'D':
                # Content slide - Validate index and text length.
                if index is None or text is None:
                    raise ValueError("Content slide requires index and text.")
                if len(text) > 38:
                    raise ValueError("Content text must be 38 characters or less.")
                self.index = index % 10  # Store only the unit digit for the index.
                self.text = text

            case 'E':
                # End slide - Validate end marker is correct.
                if end_marker != "X":
                    raise ValueError("End slide requires an end marker 'X'.")
                self.end_marker = end_marker

            case _:
                # Invalid slide type raises an error.
                raise ValueError("Invalid slide type.")

    @classmethod
    def from_string(cls, slide_data):
        """Creates a Slide object from a string based on the slide type."""
        slide_type = slide_data[0]

        if slide_type == 'T':
            # Parse file name from title slide.
            file_name = slide_data[1:].strip()
            return cls(slide_type, file_name=file_name)

        elif slide_type == 'C':
            # Parse index from confirmation slide.
            index = int(slide_data[1])
            return cls(slide_type, index=index)

        elif slide_type == 'D':
            # Parse index and text from content slide.
            index = int(slide_data[1])
            text = slide_data[2:]
            return cls(slide_type, index=index, text=text)

        elif slide_type == 'E':
            # Create end slide with fixed marker.
            return cls(slide_type, end_marker="X")

        else:
            # Handle invalid data format.
            raise ValueError("Invalid slide data format.")

    def to_string(self):
        """Returns a formatted string representation of the slide."""
        if self.type == 'T':
            # Title slide - pad file name to 39 characters.
            return f"T{self.file_name.ljust(39)}"
        elif self.type == 'C':
            # Confirmation slide - format with index.
            return f"C{self.index}"
        elif self.type == 'D':
            # Content slide - pad text to 38 characters.
            return f"D{self.index}{self.text.ljust(38)}"
        elif self.type == 'E':
            # End slide - fixed format.
            return "EX"

    @staticmethod
    def from_text(file_name, content_text):
        """
        Creates a list of Slide objects from file name and content text.
        Includes a title slide, multiple content slides, and an end slide.
        """
        slides = [Slide('T', file_name=file_name)]  # Title slide.

        # Create content slides in segments of 38 characters.
        for i, start in enumerate(range(0, len(content_text), 38)):
            text_slice = content_text[start:start + 38]
            slides.append(Slide('D', index=i, text=text_slice))  # Store unit digit as index.

        slides.append(Slide('E', end_marker="X"))  # End slide.
        return slides
