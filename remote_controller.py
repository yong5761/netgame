from operator import truediv
from types import SimpleNamespace
from pico2d import *

import net_state
from packet import *
import common
import time

class RemoteController: # AIController 자리에 들어간다
 def __init__(self, character):
  self.ch = character
  self.packet_data = None
  self.state = STATE_IDLE
  self.last_state = STATE_IDLE
  self.state_map = self.ch.state_map
  self.prexPos = character.xPos
  self.preyPos = character.yPos
  self.lasttime = time.monotonic()
  net_state.udp_intervals.append(0.05)
 def apply_tick(self, data):
  # 서버에서 받은 패킷 저장
  self.packet_data = data
  # 패킷을 받은 시점 저장
  net_state.udp_intervals.append(time.monotonic() - self.lasttime )
  self.lasttime = time.monotonic()
  self.prexPos = self.ch.xPos
  self.preyPos = self.ch.yPos
 def update(self):
  if self.packet_data is None:
   return
  ch = self.ch
  data = self.packet_data

  # FSM 상태 동기화
  state_id = data["state"]
  new_state = self.state_map.get(state_id)
  flag = data["flag"]

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
    else:
     e = ('NETWORK', None)
    self.ch.state_machine.cur_state.exit(None)
    self.ch.state_machine.cur_state = new_state
    self.ch.state_machine.cur_state.enter(e)
  # 상태 동기화
  ch.face_dir = data["face"]
  # 위치 보간
  avg_time = sum(net_state.udp_intervals) / len(net_state.udp_intervals)
  t = 0
  if avg_time > 0:
   t = min(max((time.monotonic() - self.lasttime) / avg_time, 0), 1)
  x = self.prexPos + (data["x"] - self.prexPos) * t
  y = self.preyPos + (data["y"] - self.preyPos) * t
  ch.xPos = x
  ch.yPos = y
  # 공격 구분, 프레임
  ch.frame = data["frame"]



 def apply_hit(self, data):
  victim_num = data['victim']
  attacker_num = data['attacker']
  data['damage']
  data['hp']
  data['knock_x']
  victim_num = data["victim"]
  attacker_num = data["attacker"]

  # 플레이어 번호 검사
  if victim_num not in (0, 1) or attacker_num not in (0, 1):
   return

  victim = common.characters[victim_num]
  attacker = common.characters[attacker_num]

  # 공격 성공 처리
  attacker.is_succeeded_attack = True
  attacker.attack_hitbox.reset_rect()

  # 서버에서 계산한 HP 적용
  victim.hp = data["hp"]

  # 실제 피해가 발생한 경우
  if data["damage"] > 0:
   victim.is_hitted = True

   # 서버에서 전달한 넉백 적용
   victim.xPos += data["knock_x"]

   # 피격 애니메이션 실행
   victim.state_machine.handle_state_event(('HITTED', None))
  pass