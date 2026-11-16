from behavior_tree import BehaviorTree, Selector, Sequence, Condition, Action
from types import SimpleNamespace
from pico2d import *
from random import randint
import packet

class RemoteController: # AIController 자리에 들어간다
 def __init__(self, character):
  self.ch = character
  self.data = None

 def apply_tick(self, tick):
  # 서버에서 받은 상대 플레이어 상태 저장
  self.data = tick
 def update(self):
  if self.data is None:
   return
  ch = self.ch
  data = self.data

  # 상태 동기화
  ch.xPos = data["x"]
  ch.yPos = data["y"]
  ch.face_dir = data["face"]
  # FSM 상태 동기화
  state_id = data["state"]
  next_state = ch.get_state_object(state_id)

  if next_state is not None:
   current_state = ch.state_machine.cur_state

   if current_state != next_state:
    current_state.exit(("NETWORK", next_state))
    next_state.enter(("NETWORK", current_state))
    ch.state_machine.cur_state = next_state
 def idle(self):
  e = ('INPUT', SimpleNamespace(type=SDL_KEYUP, key=self.ch.keymap['left']))
  self.ch.state_machine.handle_state_event(e)
  e = ('INPUT', SimpleNamespace(type=SDL_KEYUP, key=self.ch.keymap['right']))
  self.ch.state_machine.handle_state_event(e)
 def walk(self):
  # face방향으로
  if self.ch.face_dir == -1:
   e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['left']))
  else:
   e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['right']))
  self.ch.state_machine.handle_state_event(e)
 def jump(self):
  e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['up']))
  self.ch.state_machine.handle_state_event(e)
 def move_jump(self):
  if self.ch.face_dir == -1:
   e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['left']))
  else:
   e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['right']))
  self.ch.state_machine.handle_state_event(e)
 def run(self):
  if self.ch.face_dir == -1:
   e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['left']))
  else:
   e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['right']))
 def run_jump(self):
  if self.ch.face_dir == -1:
   e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['left']))
  else:
   e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['right']))
 def back_dash(self):
  if self.ch.face_dir == -1:
   e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['right']))
  else:
   e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['left']))
  self.ch.state_machine.handle_state_event(e)
 def sit_down(self):
  e = ('INPUT', SimpleNamespace(type=SDL_KEYDOWN, key=self.ch.keymap['right']))
  self.ch.state_machine.handle_state_event(e)
 def apply_state(self, state):
  ch = self.ch
  ch.state = state
  # 공격 및 방어 관련 플래그
  ch.is_attacking = state in (
   packet.STATE_NORMAL_ATTACK,
   packet.STATE_AIR_ATTACK,
   packet.STATE_SIT_ATTACK,
   packet.STATE_COMBO_ATTACK
  )