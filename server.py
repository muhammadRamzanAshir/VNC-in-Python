import socket
import struct
import pyautogui
import numpy as np
import cv2

class VNC_Server():
    def __init__(self, host="0.0.0.0", port=5900):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        """ Start the VNC server and wait for a connection """
        self.server.bind((self.host, self.port))  # 🛠️ FIX: Wrap host and port in tuple
        self.server.listen(1)
        print(f"[*] Waiting for the connection on {self.host}:{self.port}")
        client, address = self.server.accept()
        print(f"[+] Connected to {address}")
        self.handle_client(client)

    def handle_client(self, client):
        """ Continuously send frames to the client """
        try:
            while True:
                frame = self.capture_screen()
                self.send_frame(client, frame)
        except (ConnectionResetError, BrokenPipeError):  # 🛠️ FIX: Handle client disconnect
            print("[!] Client disconnected.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client.close()

    def capture_screen(self):
        """ Capture screenshots and return as JPEG-encoded byte array """
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        _, img_encoded = cv2.imencode('.jpg', frame)
        return img_encoded.tobytes()  # 🛠️ FIX: Ensure byte format

    def send_frame(self, client, frame):
        """ Send the frame to the client """
        try:
            client.sendall(struct.pack("!I", len(frame)))  # Send frame size
            client.sendall(frame)  # Send frame data
        except (ConnectionResetError, BrokenPipeError):
            print("[!] Connection lost, stopping transmission.")
            client.close()

if __name__ == "__main__":
    server = VNC_Server()
    server.start()
