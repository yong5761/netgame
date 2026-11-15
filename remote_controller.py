import common
import net_state
import packet

class RemoteController: # AIController 자리에 들어간다
 def __init__(self, character):
  self.character = character
  self.data = None

 def apply_tick(self, tick):
  # 서버에서 받은 상대 플레이어 상태 저장
  self.data = tick

 def update(self):
  if self.data is None:
   return
  ch = self.character
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

 def apply_state(self, state):
  ch = self.character
  ch.state = state

  # 공격 및 방어 관련 플래그
  ch.is_attacking = state in (
   packet.STATE_NORMAL_ATTACK,
   packet.STATE_AIR_ATTACK,
   packet.STATE_SIT_ATTACK,
   packet.STATE_COMBO_ATTACK
  )