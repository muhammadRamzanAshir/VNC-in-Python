import socket
import struct
import cv2
import numpy as np

class VNC_Client():
    def __init__(self, server_ip, server_port=5900):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """ Connect to the VNC server """
        self.client.connect((self.server_ip, self.server_port))
        print("[+] Connected to VNC server")
        self.receive_stream()

    def receive_stream(self):
        """ Continuously receive and display screen frames from the server """
        try:
            while True:
                frame = self.receive_frame() 
                if frame is None:
                    break
                self.display_frame(frame)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client.close()
            cv2.destroyAllWindows()

    def receive_frame(self):
        """ Receive a single frame from the server """
        try:
            # Read frame size
            frame_size_data = self.client.recv(4)
            if not frame_size_data:
                return None
            data_size = struct.unpack("!I", frame_size_data)[0]  

            data = b""  # 🛠️ FIX: Use bytes instead of string
            while len(data) < data_size:
                packet = self.client.recv(4096)
                if not packet:
                    return None
                data += packet  # 🛠️ FIX: Properly append bytes
            
            return np.frombuffer(data, dtype=np.uint8)
        except (ConnectionResetError, BrokenPipeError):
            print("[!] Connection lost.")
            return None

    def display_frame(self, frame):
        """ Display the received frame """
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        if frame is not None:
            cv2.imshow("VNC Viewer", frame)
        if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
            self.client.close()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    client = VNC_Client(server_ip="127.0.0.1") 
    client.connect()
