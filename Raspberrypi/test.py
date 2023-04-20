import cv2
import socket
import struct
import pickle

HOST = '192.168.1.16'
PORT = 8080

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server is listening on {HOST}:{PORT}...")
    conn, addr = s.accept()
    print(f"Connected by {addr}")

    while True:
        # Nhận kích thước dữ liệu
        data_size = conn.recv(struct.calcsize("I"))
        if not data_size:
            break

        # Nhận dữ liệu
        data_size = struct.unpack("I", data_size)[0]
        data = b''
        while len(data) < data_size:
            packet = conn.recv(data_size - len(data))
            if not packet:
                break
            data += packet

        # Chuyển dữ liệu sang hình ảnh và hiển thị
        frame = pickle.loads(data)
        cv2.imshow('Received image', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Giải phóng socket và đóng cửa sổ hiển thị hình ảnh
    conn.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
