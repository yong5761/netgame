from operator import truediv
from types import SimpleNamespace
from pico2d import *
from packet import *

class RemoteController: # AIController 자리에 들어간다
 def __init__(self, character):
  self.ch = character
  self.packet_data = None
  self.state = STATE_IDLE
  self.last_state = STATE_IDLE
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
  # 공격 구분
  ch.frame = data["frame"]
  flag = data["flag"]


 def attack_event(self, new_state, flag):
  if new_state is not None and self.ch.state_machine.cur_state != new_state:
   e = None
   # 공격 수신시 이걸로 공격 종류 구분
   if bool(flag & KEY_LP):
    e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['lp']))
   elif bool(flag & KEY_RP):
    e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['rp']))
   elif bool(flag & KEY_RK):
    e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['rk']))
   elif bool(flag & KEY_LK):
    e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['lk']))
   self.ch.state_machine.handle_state_event(e)
   self.ch.state_machine.cur_state.exit(None)
   self.ch.state_machine.cur_state = new_state
   self.ch.state_machine.cur_state.enter(e)