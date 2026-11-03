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
  self.runnind=False
  # 통신 스레드
  self.tcp_thread = None
  self.udp_thread = None
  self.send_thread = None

 def connect(ip, port):
  pass
 def disconnect():
  pass
 def send_packet(pkt_type, body): # TCP
  pass
 def send_tick(body): # UDP
  pass
 def pop_packet():
  pass
 def _tcp_recv_loop():
  pass
 def _udp_recv_loop():
  pass
 def _send_loop():
  pass