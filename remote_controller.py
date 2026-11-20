from operator import truediv
from types import SimpleNamespace
from pico2d import *
from packet import *

class RemoteController: # AIController 자리에 들어간다
 def __init__(self, character):
  self.ch = character
  self.packet_data = None
  self.state = STATE_IDLE
  self.state_map = self.ch.state_map
 def apply_tick(self, data):
  # 서버에서 받은 패킷 저장
  self.packet_data = data
 def update(self):
  if self.packet_data is None:
   return
  ch = self.ch
  data = self.packet_data

  # 상태 동기화
  ch.xPos = data["x"]
  ch.yPos = data["y"]
  ch.face_dir = data["face"]
  # FSM 상태 동기화
  state_id = data["state"]
  # 프레임 수정, 상태 수정
  new_state = self.state_map.get(state_id)
  if new_state is not None:
   if ch.state_machine.cur_state != state_id:
    ch.state_machine.cur_state.exit(('NETWORK', None))
    ch.state_machine.cur_state = new_state
    ch.state_machine.cur_state.enter(None)

  ch.frame = data["frame"]

  flag = data["flag"]
  ch.is_attacking = bool(flag & FLAG_ATTACKING)
  ch.is_guarding = bool(flag & FLAG_GUARDING)
  ch.is_hitted = bool(flag & FLAG_HITTED)
  ch.is_opponent_attacking = bool(flag & FLAG_DAMAGEABLE)