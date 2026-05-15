"""本地Socket通信服务 - 桌宠端监听，CLI端发送"""
import json
import socket
import threading
from PyQt6.QtCore import QObject, pyqtSignal


SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 19527


class SocketServer(QObject):
    """桌宠端：监听来自CLI的消息"""
    message_received = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._running = False
        self._server: socket.socket | None = None
        self._thread: threading.Thread | None = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._server:
            self._server.close()

    def _listen(self):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._server.bind((SOCKET_HOST, SOCKET_PORT))
            self._server.listen(5)
            self._server.settimeout(1.0)
            while self._running:
                try:
                    conn, _ = self._server.accept()
                    data = conn.recv(4096).decode("utf-8")
                    conn.close()
                    if data:
                        msg = json.loads(data)
                        self.message_received.emit(msg)
                except socket.timeout:
                    continue
                except (json.JSONDecodeError, ConnectionError):
                    continue
        except OSError:
            pass
        finally:
            if self._server:
                self._server.close()


def send_to_pet(message: dict) -> bool:
    """CLI端：发送消息给桌宠"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        sock.connect((SOCKET_HOST, SOCKET_PORT))
        sock.sendall(json.dumps(message, ensure_ascii=False).encode("utf-8"))
        sock.close()
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False
