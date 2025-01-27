# LightLink

LightLink is a Python-based project enabling data transfer between two computers using QR codes. The project features a simple user interface for sending and receiving files, utilizing cameras and screens for communication.

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

## **Project Structure**
```
LightLink/
├── src/
│   ├── main.py         # Main application file
│   ├── sender.py       # Back-end logic for the sender
│   ├── receiver.py     # Back-end logic for the receiver
│   ├── slide.py        # Handles chunking data into QR codes
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

![Example QR Code](assets/qr_example1.png)

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
