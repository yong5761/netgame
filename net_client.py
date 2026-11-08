import socket
import threading
import queue
import struct

import threading
import net_state
import packet

# 네트워크 통신 클래스
class NetClient:
 def __init__(self):
  self.tcp_socket = None
  self.udp_socket = None
  # 통신 중
  self.running = False
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
  if not net_state.is_connected or self.tcp_sock is None:
   return False
  try:
   # 헤더 생성 (본문 크기 + 패킷 종류)
   header = packet.pack_header(len(body), pkt_type)
   send_data = header + body

   self.tcp_sock.sendall(send_data)# TCP 전송
   return True
  except OSError as e:
   print(f"TCP 전송 오류: {e}")
   return False

 def send_tick(self, body): # UDP
  if not net_state.is_connected or self.udp_sock is None:
   return False
  try:
   # 틱 패킷 헤더 생성
   header = packet.pack_header(len(body), packet.PKT_TICK_C2S)
   send_data = header + body

   self.udp_sock.sendto(send_data, (net_state.server_ip, net_state.server_port))# UDP 전송
   return True
  except OSError as e:
     print(f"UDP 전송 오류: {e}")
     return False

 def pop_packet(self):# 수신 큐에서 패킷 가져오기
 # 가장 먼저 들어온 패킷 반환
    try:
     return net_state.recv_queue.get_nowait()
    except queue.Empty:
      return None
 def _recv_exact(self, size):# 헤더 받기
     data = bytearray()
     while len(data) < size:
         chunk = self.tcp_sock.recv(size - len(data))
         if not chunk:
             return None
         data.extend(chunk)
     return bytes(data)

 def _tcp_recv_loop(self):# TCP 수신 스레드용 함수
  while self.running:
     try:
         header = self._recv_exact(packet.HEADER_SIZE)
         if header is None:
             break
         packet.unpack_header(header)
         data = self.tcp_sock.recv(32)
         if not data:
             break
         net_state.recv_queue.put(data)
     except OSError:
         break
  self.disconnect()

 def _udp_recv_loop(self):# UDP 수신 스레드용 함수
  pass
 def _send_loop(self):# 발신
  pass