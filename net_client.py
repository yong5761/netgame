# 네트워크 통신 클래스
class NetClient:
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