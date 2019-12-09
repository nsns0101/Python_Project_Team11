import arcade

def default():
    pass

class Button_cr:#arcade.Texture

    def __init__(self, left_x,right_x,top,bottom,text,color,action=default,size=50):
        self.left = left_x      # 왼쪽 x
        self.right = right_x    # 오른쪽 x
        self.top = top          # 윗쪽 y
        self.bottom = bottom    # 아랫쪽 y
        self.color = color      # 버튼 색
        self.pressed = False    # 눌린 상태
        self.f_color = color    # 글자 색
        self.text = text        # 글자
        self.action = action    # 액션 이벤트
        self.size = size        # 크기
    def draw_button(self): # 버튼 생성

        if not self.pressed:
            self.color = self.f_color
        else:
            self.color = arcade.color.BATTLESHIP_GREY

        arcade.draw_lrtb_rectangle_filled(self.left,self.right,self.top,self.bottom, self.color)
        arcade.draw_text(self.text, (self.left + self.right)//2, (self.top + self.bottom)//2 , arcade.color.BLACK,self.size, align="center", anchor_x="center", anchor_y="center")
        # print((self.left + self.right)//2)

    def on_press(self): # 눌리면
        self.pressed = True
        self.action()
        print("이벤트 실행")

    def on_release(self): # 때면
        self.pressed = False

def check_mouse_press_buttons(x, y, button_list): # 마우스 이벤트
    for button in button_list:
        if  button.left <= x <= button.right:
            if button.bottom <= y <= button.top:
                button.on_press()
        else:
            continue
def check_mouse_release_buttons(_x, _y, button_list): # 마우스 를 땟을 때
    for button in button_list:
        if button.pressed:
            button.on_release()

class Text_cr:
    def __init__(self, left, right, top , bottom, text, color=arcade.color.BLACK,size=50):
        self.left = left        # 왼쪽 x
        self.right = right      # 오른쪽 x
        self.top = top          # 윗쪽 x
        self.bottom = bottom    # 아랫쪽 y
        self.text = text        # text
        self.color = color      # 색
        self.size = size        # 크기
    def draw_text(self): # 텍스트 생성
        arcade.draw_text(self.text, (self.left + self.right)//2, (self.top + self.bottom)//2 , self.color, self.size, align="center", anchor_x="center", anchor_y="center")
