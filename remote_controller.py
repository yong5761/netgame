from operator import truediv
from types import SimpleNamespace
from pico2d import *
from packet import *

class RemoteController: # AIController 자리에 들어간다
 def __init__(self, character):
  self.ch = character
  self.packet_data = None
  self.state = STATE_IDLE
  self.state_map = {
   STATE_IDLE: self.idle,
   STATE_WALK: self.walk,
   STATE_JUMP: self.jump,
   STATE_MOVE_JUMP: self.move_jump,
   STATE_RUN: self.run,
   STATE_RUN_JUMP: self.run_jump,
   STATE_BACK_DASH: self.back_dash,
   STATE_SIT_DOWN: self.sit_down,
   STATE_SIT_UP: self.sit_up,
   STATE_NORMAL_ATTACK: self.normal_attack,
   STATE_AIR_ATTACK: self.air_attack,
   STATE_SIT_ATTACK: self.sit_attaack,
   STATE_GUARD: self.guard,
   STATE_GET_HIT: self.get_hit,
   STATE_COMBO_ATTACK: self.combo_attack,
   STATE_DEAD: self.dead
  }
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

  if state_id is not None:
   last_state_id = ch.get_state_id()

   if last_state_id != state_id:
    self.ch.state_machine.cur_state.exit(None)
    self.ch.state_machine.cur_state = self.state_map.get(state_id)
    self.ch.state_machine.cur_state.enter(None)

  ch.frame= data["frame"]

  flag = data["flag"]
  if flag & FLAG_ATTACKING:
   self.ch.is_attacking = True
  if flag & FLAG_GUARDING:
   self.ch.is_guarding = True
  if flag & FLAG_HITTED:
   self.ch.is_hitted = True
  if flag & FLAG_DAMAGEABLE:
   self.ch.is_opponent_attacking = True
