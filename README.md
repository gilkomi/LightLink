# LightLink

[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

Transfer files between computers using QR codes - no internet or cables required! LightLink transforms your data into a sequence of QR codes displayed on one screen and captured by another device's camera, enabling seamless file transfer without traditional connectivity methods.

![Demo](assets/demo.gif)

## System Requirements
- Python 3.12 (developed and tested with this version)
- IDE: Tested on JetBrains PyCharm
- Hardware Requirements:
  - Webcam
  - Display screen
  - Operating System: Windows (currently tested only on Windows)

## Important Notes
- Ensure no other applications are using the camera while running LightLink
- Camera access permissions may be required on first run

---

## **Project Overview**
LightLink showcases the use of QR codes for innovative data transfer. By breaking down text files into smaller chunks and encoding them into QR codes, the project demonstrates how visual communication can bypass traditional network protocols.

---

## **Features**
- **Send and Receive Files**: Transfer text files between devices via QR codes.
- **Simple UI**: Easy-to-use interface for both sender and receiver.
- **Real-time Operation**: Processes frames in real-time to ensure smooth communication.

---

## **Technologies Used**
- **Python**: Core programming language.
- **Tkinter**: For creating the user interface.
- **OpenCV**: For handling camera input and QR code detection.

---

## How It Works

### Data Transfer Protocol
LightLink uses a simple yet robust protocol for transferring data through QR codes. Each QR code represents one of four types of frames:

#### Frame Types and Structure
1. **Title Frame (T)**
   - Format: `Tfilename`
   - Length: 39 characters
   - Example: `Tsend_file.txt`
   - Always has index 0
   - Contains the name of the file being transferred

2. **Content Frame (D)**
   - Format: `Dindex|content`
   - Length: 39 characters total
     - Index: 1 character
     - Content: 38 characters
   - Example: `D1abcdefghij0123456789abcdefghij01234567`
   - Sequential index starting from 1

3. **Confirmation Frame (C)**
   - Format: `Cindex`
   - Length: 2 characters
   - Example: `C0`
   - Sent by receiver to confirm successful frame reception

4. **End Frame (E)**
   - Format: `EX`
   - Length: 2 characters
   - Marks the end of transmission

### Frame Sequencing
- Frame indexing starts at 0 (Title frame)
- Content frames use sequential numbers (1,2,3...)
- Each frame maintains a fixed length for reliable transmission

  ---

## **Project Structure**
```
LightLink/
├── src/
│   ├── main.py         # Main application file
│   ├── sender.py       # Back-end logic for the sender
│   ├── receiver.py     # Back-end logic for the receiver
│   ├── slide.py        # Handles chunking data into QR codes
├── assets/
│   ├── qr_example1.png # Example QR code
│   ├── qr_example2.png # Example QR code
├── docs/
│   ├── sequence_diagram.png # Sequence diagram
├── README.md           # Project documentation
├── LICENSE             # Project license
├── requirements.txt    # Python dependencies
```

---

## **Installation**
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/LightLink.git
   cd LightLink
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python src/main.py
   ```

---

## **Usage**
1. Launch the application.
2. Select the "Send" tab to start sending files:
   - Upload a text file.
   - The application will split the file into chunks and display QR codes sequentially.
3. Select the "Receive" tab to start receiving files:
   - Use the camera to scan QR codes.
   - The application will reconstruct the file from the scanned codes.

---

## **Example**
Below is an example of how QR codes are used to transfer files:

![image](https://github.com/user-attachments/assets/967e70d3-dd85-45c3-b69f-1d08138f2b3f)



---

## **Sequence Diagram**
The following diagram illustrates the workflow between the sender and receiver:

```mermaid
sequenceDiagram
    participant U1 as User (Sender)
    participant ST as SendTab
    participant S as Sender
    participant CM as CameraManager
    participant Sl as Slide
    participant R as Receiver
    participant RT as ReceiveTab
    participant U2 as User (Receiver)
    
    %% Initial Setup - Receiver Side (starts first)
    U2->>RT: initialize_ui()
    RT->>CM: start_camera()
    RT->>RT: start_capture()
    Note over RT,RT: Waiting for QR codes
    
    %% Initial Setup - Sender Side
    U1->>ST: browse_file()
    ST->>S: start_transfer(file_path)
    S->>CM: start_camera()
    
    %% Title Slide Process
    S->>S: get_title_slide_content()
    S->>Sl: from_text(filename, "")
    Sl-->>S: title_slide
    S->>S: generate_qr_code(title_slide)
    S->>ST: display_qr(qr_image)
    
    %% Title Slide Reception
    RT->>R: analyze_frame(frame)
    R->>Sl: from_string(qr_data)
    Note over R: Validate title slide
    R->>R: handle_received_data()
    Sl->>R: generate_confirmation_qr(0)
    R->>RT: display_qr(confirm_qr)
    
    %% Content Transfer Loop
    loop Until all content is transferred
        %% Confirmation handling
        ST->>S: analyze_frame(frame)
        S->>S: handle_confirmation()
        Note over S: Verify confirmation index

        %% Sender side
        S->>S: get_next_content_slide()
        S->>Sl: to_string()
        S->>S: generate_qr_code(content)
        S->>ST: display_qr(qr_image)
        Note over S: Wait for confirmation
        
        %% Receiver side
        RT->>R: analyze_frame(frame)
        Note over R: Validate content & index
        R->>Sl: from_string(qr_data)
        R->>R: handle_received_data()
        Sl->>R: generate_confirmation_qr(index)
        R->>RT: display_qr(confirm_qr)
        
    end
    
    %% End Process
    S->>Sl: get_end_slide()
    S->>S: generate_qr_code(end_slide)
    S->>ST: display_qr(end_qr)
    
    RT->>R: analyze_frame(frame)
    R->>Sl: from_string(qr_data)
    R->>R: handle_received_data()
    R->>R: save_to_file()
    
    %% Cleanup
    S->>CM: stop_camera()
    R->>CM: stop_camera()
    
    Note over U1,U2: Transfer Complete
```
---

## **License**
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## **Contributing**
Contributions are welcome! Feel free to submit a pull request or open an issue.

---

## **Acknowledgments**
Special thanks to the developers and contributors who made this project possible.
