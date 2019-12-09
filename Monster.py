import arcade

class Monster:
    monster = None      #몬스터
    center_x = None     #몬스터 x위치
    center_y = None     #몬스터 y위치
    scale = None        #몬스터 크기
    speed = None        #몬스터 속도
    start_x = None      #맴돌 start위치
    end_x = None        #맴돌 end위치

    def __init__(self, monster, center_x, center_y, scale, speed, start_x, end_x):
        self.monster = monster
        self.center_x = center_x
        self.center_y = center_y
        self.scale = scale
        self.speed = speed
        self.start_x = start_x
        self.end_x = end_x

    def newMonster(self):    #몬스터 생성
        self.monster_sprite = arcade.Sprite("images\enemies\{}.png".format(self.monster), self.scale)
        self.monster_sprite.center_x = self.center_x
        self.monster_sprite.center_y = self.center_y
        return self.monster_sprite

    def moveMonster(self):         # 일정 자리를 맴돌게 하기
        if 2 >self.center_x - self.start_x > -2:
            if(self.speed < 0):
                self.speed = -self.speed
            self.speed = +self.speed

        elif 2 > self.center_x - self.end_x > -2:
            self.speed = -self.speed

        self.center_x = self.center_x +  self.speed
        return self.speed
