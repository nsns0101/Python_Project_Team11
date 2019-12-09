import arcade

class Platform:
    platform = None
    center_x = None     #장애물 x위치
    center_y = None     #장애물 y위치
    scale = None        #장애물 크기
    speed = None        #장애물 속도
    start_x = None      #장애물 start위치
    end_x = None        #장애물 end위치
    fall = False        #떨어지는 장애물인지의 유무
    teleport = False    #텔레포트 기능
    hard_platform = False   #플랫폼 위에 오를 수 있는 기능
    die = False             #부딪히면 죽는지의 여부
    def __init__(self, platform, center_x, center_y, scale, speed = 0, start_x = 0, end_x = 0,fall = False, die = False, teleport = None, hard_platform = False):
        self.platform = platform
        self.center_x = center_x
        self.center_y = center_y
        self.scale = scale
        self.speed = speed
        self.start_x = start_x
        self.end_x = end_x
        self.fall = fall
        self.die = die
        self.teleport = teleport
        self.hard_platform = hard_platform
    def newPlatform(self):
        self.platform_sprite = arcade.Sprite("images/tiles/{}.png".format(self.platform), self.scale)
        self.platform_sprite.center_x = self.center_x
        self.platform_sprite.center_y = self.center_y
        return self.platform_sprite

    def movePlatform(self):         # 일정 자리를 맴돌게 하기
        if 2 >self.center_x - self.start_x > -2:
            #전의 speed가 -면 -로 줘서 +로
            if(self.speed < 0):
                self.speed = -self.speed
            self.speed = +self.speed

        elif 2 > self.center_x - self.end_x > -2:
            self.speed = -self.speed

        self.center_x = self.center_x +  self.speed
        return self.speed
