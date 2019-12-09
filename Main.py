"""
Platformer Game
"""
import arcade
import random
import Monster
import Platform
import os
from  button_create import *
import time
a_left = False
a_right = False

over = True
# 화면 크기
screen_width = 1500
screen_height = 850
screen_size={1:{"width":800,"height":600},2:{"width":1024,"height":768},3:{"width":1280,"height":1024},4:{"width":1500,"height":850}}
count = 4

#게임 제목
SCREEN_TITLE = "game"

#기본적인 요소 크기
CHARACTER_SCALING = 1       #플레이어 크기
TILE_SCALING = 0.5          #땅 크기
COIN_SCALING = 0.5          #코인 크기
SPRITE_PIXEL_SIZE = 128     #몬스터 크기
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 6  #플레이어 스피드
MONSTER_MOVEMENT_SPEED = 1   #몬스터 스피드
PLATFORM_MOVEMENT_SPEED = 1  #플랫폼 스피드

GRAVITY = 1
PLAYER_JUMP_SPEED = 24      #플레이어 점프 속도

#플레이어를 기준으로 위아래, 양옆을 보여주는 빈도
LEFT_VIEWPORT_MARGIN = 130      #왼쪽
RIGHT_VIEWPORT_MARGIN = 230     #오른쪽
BOTTOM_VIEWPORT_MARGIN = 200    #아래
TOP_VIEWPORT_MARGIN = 130       #위

#플레이어 시작 좌표
PLAYER_START_X = 180
PLAYER_START_Y = 300


RIGHT_FACING = 0
LEFT_FACING = 1

menu_button_left = int(1.5*(screen_width//3))
menu_button_right = int(1.3*(screen_width//3))+274

def load_texture_pair(filename):# 화면 , 가상 화면
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename, scale=CHARACTER_SCALING),
        arcade.load_texture(filename, scale=CHARACTER_SCALING, mirrored=True)
    ]

def fit_size(width, height): #  게임 창 크기 변화에 따른 변수 값 변경
    global screen_width, screen_height, menu_button_left, menu_button_right

    screen_width = width
    screen_height = height
    menu_button_left = int(1.2*(screen_width//3))
    menu_button_right = int(1.2*(screen_width//3))+274

#사진, 애니메이션 관련  .. 스프라이트
class PlayerCharacter(arcade.Sprite): # 메인 캐릭터 움직임 애니메이션 처리

    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        # Track our state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False
        self.ground_ff = False

        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)

        # 구조물 판정 박스
        self.points = [[-22, -45], [22, -45], [22, 20], [-22, 20]]

        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3

        main_path = "images\man\size2\character_malePerson"

        # 텍스처 로딩, 서있을 때, 점프(올라갈 때 ) 점프(내려올 떄)
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        # 걷는 이미지 추가
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # 사다리 이미지 추가
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png", scale=CHARACTER_SCALING)
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png", scale=CHARACTER_SCALING)
        self.climbing_textures.append(texture)

        #불러온 이미지로 애니메이션 적용
    def update_animation(self, delta_time: float = 1/60):

        # 왼쪽, 오른쪽 보기
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # 사다리 애니메이션
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        # 점프애니메이션
        if self.jumping and not self.is_on_ladder:
            global ground_ff

            if self.change_y > 0 :
                self.texture = self.jump_texture_pair[self.character_face_direction]
            elif self.change_y < 0:
                self.texture = self.fall_texture_pair[self.character_face_direction]
                self.ground_ff = True

            if self.ground_ff:
                if self.change_y ==0:
                    self.jumping= False
                    self.ground_ff =False

            return

        # 가만히 서있는 애니메이션
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # 걷는 애니메이션
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

class MyGame(arcade.Window): # 메인 클래스
    """
    Main application class.
    """

    def __init__(self): # 초기화
        # Call the parent class and set up the window
        super().__init__(screen_width, screen_height, SCREEN_TITLE,resizable=True)

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.check_game = False
        self.check_menu = True
        self.check_option = False
        self.check_role = False
        self.background = None

        self.sound_status= True
        # path 설정
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # 버튼 리스트
        self.button_list = 0
        self.text_list = 0
        # 키가 눌린 상태
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        #추가
        self.monster = []
        self.platform = []

        self.coin_list = None
        self.wall_list = None
        self.foreground_list = None
        self.background_list = None
        self.dont_touch_list = None
        self.ladder_list = None
        self.player_list = None

        self.player_sprite = None
        self.button_sprite = None

        #추가
        self.monster_sprite = []
        self.platform_sprite = []

        self.player_physics_engine = None
        self.monster_physics_engine = []
        self.platform_physics_engine = []


        self.view_bottom = 0
        self.view_left = 0

        # Where is the right edge of the map?
        self.end_of_map = 0


        self.level = 1  #초기 시작 레벨
        self.coin = 0   #먹어야할 코인 수
        self.life = 0   #남은 목숨

        self.bool_life = True

        self.menu_setup()
        # self.game_over_setup()

        #사운드
        #코인 먹기
        self.collect_coin_sound = arcade.load_sound("sounds/coin1.wav")
        #점프
        self.jump_sound = arcade.load_sound("sounds/jump1.wav")
        #게임오버
        self.game_over = arcade.load_sound("sounds/gameover1.wav")
    def menu_setup(self): # 메뉴 화면 초기화(init)
        # 배경
        self.background_title = 0
        self.bakcground = 0
        self.background_title = arcade.load_texture("images/game.png")
        self.background = arcade.load_texture("images/background.png")

        # 리스트.
        self.text_list = []
        self.button_list = []
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        ## 처음 버튼 생성.
        # 시작 버튼
        self.menu_left = screen_width/3+screen_width*(1/12)-15
        self.start_buttom = Button_cr(self.menu_left ,self.menu_left +250,screen_height*(3/5)+screen_height*(1/10),screen_height*(3/5),"Start",arcade.color.ANDROID_GREEN,self.game_start)
        self.option_buttom = Button_cr(self.menu_left ,self.menu_left +250,screen_height*(2/5)+screen_height*(1/10),screen_height*(2/5),"Option",arcade.color.ANDROID_GREEN,self.go_to_option)
        self.rule_buttom = Button_cr(self.menu_left ,self.menu_left +250,screen_height*(1/5)+screen_height*(1/10),screen_height*(1/5),"Rule",arcade.color.ANDROID_GREEN,self.go_to_rule)
        self.button_list.append(self.start_buttom)
        self.button_list.append(self.option_buttom)
        self.button_list.append(self.rule_buttom)

        print ("추가됨")
    def option_setup(self): #옵션 화면 초기화(init)
        self.option_left = screen_width//3
        self.option_right = screen_width*(2/3)
        self.title_left = int (screen_width*(1/12))
        self.title_right =  int (self.title_left + screen_width*(1/6))
        self.button_list = []
        self.text_list = []

        self.title_option = Text_cr(self.option_left,self.option_right ,screen_height-screen_height//8,screen_height*(3/4),"Option")
        #해상도
        self.title_size = Text_cr( self.title_left,self.title_right,screen_height*(3/4)-screen_height//16,screen_height*(2/4),"Size")
        self.text_size =Text_cr(self.option_left,self.option_right,screen_height*(3/4)-screen_height//16,screen_height*(2/4),"{} X {}".format(screen_width,screen_height),size=40)
        self.size_up_button = Button_cr(self.option_right+10, screen_width-screen_width*(1/6), screen_height*(3/4)-screen_height//16, screen_height*(19/32),"UP",arcade.color.ANDROID_GREEN,self.size_up,size=15)
        self.size_down_button = Button_cr(self.option_right+10,screen_width-screen_width*(1/6),screen_height*(19/32),screen_height*(2/4),"DOWN",arcade.color.ANDROID_GREEN,self.size_down,size=15)
        #소리
        self.title_sound = Text_cr(self.title_left,self.title_right,screen_height*(2/4)-screen_height//16,screen_height*(1/4),"Sound")
        self.status_sound = Button_cr(self.option_left,self.option_right,screen_height*(2/4)-screen_height//16,screen_height*(1/4),"ON",arcade.color.ANDROID_GREEN,self.sound_on_off)


        self.text_list.append(self.title_option)

        self.text_list.append(self.title_size)
        self.text_list.append(self.text_size)
        self.text_list.append(self.title_sound)
        self.back_button = Button_cr(self.title_left,self.title_right,screen_height-screen_height//8,screen_height*(3/4),"Back",arcade.color.ANDROID_GREEN,self.go_to_menu)
        self.button_list.append(self.back_button)
        self.button_list.append(self.size_up_button)
        self.button_list.append(self.size_down_button)
        self.button_list.append(self.status_sound)


        print("옵션 셋")

    def rule_setup(self):#규칙 화면 초기화(init)
        self.rule_left = screen_width//3
        self.rule_right = screen_width*(2/3)
        self.title_left = int (screen_width*(1/12))
        self.title_right =  int (self.title_left + screen_width*(1/6))
        self.text_list = []
        self.button_list = []
        self.title_rule = Text_cr(self.rule_left,self.rule_right ,screen_height-screen_height//8,screen_height*(3/4),"Rule")
        self.back_button = Button_cr(self.title_left, self.title_right,screen_height-screen_height//8,screen_height*(3/4),"Back",arcade.color.ANDROID_GREEN,self.go_to_menu)
        self.text_list.append(self.title_rule)
        self.button_list.append(self.back_button)
        self.title_controll = Text_cr(self.title_left,self.title_right,screen_height*(3/4)-screen_height//16,screen_height*(2/4),"Key",size=35)
        self.title_rule = Text_cr(self.title_left,self.title_right,screen_height*(2/4)-screen_height//16,screen_height*(1/4),"Rule")
        self.rule_key = Text_cr(self.rule_left,self.rule_right,  screen_height*(3/4)-screen_height//16,  screen_height*(2/4),"UP: W or ↑, DOWN: S or ↓",size=25)
        self.rule_key2 = Text_cr(self.rule_left,self.rule_right,  screen_height*(3/4)-screen_height//16-50,  screen_height*(2/4)-50,"LEFT: A or ←, RIGHT: D or →",size=25)
        self.rule_text = Text_cr(self.rule_left,self.rule_right,screen_height*(2/4)-screen_height//16,screen_height*(1/4),"Collecting the coins! (multi round) ",size=25)
        self.text_list.append(self.title_controll)
        self.text_list.append(self.title_rule)
        self.text_list.append(self.rule_key)
        self.text_list.append(self.rule_key2)
        self.text_list.append(self.rule_text)
    def game_setup(self, level):# 게임 화면 초기화(init)     #초기값 설정
        """ Set up the game here. Call this function to restart the game. """
        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        #몬스터 리셋
        for i in range(len(self.monster)):
            del self.monster[0]
            del self.monster_sprite[0]
            del self.monster_physics_engine[0]
        #움직이는 플랫폼 리셋
        for i in range(len(self.platform)):
            del self.platform[0]
            del self.platform_sprite[0]
            del self.platform_physics_engine[0]

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.button_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.monster_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()

        self.ladder_list = None # 사다리 리스트

        level_list = {
            1: self.map_level_1,
            2: self.map_level_2,
            3: self.map_level_3,
            4: self.map_level_4,
            5: self.map_level_5,
            6: self.map_level_6,
            }


        #레벨함수 호출 (레벨마다의 설정)
        level_list[self.level]()

        #라이프가 초기화 되지 않게

        if self.bool_life == True:
            self.life = 10
        self.bool_life = False


        #캐릭터
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)



        # --- Load in a map from the tiled editor ---

        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'
        # Name of the layer that has items for foreground
        foreground_layer_name = 'Foreground'
        # Name of the layer that has items for background
        background_layer_name = 'Background'
        # Name of the layer that has items we shouldn't touch
        dont_touch_layer_name = "Don't Touch"
        #사다리 레이어
        ladders_layer_name = "Ladders"

        #맵 이름
        map_name = f"map2_level_{level}.tmx"
        # Read in the tiled map
        my_map = arcade.read_tiled_map(map_name, TILE_SCALING)

        # -- Walls
        # Grab the layer of items we can't move through
        map_array = my_map.layers_int_data[platforms_layer_name]

        #맵에서 오른 쪽 끝자리를 계산 (다음 맵으로)
        self.end_of_map = len(map_array[0]) * GRID_PIXEL_SIZE - 120

        # -- Background(my_map, "background", 0.5)
        self.background_list = arcade.generate_sprites(my_map, background_layer_name, TILE_SCALING)

        # -- Foreground
        self.foreground_list = arcade.generate_sprites(my_map, foreground_layer_name, TILE_SCALING)

        # -- Platforms
        self.wall_list = arcade.generate_sprites(my_map, platforms_layer_name, TILE_SCALING)
        # -- Coins
        self.coin_list = arcade.generate_sprites(my_map, coins_layer_name, TILE_SCALING)

        # -- Don't Touch Layer
        #여기서 맵.tmx파일이랑 연동?
        self.dont_touch_list = arcade.generate_sprites(my_map, dont_touch_layer_name, TILE_SCALING)


        # --- Other stuff
        # Set the background color
        if my_map.backgroundcolor:
            arcade.set_background_color(my_map.backgroundcolor)

        # #사다리가 있는 4번 맵


        # #플레이어의 움직임
        self.ladder_list = arcade.generate_sprites(my_map, ladders_layer_name, TILE_SCALING)

        self.player_physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,self.wall_list,gravity_constant=GRAVITY,ladders=self.ladder_list)
        print(self.player_physics_engine)


        #몬스터들은 중력에 영향이 없음
        for i in range(len(self.monster)):
            self.monster_physics_engine.append(arcade.PhysicsEnginePlatformer(self.monster_sprite[i], self.wall_list, 0))

        #플랫폼들은 중력에 영향이 없음(wall_list랑은 다름)
        for i in range(len(self.platform)):
            self.platform_physics_engine.append(arcade.PhysicsEnginePlatformer(self.platform_sprite[i],self.wall_list, 0))


    def game_over_setup(self): # 게임 오버
        self.background_title = 0
        self.text_list = []
        self.button_list = []
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.menu_left = screen_width/3+screen_width*(1/12)-15

        self.restart_button = Button_cr(self.menu_left ,self.menu_left +250,screen_height*(2/5)+screen_height*(1/10),screen_height*(2/5),"ReStart",arcade.color.ANDROID_GREEN,self.game_start)
        self.go_to_menu_button = Button_cr(self.menu_left ,self.menu_left +250,screen_height*(1/5)+screen_height*(1/10),screen_height*(1/5),"Menu",arcade.color.ANDROID_GREEN,self.go_to_menu)

        self.button_list.append(self.restart_button)
        self.button_list.append(self.go_to_menu_button)

        self.game_over_title = Text_cr(self.menu_left ,self.menu_left +250,screen_height*(3/5)+screen_height*(1/10),screen_height*(3/5),"GAME OVER")
        self.text_list.append(self.game_over_title)
        self.life = 10
    def game_clear_setup(self): # 게임 클리어
        self.background_title = 0
        self.text_list = []
        self.button_list = []
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.menu_left = screen_width/3+screen_width*(1/12)-15

        self.restart_button = Button_cr(self.menu_left ,self.menu_left +250,screen_height*(2/5)+screen_height*(1/10),screen_height*(2/5),"ReStart",arcade.color.ANDROID_GREEN,self.game_start)
        self.go_to_menu_button = Button_cr(self.menu_left ,self.menu_left +250,screen_height*(1/5)+screen_height*(1/10),screen_height*(1/5),"Menu",arcade.color.ANDROID_GREEN,self.go_to_menu)

        self.button_list.append(self.restart_button)
        self.button_list.append(self.go_to_menu_button)

        self.game_clear_title = Text_cr(self.menu_left ,self.menu_left +250,screen_height*(3/5)+screen_height*(1/10),screen_height*(3/5),"GAME CLEAR!!")
        self.text_list.append(self.game_clear_title)
        self.life = 10
    def on_draw(self):# 화면 그리기
        """ Render the screen. """
        arcade.start_render()
        if self.check_game == True:
            # Draw our sprites
            self.wall_list.draw()
            self.background_list.draw()
            self.coin_list.draw()
            self.dont_touch_list.draw()
            self.monster_list.draw()
            self.platform_list.draw()
            self.foreground_list.draw()
            self.ladder_list.draw()
            self.player_list.draw()

            #레벨이 0이면 코인 표시 x
            if self.level != 0:
                coin_text = "Coin: {}".format(self.coin)     #남은 코인 표시
                life_text = "Life: {}".format(self.life)
                arcade.draw_text(coin_text, 10 + self.view_left, 30 + self.view_bottom,
                            arcade.csscolor.BLACK, 18)
                arcade.draw_text(life_text, 10 + self.view_left, 10 + self.view_bottom,
                            arcade.csscolor.BLACK, 18)

        else:
            arcade.start_render()
            if self.background_title: # 처음 화면 ( 메뉴화면 )
                    arcade.draw_texture_rectangle(int(1.5*(screen_width//3)), int(9.5*(screen_height//11)) , 274, 62, self.background_title) # x(가운데 ) , y(가운데), 전체 width, 전체 height
                    arcade.draw_texture_rectangle(screen_width//2,screen_height//2 , screen_width, screen_height, self.background)
            if self.button_list:
                for button in self.button_list:
                    button.draw_button()
            if self.text_list:
                for text in self.text_list:
                    text.draw_text()

    def process_keychange(self): # 키가 변경되었을 때

        if self.check_game == True:
        # 키 변경시 호출

        # 위  아래
            if self.up_pressed and not self.down_pressed:  # 위쪽 키 누름 / 아래 키 안눌림
                if self.player_physics_engine.is_on_ladder():# 사다리 위에 있으면 위로 이동
                    self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED

                elif self.player_physics_engine.can_jump()  and not self.jump_needs_reset:
                    # or self.player_physics_engine2.can_jump()
                    # 점프 가능한 상태이면 소리를 내면서 점프
                    self.player_sprite.change_y = PLAYER_JUMP_SPEED
                    self.jump_needs_reset = True
                    if self.sound_status:
                        arcade.play_sound(self.jump_sound)
                    self.player_sprite.jumping = True

                #3라운드
                # elif self.player_physics_engine2  and not self.jump_needs_reset:
                #     # or self.player_physics_engine2.can_jump()
                #     # 점프 가능한 상태이면 소리를 내면서 점프
                #     self.player_sprite.change_y = PLAYER_JUMP_SPEED
                #     self.jump_needs_reset = True
                #     arcade.play_sound(self.jump_sound)
                #     self.player_sprite.jumping = True

            elif self.down_pressed and not self.up_pressed: # 아랫쪽키 누름  / 위쪽 키 안눌림
                if self.player_physics_engine.is_on_ladder(): # 사다리 위에 있으면
                    self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED  #아래로 이동

            # 사다리에 있는 상태에서 위 / 아래
            if self.player_physics_engine.is_on_ladder():
                if not self.up_pressed and not self.down_pressed: # 둘다 안눌림
                    self.player_sprite.change_y = 0  # 가만히
                elif self.up_pressed and self.down_pressed:
                    self.player_sprite.change_y = 0  # 둘다 눌림 가만히

            # 왼쪽 오른쪽
            if self.right_pressed and not self.left_pressed:
                self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            elif self.left_pressed and not self.right_pressed:
                self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            else:
                self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):# 키가 눌렸을 때
        # 키가 눌리면 호출됨


        #눌렸으면 상태롤 True 로 변경
        if self.check_game == True:
            if key == arcade.key.UP or key == arcade.key.W:
                self.up_pressed = True
            elif key == arcade.key.DOWN or key == arcade.key.S:
                self.down_pressed = True
            elif key == arcade.key.LEFT or key == arcade.key.A:
                self.left_pressed = True
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.right_pressed = True
            elif key == arcade.key.O:
                arcade.pause(1)
            elif key ==arcade.key.P:
                arcade.quick_run(5)
            self.process_keychange()

    def on_key_release(self, key, modifiers):# 눌린키를 손에서 떗을 때
        # 키를 땔 때 불림

        # 키를 때면 상태를 False 로 적용.
        if self.check_game == True:
            if key == arcade.key.UP or key == arcade.key.W:
                self.up_pressed = False
                self.jump_needs_reset = False # 위쪽 키는 다시 점프 할 수 있게 상태를 만들기 위해서.
            elif key == arcade.key.DOWN or key == arcade.key.S:
                self.down_pressed = False
            elif key == arcade.key.LEFT or key == arcade.key.A:
                self.left_pressed = False
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.right_pressed = False

            self.process_keychange() # 키 적용

    def on_update(self, delta_time):# 이벤트 발생, 변수 등을 변경, 상태 체크
        """ Movement and game logic """
        if self.check_game == True:

            self.player_physics_engine.update()

            # See if we hit any coins
            coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                                self.coin_list)
            #코인을 먹으면
            for coin in coin_hit_list:
                print(coin_hit_list)
                # 코인을 먹으면 코인 삭제
                coin.remove_from_sprite_lists()
                # 코인을 먹으면 사운드
                if self.sound_status:
                    arcade.play_sound(self.collect_coin_sound)
                # 점수 +1점
                self.coin -= 1

            # Track if we need to change the viewport
            changed_viewport = False

            #플레이어가 맵에서 떨어질 경우( y좌표가 -100이하로 떨어질 경우)
            if self.player_sprite.center_y < -100:

                if self.sound_status:
                    arcade.play_sound(self.game_over)
                self.game_setup(self.level)  #현재 맵을 다시 그려줌

            #닿아서는 안될 곳을 닿을 경우 초기 좌표로
            if arcade.check_for_collision_with_list(self.player_sprite, self.dont_touch_list):
                self.life-=1    #목숨 -1
                if self.sound_status:
                    arcade.play_sound(self.game_over)
                self.game_setup(self.level)  #현재 맵을 다시 그려줌

            if self.level == 2 or self.level == 4:
                if arcade.check_for_collision_with_list(self.player_sprite, self.platform_list):
                    self.life-=1
                    if self.sound_status:
                        arcade.play_sound(self.game_over)
                    self.game_setup(self.level)  #현재 맵을 다시 그려줌


            # 몬스터 맴돌게 하기
            for i in range(len(self.monster)):
                self.monster_physics_engine[i].update() #업데이트
                self.monster_sprite[i].change_x = self.monster[i].moveMonster()

            for i in range(len(self.platform)):
                self.platform_physics_engine[i].update()    #업데이트

                #플랫폼 맴돌게 하기
                self.platform_sprite[i].change_x = self.platform[i].movePlatform()

                #플랫폼 떨어트리기
                if self.platform[i].fall == True:
                    #돌 떨어트리기
                    if self.level == 2:
                        if(80 > (self.platform_sprite[i].center_x - self.player_sprite.center_x ) > 40):
                            self.platform_physics_engine[i] = arcade.PhysicsEnginePlatformer(self.platform_sprite[i],self.wall_list,GRAVITY)
                    elif self.level == 4 or self.level == 5:
                        #2층 번개
                        if i == 0:
                            if(40 > (self.platform_sprite[0].center_x - self.player_sprite.center_x ) > 30 and self.player_sprite.center_y >= 300):
                                self.platform_physics_engine[0] = arcade.PhysicsEnginePlatformer(self.platform_sprite[0],self.wall_list,GRAVITY)
                        #3층 번개
                        elif self.platform[i].die == True:
                            if(70 > (self.platform_sprite[i].center_x - self.player_sprite.center_x ) > 60 and self.player_sprite.center_y >= 550):
                                self.platform_physics_engine[i] = arcade.PhysicsEnginePlatformer(self.platform_sprite[i],self.wall_list,GRAVITY)

                #딱딱한 플랫폼이면 위에 서기(플랫폼과 플레이어가 부딪히고, 하드플랫폼이면 platform_list에 중력)
                #왜 마지막 애만 중력받지?
                if arcade.check_for_collision(self.player_sprite, self.platform_sprite[i]) and self.platform[i].hard_platform == True and self.player_sprite.center_y:
                    self.player_physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,self.platform_list, gravity_constant=GRAVITY,ladders=self.ladder_list)
                #플랫폼에 안닿았거나 하드플랫폼이 아니거나 그외일 경우
                elif not arcade.check_for_collision(self.player_sprite, self.platform_sprite[i]):
                    self.player_physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,self.wall_list, gravity_constant=GRAVITY,ladders=self.ladder_list)

                #플랫폼에 닿았을 때
                if arcade.check_for_collision(self.player_sprite, self.platform_sprite[i]):

                     #떨어지고 죽는 플랫폼인 경우
                    if self.platform[i].fall == True and self.platform[i].die == True:
                        self.life-=1
                        arcade.play_sound(self.game_over)
                        self.game_setup(self.level)  #현재 맵을 다시 그려줌
                    if self.level == 5:
                        #텔레포트 기능
                        if self.platform[i].teleport == True and self.player_sprite.center_y > 320:         #아래 텔레포트
                            time.sleep(0.5)

                            self.player_sprite.center_x = 180
                            self.player_sprite.center_y = 650
                        elif self.platform[i].teleport == False and self.player_sprite.center_y > 650:      #윗 텔레포트
                            self.player_sprite.center_x = 2300
                            self.player_sprite.center_y = 310


            #몬스터에 닿였을 때
            if arcade.check_for_collision_with_list(self.player_sprite, self.monster_list):
                self.life-=1
                if self.sound_status:
                    arcade.play_sound(self.game_over)
                self.game_setup(self.level)  #현재 맵을 다시 그려줌

            #목숨0
            if self.life == 0:
                self.level = 1
                self.bool_life = True
                if self.sound_status:
                    arcade.play_sound(self.game_over)
                self.go_to_over()  #게임 오버

            if self.level == 5 and self.coin == 0: # 수정
                self.player_sprite.center_x = 0
                self.player_sprite.center_y = 0
                self.go_to_game_clear()
                self.level =1
            # 플레이어의 x좌표가 게임의 마지막 좌표를 넘을 경우
            if self.player_sprite.center_x >= self.end_of_map and self.coin == 0:
                # Advance to the next level
                self.level += 1     #다음 맵으로 넘어가기 위해
                # if self.level == 5:
                self.game_setup(self.level)  #다음 맵을 로드함
                # else :
                    # self.game_setup(self.level)
                #카메라 시작점을 설정
                self.view_left = 0
                self.view_bottom = 0
                changed_viewport = True

            # --- Manage Scrolling ---
            # 점프  이 부분의 로직을 완벽히 이해하기 위에서는 API 를 분석할 필요가 있음
            if self.player_physics_engine.can_jump(): # 물리엔진이 점프 가능하면
                self.player_sprite.can_jump = False # 유저 False --> 점프 가능

            else:
                self.player_sprite.can_jump = True # 유저 점프 불가능


            # 물리엔진이 판단해여 사다리에 있고, 점프가 불가능하면
            if self.player_physics_engine.is_on_ladder() and not self.player_physics_engine.can_jump():

                self.player_sprite.is_on_ladder = True
                self.process_keychange()
            else:# 없으면 유저는 사다리 에 없다 False
                self.player_sprite.is_on_ladder = False
                self.process_keychange()

            # 애니메이션 업데이트
            self.coin_list.update_animation(delta_time)
            self.background_list.update_animation(delta_time)
            self.player_list.update_animation(delta_time)
            # Scroll left
            left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN + 300
            if self.player_sprite.left < left_boundary:
                self.view_left -= left_boundary - self.player_sprite.left
                changed_viewport = True

            # Scroll right
            right_boundary = self.view_left + screen_width - RIGHT_VIEWPORT_MARGIN  -300
            if self.player_sprite.right > right_boundary:
                self.view_left += self.player_sprite.right - right_boundary
                changed_viewport = True

            # Scroll up
            top_boundary = self.view_bottom + screen_height - TOP_VIEWPORT_MARGIN  -300
            if self.player_sprite.top > top_boundary:
                self.view_bottom += self.player_sprite.top - top_boundary
                changed_viewport = True

            # Scroll down
            bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
            if self.player_sprite.bottom < bottom_boundary:
                self.view_bottom -= bottom_boundary - self.player_sprite.bottom
                changed_viewport = True

            if changed_viewport:
                # Only scroll to integers. Otherwise we end up with pixels that
                # don't line up on the screen
                self.view_bottom = int(self.view_bottom)
                self.view_left = int(self.view_left)

                # Do the scrolling
                arcade.set_viewport(self.view_left,
                                    screen_width + self.view_left,
                                    self.view_bottom,
                                    screen_height + self.view_bottom)
        else:
            arcade.set_viewport(0,screen_width, 0, screen_height)
    def on_mouse_press(self, x, y, button, key_modifiers):# 마우스가 눌렸을 때
            if not self.check_game :
                check_mouse_press_buttons(x, y, self.button_list)
    def on_mouse_release(self, x, y, button, key_modifiers):# 누른 마우스를 손에서 땟을 때
        if not self.check_game :
            check_mouse_release_buttons(x, y, self.button_list)

    def game_start(self):# 게임 시작
        self.level = 5
        self.game_setup(self.level)
        self.check_game= True
        self.check_menu= False

    def go_to_option(self):# 옵션 화면 으로 가는 이벤트 콜백함수
        self.option_setup()
        self.check_option = True
        self.check_menu= False
        self.background = 0
        self.background_title =0
    def go_to_menu(self):# 메뉴 화면 으로 가는 이벤트 콜백함수
        self.menu_setup()
        self.check_menu= True
        self.check_option = False
        self.check_rule = False
    def go_to_rule(self):# 규칙 화면 으로 가는 이벤트 콜백함수
        self.rule_setup()
        self.check_menu = False
        self.check_rule = True
        self.background = 0
        self.background_title =0
    def go_to_over(self):# 게임오버 화면 으로 가는 이벤트 콜백함수
        self.game_over_setup()
        self.check_game = False
    def go_to_game_clear(self):# 게임 클리어 화면으로 가는 이벤트 콜백함수
        self.game_clear_setup()
        self.check_game = False
        # self.go_to_menu()
    def size_up(self):# 화면 사이즈 업 이벤트 콜백함수
        global count
        # , screen_width, screen_height
        if count <4:
            count +=1
            arcade.Window.set_size(self,screen_size[count]["width"] , screen_size[count]["height"])
            self.text_size.text = "{} X {}".format(screen_size[count]["width"],screen_size[count]["height"])
            # screen_width = screen_size[count]["width"]
            # screen_height = screen_size[count]["height"]
            fit_size(screen_size[count]["width"],screen_size[count]["height"])
            self.option_setup()
            print("left: {}   right : {}".format(self.title_option.left,self.title_option.right))
            print("top: {}   bottom : {}".format(self.title_option.top,self.title_option.bottom))
            # self.button_list.update()
            # self.title_list.update()
    def size_down(self):# 화면 사이즈 다운 이벤트 콜백함수
        global count, screen_width, screen_height
        if count >1:
            count -=1
            arcade.Window.set_size(self,screen_size[count]["width"] , screen_size[count]["height"])
            self.text_size.text = "{} X {}".format(screen_size[count]["width"],screen_size[count]["height"])

            fit_size(screen_size[count]["width"],screen_size[count]["height"])

            self.option_setup()
            print("left: {}   right : {}".format(self.title_option.left,self.title_option.right))
            print("top: {}   bottom : {}".format(self.title_option.top,self.title_option.bottom))

        # arcade.Window.maximize(self)
    def sound_on_off(self):# 사운드 온/오프 이벤트 콜백 함수
        if self.status_sound.text == "ON":
            self.status_sound.text = "OFF"
            self.sound_status = False
            # self.collect_coin_sound = 0
            # self.jump_sound = 0
            # self.game_over = 0
        else:
            self.status_sound.text = "ON"
            self.sound_status = True
            # self.collect_coin_sound = arcade.load_sound("sounds/coin1.wav")
            # self.jump_sound = arcade.load_sound("sounds/jump1.wav")
            # self.game_over = arcade.load_sound("sounds/gameover1.wav")

    def map_level_1(self): # 1번 맵 로딩 함수
        self.coin = 4
    def map_level_2(self):# 2번 맵 로딩 함수
        self.coin = 4
        self.monster.append(Monster.Monster("bee",800,420, CHARACTER_SCALING * 0.5, MONSTER_MOVEMENT_SPEED, 800, 930))
        for i in range(len(self.monster)):
            self.monster_sprite.append(self.monster[i].newMonster())
            self.monster_list.append(self.monster_sprite[i])
        self.platform.append(Platform.Platform("rock",690,700, CHARACTER_SCALING * 0.5, fall = True, die = True))
        for i in range(len(self.platform)):
            self.platform_sprite.append(self.platform[i].newPlatform())
            self.platform_list.append(self.platform_sprite[i])
    def map_level_3(self):# 3번 맵 로딩 함수
        self.coin = 4
        self.monster.append(Monster.Monster("bee",400,150, CHARACTER_SCALING * 0.5, MONSTER_MOVEMENT_SPEED*2, 300, 1000))
        self.platform.append(Platform.Platform("bridgeA",400,50, CHARACTER_SCALING * 0.5,PLATFORM_MOVEMENT_SPEED, 300, 1200, hard_platform = True))
        for i in range(len(self.platform)):
            self.platform_sprite.append(self.platform[i].newPlatform())
            self.platform_list.append(self.platform_sprite[i])
        for i in range(len(self.monster)):
            self.monster_sprite.append(self.monster[i].newMonster())
            self.monster_list.append(self.monster_sprite[i])
    def map_level_4(self):# 4번 맵 로딩 함수
        self.coin = 6

        self.monster.append(Monster.Monster("bee",156,430, CHARACTER_SCALING * 0.5, MONSTER_MOVEMENT_SPEED*3, 156, 348))
        self.monster.append(Monster.Monster("bee",1000,430, CHARACTER_SCALING * 0.5, MONSTER_MOVEMENT_SPEED*3, 800, 1000))
        self.platform.append(Platform.Platform("rock",1050, 1160, CHARACTER_SCALING * 0.5,fall = True, die = True))
        #몬스터
        for i in range(len(self.monster)):
            self.monster_sprite.append(self.monster[i].newMonster())
            self.monster_list.append(self.monster_sprite[i])
        #플랫폼
        for i in range(len(self.platform)):
            self.platform_sprite.append(self.platform[i].newPlatform())
            self.platform_list.append(self.platform_sprite[i])
    def map_level_5(self):# 5번 맵 로딩 함수
        self.coin = 1
        #몬스터
        self.monster.append(Monster.Monster("mouse",1900,300, CHARACTER_SCALING * 0.5, MONSTER_MOVEMENT_SPEED*3, 300, 2400))
        self.monster.append(Monster.Monster("wormGreen",2400,300, CHARACTER_SCALING * 0.5, MONSTER_MOVEMENT_SPEED*3, 300, 2400))
        self.monster.append(Monster.Monster("bee",1100,450, CHARACTER_SCALING * 0.5, MONSTER_MOVEMENT_SPEED*3, 300, 1200))
        self.monster.append(Monster.Monster("bee",600,450, CHARACTER_SCALING * 0.5, MONSTER_MOVEMENT_SPEED*3, 1200, 2400))
        self.monster.append(Monster.Monster("bee",500,1000, CHARACTER_SCALING * 0.5, MONSTER_MOVEMENT_SPEED*3, 600, 1200))
        self.monster.append(Monster.Monster("bee",800,1000, CHARACTER_SCALING * 0.5, MONSTER_MOVEMENT_SPEED*3, 1200, 2400))
        #플랫폼

        self.platform.append(Platform.Platform("thunder",1080,900, CHARACTER_SCALING * 0.5,fall = True, die = True))   #2층에서 내리는 번개
        self.platform.append(Platform.Platform("doorClosed_mid",2400,290, CHARACTER_SCALING * 0.5, teleport = True))   #아래 텔레포트
        self.platform.append(Platform.Platform("doorClosed_mid",50,610, CHARACTER_SCALING * 0.5, teleport = False))   #윗 텔레포트
        #3층 번개
        for i in range(1):
            self.platform.append(Platform.Platform("thunder",288+ (i*128),800, CHARACTER_SCALING * 0.5, fall = True,  die = True))
        for i in range(1):
            self.platform.append(Platform.Platform("thunder",358+ ( (14 + i)*64),800, CHARACTER_SCALING * 0.5, fall = True,  die = True))
        self.platform.append(Platform.Platform("thunder",1900,820, CHARACTER_SCALING, fall = True,  die = True))

        self.platform.append(Platform.Platform("bridgeA",400,930, CHARACTER_SCALING * 0.5,PLATFORM_MOVEMENT_SPEED*4, 400, 2200, hard_platform = True))
        #몬스터
        for i in range(len(self.monster)):
            self.monster_sprite.append(self.monster[i].newMonster())
            self.monster_list.append(self.monster_sprite[i])
        #플랫폼
        for i in range(len(self.platform)):
            self.platform_sprite.append(self.platform[i].newPlatform())
            self.platform_list.append(self.platform_sprite[i])
    def map_level_6(self):# 6번 맵(클리어) 로딩 함수 --> 화면 위치를 x = 0 , y= 0 으로 맞추기 위한 함수
        self.coin=1

def main(): # 메인 함수
    """ Main method """
    window = MyGame() # 메인 게임 생성

    arcade.run() # arcade 스레드 실행 ( 게임 실행 )


#현 클래스가 메인클래스이면 main()함수 실행
if __name__ == "__main__":
    main()
