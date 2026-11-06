import socket
import threading
import queue
import struct

import threading
import net_state
# 네트워크 통신 클래스
class NetClient:
 def __init__(self):
  self.tcp_socket=None
  self.udp_socket=None
  # 통신 중
  self.running=False
  # 통신 스레드
  self.tcp_thread = None
  self.udp_thread = None
  self.send_thread = None

 def connect(self, ip, port):
    try:

        net_state.server_ip = ip
        net_state.server_port = port
        # TCP 소켓 생성 및 연결
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.connect((ip, port))
        # UDP 소켓 생성 및 수신용 포트 할당
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind(("", 0))

        self.running = True
        net_state.is_connected = True

        self.tcp_thread = threading.Thread(target=self._tcp_recv_loop, daemon=True)# TCP 수신 스레드
        self.udp_thread = threading.Thread(target=self._udp_recv_loop, daemon=True)# UDP 수신 스레드
        self.send_thread = threading.Thread(target=self._send_loop, daemon=True)# 송신 스레드

        self.tcp_thread.start()
        self.udp_thread.start()
        self.send_thread.start()

        return True
    # 연결 중 에러
    except OSError as e:
        print("서버 연결 실패:", e)
        self.disconnect()
        return False

 def disconnect(self):
     self.running = False
     net_state.is_connected = False

     for sock in (self.tcp_sock, self.udp_sock):# 소켓 닫기
         if sock:
             try:
                 sock.shutdown(socket.SHUT_RDWR)
             except OSError:
                 pass

             try:
                 sock.close()
             except OSError:
                 pass

     self.tcp_sock = None
     self.udp_sock = None

 def send_packet(self, pkt_type, body): # TCP
  pass
 def send_tick(self, body): # UDP
  pass
 def pop_packet(self):# 수신 큐에서 패킷 가져오기
  pass
 def _tcp_recv_loop(self):# TCP 수신
  pass
 def _udp_recv_loop(self):# UDP 수신
  pass
 def _send_loop(self):# 발신
  pass