import queue
import threading

my_player_num   = -1                # 내가 1P(0) 인지 2P(1) 인지

is_connected    = True              # 서버 연결

server_ip       = "127.0.0.1"
server_port     = 9000

recv_queue      = queue.Queue()     # 수신한 패킷 저장
send_queue      = queue.Queue()     # 송신할 패킷 저장

queue_lock      = threading.Lock()  # 큐 동기화

last_recv_seq   = -1                # UDP 순번. 이보다 작으면 버린다

send_seq        = 0                 # 전송할 UDP순번