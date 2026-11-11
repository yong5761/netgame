from pico2d import draw_rectangle
import round_sync

class HitBox:
    def __init__(self, owner, hb_kind:str, rect:tuple[float, float, float, float]):
        self.owner = owner
        self.hb_kind = hb_kind
        self.rect = rect
    def update(self, new_rect:tuple[float, float, float, float]):
        self.rect = new_rect
    def reset_rect(self):
        self.rect = (0,0,0,0)

class HitBoxManager:
    def __init__(self):
        self.hitboxes = []
        self.hit_reported = False

    def register_hitbox(self, hitbox: HitBox):
        self.hitboxes.append(hitbox)

    def debug_draw(self):
        for hb in self.hitboxes:
            draw_rectangle(hb.rect[0], hb.rect[1], hb.rect[0] + hb.rect[2], hb.rect[1] + hb.rect[3])

    def collision_check(self, hb1: HitBox, hb2: HitBox) -> bool:
        x1, y1, w1, h1 = hb1.rect
        x2, y2, w2, h2 = hb2.rect

        # 너비/높이가 음수일 수인 경우도 고려
        left1 = min(x1, x1 + w1)
        right1 = max(x1, x1 + w1)
        bottom1 = min(y1, y1 + h1)
        top1 = max(y1, y1 + h1)

        left2 = min(x2, x2 + w2)
        right2 = max(x2, x2 + w2)
        bottom2 = min(y2, y2 + h2)
        top2 = max(y2, y2 + h2)

        # 두 사각형이 서로 겹치지 않는 조건을 먼저 검사
        no_overlap = (right1 < left2) or (left1 > right2) or (top1 < bottom2) or (bottom1 > top2)

        # no_overlap 가 False 이면 충돌(테두리 맞닿음 포함)
        return not no_overlap

    def detect_is_opponent_attacking(self):
        main_boxes = [hb for hb in self.hitboxes if hb.hb_kind == 'body']
        box_1 = main_boxes[0]
        box_2 = main_boxes[1]
        ch_1 = box_1.owner
        ch_2 = box_2.owner
        if ch_1.is_attacking :
            ch_2.is_opponent_attacking = True
        else:
            ch_2.is_opponent_attacking = False

        if ch_2.is_attacking :
            ch_1.is_opponent_attacking = True
        else:
            ch_1.is_opponent_attacking = False

    def detect_body_overlaps(self):
        boxes = [hb for hb in self.hitboxes if hb.hb_kind == 'body']
        box_1 = boxes[0]
        box_2 = boxes[1]
        ch_1 = box_1.owner
        ch_2 = box_2.owner

        if self.collision_check(box_1, box_2) and ch_1.is_hitted == False and ch_2.is_hitted == False and ch_1.is_attacking == False and ch_2.is_attacking == False:
            if ch_1.vy ==0 or ch_2.vy ==0:
                if ch_1.xPos < ch_2.xPos:
                    overlap_x = min(box_1.rect[0] + box_1.rect[2], box_2.rect[0] + box_2.rect[2]) - max(box_1.rect[0], box_2.rect[0])
                    ch_1.xPos -= overlap_x//2
                    ch_2.xPos += overlap_x//2
                else:
                    overlap_x = min(box_1.rect[0] + box_1.rect[2], box_2.rect[0] + box_2.rect[2]) - max(box_1.rect[0], box_2.rect[0])
                    ch_1.xPos += overlap_x//2
                    ch_2.xPos -= overlap_x//2
    def can_hit(self, attacker, target):
        # 공격 박스와 상대 물체가 겹치지 않으면 피격 처리 X
        if not self.collision_check(attacker.attack_hitbox, target.body_hitbox):
            return False
        # 상대가 가드 중이면 피해 X
        if target.is_guarding:
            return False
        # 피해를 받을 수 없는 상태면 피해 X
        if not target.get_damage:
            return False
        return True

    def apply_local_hit(self, attacker, target):
        target.is_hitted = True
        attacker.is_succeeded_attack = True
        target.hp -= attacker.atk
        target.get_damage = False
        target.xPos += (40 * attacker.face_dir)  # 넉백 효과
        target.state_machine.handle_state_event(('HITTED', None))

    def detect_online_hit(self, characters, my_player_num):
        # 플레이어 번호를 받기 전에는 검사하지 않음
        if my_player_num not in (0, 1):
            return False

        if len(characters) != 2:
            return False

        victim_num = my_player_num
        attacker_num = 1 - my_player_num

        target = characters[victim_num]
        attacker = characters[attacker_num]

        # 공격 박스가 사라지면 다음 공격을 보고할 수 있게 초기화
        _, _, width, height = attacker.attack_hitbox.rect
        if width == 0 or height == 0:
            self.hit_reported = False
            return False

        if self.hit_reported:
            return False

        if not target.get_damage:
            return False

        if not self.collision_check(attacker.attack_hitbox, target.body_hitbox):
            return False

        queued = round_sync.report_hit(victim_num, attacker_num, attacker.atk, target.is_guarding)
        if queued:
            self.hit_reported = True

        return queued

    def detect_attack_hits(self):
        body_boxes = [hb for hb in self.hitboxes if hb.hb_kind == 'body']
        body_box_1, body_box_2 = body_boxes[0], body_boxes[1]

        def handle(attacker, target):
            if self.can_hit(attacker, target):
                self.apply_local_hit(attacker, target)
                
        handle(body_box_1.owner, body_box_2.owner)
        handle(body_box_2.owner, body_box_1.owner)


    def update_face_dir(self, ch1, ch2):
        if ch1.xPos < ch2.xPos:
            if ch1.vy ==0:
                ch1.face_dir = 1
            if ch2.vy ==0:
                ch2.face_dir = -1
        else:
            if ch1.vy ==0:
                ch1.face_dir = -1
            if ch2.vy ==0:
                ch2.face_dir = 1