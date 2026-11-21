import pygame
import random
import math
import json
import os
from datetime import date
from array import array

pygame.init()

# ============================================================
# SNAKE GAME 4.0 - built on the user's Snake Game 3.2
# Keeps touch controls, store, missions, music, save data and
# adds golden apples, powers, levels, obstacles, daily chest,
# rare skins, achievements and records.
# ============================================================

info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
pygame.display.set_caption("Snake Game 4.0")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 30)
big = pygame.font.SysFont(None, 55)
small = pygame.font.SysFont(None, 23)
tiny = pygame.font.SysFont(None, 19)

WHITE = (245, 245, 245)
GREEN = (70, 220, 130)
DARK_GREEN = (30, 150, 90)
BLUE = (65, 130, 230)
RED = (255, 85, 100)
YELLOW = (255, 210, 90)
GRAY = (90, 105, 125)
GOLD = (255, 190, 35)
CYAN = (80, 220, 245)

DATA_FILE = "snake_data.json"
BEST_FILE = "snake_best.txt"
today = str(date.today())

# ---------- STORE CATALOG ----------
skins = [
    {"name": "GREEN", "color": (70,220,130), "price": 0},
    {"name": "BLUE", "color": (65,150,255), "price": 10},
    {"name": "GOLD", "color": (255,205,65), "price": 20},
    {"name": "PURPLE", "color": (190,100,255), "price": 30},
    {"name": "FIRE", "color": (255,95,45), "price": 65},
    {"name": "ICE", "color": (100,235,255), "price": 80},
    {"name": "SHADOW", "color": (155,145,185), "price": 110},
    {"name": "RAINBOW", "color": (255,110,190), "price": 150},
]
backgrounds = [
    {"name": "DARK BLUE", "color": (12,20,35), "price": 0},
    {"name": "BLACK", "color": (5,5,10), "price": 15},
    {"name": "PURPLE", "color": (30,15,48), "price": 25},
    {"name": "SPACE", "color": (8,12,38), "price": 40},
    {"name": "FOREST", "color": (8,35,28), "price": 65},
    {"name": "SUNSET", "color": (55,24,35), "price": 85},
]

coins = 0
owned_skins = [0]
owned_backgrounds = [0]
selected_skin = 0
selected_background = 0
best_score = 0
daily_food = 0
daily_games = 0
claimed = []
chest_claimed = False
total_food = 0
total_games = 0
total_coins_earned = 0
achievement_claimed = []
max_level = 1
record_level = 1
missions = [
    {"name": "Eat 5 food", "target": 5, "reward": 10, "type": "food"},
    {"name": "Eat 15 food", "target": 15, "reward": 25, "type": "food"},
    {"name": "Play 3 games", "target": 3, "reward": 20, "type": "games"},
]

achievements = [
    {"name":"First Bite", "desc":"Eat your first apple", "goal":1, "type":"food", "reward":10},
    {"name":"Apple Fan", "desc":"Eat 50 apples total", "goal":50, "type":"food", "reward":35},
    {"name":"Snake Veteran", "desc":"Play 10 games", "goal":10, "type":"games", "reward":40},
    {"name":"Coin Collector", "desc":"Earn 100 coins total", "goal":100, "type":"coins", "reward":50},
    {"name":"Level Climber", "desc":"Reach level 5", "goal":5, "type":"level", "reward":60},
    {"name":"High Scorer", "desc":"Score 25 in one game", "goal":25, "type":"score", "reward":75},
]

def save_data():
    data = {
        "coins": coins, "owned_skins": owned_skins,
        "owned_backgrounds": owned_backgrounds,
        "selected_skin": selected_skin,
        "selected_background": selected_background,
        "daily_date": today, "daily_food": daily_food,
        "daily_games": daily_games, "claimed": claimed,
        "chest_claimed": chest_claimed,
        "total_food": total_food, "total_games": total_games,
        "total_coins_earned": total_coins_earned,
        "achievement_claimed": achievement_claimed,
        "max_level": max_level, "record_level": record_level
    }
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

def load_data():
    global coins, owned_skins, owned_backgrounds, selected_skin
    global selected_background, daily_food, daily_games, claimed
    global chest_claimed, total_food, total_games, total_coins_earned
    global achievement_claimed, max_level, record_level
    try:
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
        coins = max(0, int(d.get("coins", 0)))
        owned_skins = d.get("owned_skins", [0])
        owned_backgrounds = d.get("owned_backgrounds", [0])
        selected_skin = int(d.get("selected_skin", 0))
        selected_background = int(d.get("selected_background", 0))
        total_food = int(d.get("total_food", 0))
        total_games = int(d.get("total_games", 0))
        total_coins_earned = int(d.get("total_coins_earned", 0))
        achievement_claimed = d.get("achievement_claimed", [])
        max_level = int(d.get("max_level", 1))
        record_level = int(d.get("record_level", 1))
        if d.get("daily_date", today) == today:
            daily_food = int(d.get("daily_food", 0))
            daily_games = int(d.get("daily_games", 0))
            claimed = d.get("claimed", [])
            chest_claimed = bool(d.get("chest_claimed", False))
        else:
            daily_food = daily_games = 0
            claimed = []
            chest_claimed = False
        if 0 not in owned_skins: owned_skins.append(0)
        if 0 not in owned_backgrounds: owned_backgrounds.append(0)
        owned_skins = [i for i in owned_skins if isinstance(i,int) and 0 <= i < len(skins)]
        owned_backgrounds = [i for i in owned_backgrounds if isinstance(i,int) and 0 <= i < len(backgrounds)]
        if selected_skin not in owned_skins: selected_skin = 0
        if selected_background not in owned_backgrounds: selected_background = 0
    except:
        pass

load_data()
try:
    with open(BEST_FILE, "r") as f: best_score = int(f.read())
except:
    best_score = 0

def save_best():
    try:
        with open(BEST_FILE, "w") as f: f.write(str(best_score))
    except:
        pass

# ---------- SOUND ----------
music_channel = None
eat_sound = None
gold_sound = None
lose_sound = None
music_index = 1
music_levels = [0, 0.025, 0.05]
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    def make_tone(freq, duration, volume=0.045):
        rate = 22050
        samples = array("h")
        count = int(rate * duration)
        for i in range(count):
            t = i / rate
            fade = min(1, i/180) * max(0, 1-i/count)
            samples.append(int(32767 * volume * fade * math.sin(2*math.pi*freq*t)))
        return pygame.mixer.Sound(buffer=samples.tobytes())
    eat_sound = make_tone(590, 0.16, 0.045)
    gold_sound = make_tone(880, 0.32, 0.055)
    lose_sound = make_tone(260, 0.25, 0.035)
    rate = 22050
    notes = [261.63,329.63,392,329.63,293.66,349.23,440,349.23]
    samples = array("h")
    for i in range(rate*16):
        t=i/rate
        n=int(t/2)%len(notes)
        wave=math.sin(2*math.pi*notes[n]*t)+0.2*math.sin(2*math.pi*notes[n]/2*t)
        samples.append(int(32767*wave*0.012))
    music = pygame.mixer.Sound(buffer=samples.tobytes())
    music_channel = music.play(-1)
except:
    pass

def sound(s):
    if s:
        try: s.play()
        except: pass

def update_music():
    if music_channel:
        try: music_channel.set_volume(music_levels[music_index])
        except: pass
update_music()

# ---------- RESPONSIVE BOARD AND CONTROLS ----------
CONTROL_H = min(int(H*0.46), max(276, int(H*0.40)))
BOARD_H = H-CONTROL_H
SIZE = max(15, min(20, W//20))
COLS = max(5, W//SIZE)
BOARD_W = COLS*SIZE
BOARD_X = (W-BOARD_W)//2
BOARD_Y = 120
ROWS = max(5, (BOARD_H-150)//SIZE)
BOARD_H_CELLS = ROWS*SIZE
CX = W//2

top_y = BOARD_H+8
row_button_h = 40
pause_btn = pygame.Rect(10,top_y,W//2-18,row_button_h)
restart_btn = pygame.Rect(W//2+8,top_y,W//2-18,row_button_h)
shop_y=top_y+48
store_btn=pygame.Rect(10,shop_y,W//2-18,row_button_h)
missions_btn=pygame.Rect(W//2+8,shop_y,W//2-18,row_button_h)
music_btn=pygame.Rect(CX-82,top_y+96,164,30)
bw=min(145,max(95,int(W*0.22)))
bh=min(60,max(40,int(CONTROL_H*0.14)))
hg=max(38,int(W*0.085))
vg=max(9,min(18,int(CONTROL_H*0.03)))
arrow_y=top_y+min(128,max(118,CONTROL_H-8-3*bh-2*vg))
buttons={
    "UP":pygame.Rect(CX-bw//2,arrow_y,bw,bh),
    "LEFT":pygame.Rect(CX-bw-hg//2,arrow_y+bh+vg,bw,bh),
    "RIGHT":pygame.Rect(CX+hg//2,arrow_y+bh+vg,bw,bh),
    "DOWN":pygame.Rect(CX-bw//2,arrow_y+2*(bh+vg),bw,bh)
}
start_btn=pygame.Rect(CX-105,BOARD_Y+300,210,60)
# Menu buttons are recalculated to match the full-screen menu layout.
_menu_w = min(W-70, 250)
_menu_h = min(62, max(48, int(H*0.045)))
_menu_gap = max(12, int(H*0.012))
_menu_y = int(H*0.47)
_menu_total = 5*_menu_h + 4*_menu_gap
if _menu_y + _menu_total > H-45:
    _menu_y = max(int(H*0.39), (H-_menu_total)//2)
start_btn = pygame.Rect(CX-_menu_w//2, _menu_y, _menu_w, _menu_h)
menu_store_btn = pygame.Rect(CX-_menu_w//2, _menu_y+(_menu_h+_menu_gap), _menu_w, _menu_h)
menu_missions_btn = pygame.Rect(CX-_menu_w//2, _menu_y+2*(_menu_h+_menu_gap), _menu_w, _menu_h)
menu_chest_btn = pygame.Rect(CX-_menu_w//2, _menu_y+3*(_menu_h+_menu_gap), _menu_w, _menu_h)
menu_ach_btn = pygame.Rect(CX-_menu_w//2, _menu_y+4*(_menu_h+_menu_gap), _menu_w, _menu_h)
back_btn=pygame.Rect(12,BOARD_Y+12,100,42)
skin_tab=pygame.Rect(10,BOARD_Y+75,W//2-15,42)
bg_tab=pygame.Rect(W//2+5,BOARD_Y+75,W//2-15,42)
item_width=min(300,W-30)
item_rects=[pygame.Rect(CX-item_width//2,BOARD_Y+135+i*83,item_width,72) for i in range(8)]

# ---------- GAME STATE ----------
state="menu"
return_state="menu"
shop_category="skins"
score=0
move_timer=0
turn_locked=False
snake=[]
food=None
golden_food=None
direction=(1,0)
next_direction=(1,0)
obstacles=[]
powerup=None
power_type=None
power_timer=0
shield_timer=0
magnet_timer=0
turbo_timer=0
level=1
foods_this_level=0
last_record_saved=0
notice=""
notice_timer=0

def draw_text(value,fnt,color,x,y):
    img=fnt.render(str(value),True,color)
    screen.blit(img,img.get_rect(center=(x,y)))

def draw_button(rect,label,color,size=28):
    pygame.draw.rect(screen,color,rect,border_radius=12)
    pygame.draw.rect(screen,WHITE,rect,2,border_radius=12)
    draw_text(label,pygame.font.SysFont(None,size),WHITE,rect.centerx,rect.centery)

def draw_arrow(rect,name):
    cx,cy=rect.center
    s=min(21,max(15,rect.height//3))
    pygame.draw.rect(screen,BLUE,rect,border_radius=13)
    pygame.draw.rect(screen,WHITE,rect,2,border_radius=13)
    if name=="UP": p=[(cx,cy-s),(cx-s,cy+s),(cx+s,cy+s)]
    elif name=="DOWN": p=[(cx,cy+s),(cx-s,cy-s),(cx+s,cy-s)]
    elif name=="LEFT": p=[(cx-s,cy),(cx+s,cy-s),(cx+s,cy+s)]
    else: p=[(cx+s,cy),(cx-s,cy-s),(cx-s,cy+s)]
    pygame.draw.polygon(screen,WHITE,p)

def cell_rect(cell):
    return pygame.Rect(BOARD_X+cell[0]*SIZE,BOARD_Y+cell[1]*SIZE,SIZE,SIZE)

def random_empty():
    occupied=set(snake)|set(obstacles)
    if food: occupied.add(food)
    if golden_food: occupied.add(golden_food)
    if powerup: occupied.add(powerup)
    empty=[(x,y) for x in range(COLS) for y in range(ROWS) if (x,y) not in occupied]
    return random.choice(empty) if empty else None

def create_food():
    return random_empty()

def create_obstacles():
    global obstacles
    obstacles=[]
    # Obstacles grow with level, but leave the starting snake clear.
    count=min(2+(level-1)*2, 18)
    safe={(COLS//2,ROWS//2),(COLS//2-1,ROWS//2),(COLS//2-2,ROWS//2)}
    for _ in range(count*4):
        if len(obstacles)>=count: break
        p=(random.randint(1,max(1,COLS-2)),random.randint(1,max(1,ROWS-2)))
        if p not in safe and p not in obstacles: obstacles.append(p)

def spawn_powerup():
    global powerup,power_type
    if random.random()<0.58:
        powerup=random_empty()
        power_type=random.choice(["shield","magnet","turbo"])
    else:
        powerup=None
        power_type=None

def reset_game(mode="playing"):
    global snake,direction,next_direction,turn_locked,score,move_timer
    global food,golden_food,obstacles,powerup,power_type,power_timer
    global shield_timer,magnet_timer,turbo_timer,level,foods_this_level
    snake=[(COLS//2,ROWS//2),(COLS//2-1,ROWS//2),(COLS//2-2,ROWS//2)]
    direction=next_direction=(1,0)
    turn_locked=False
    score=0
    move_timer=0
    level=1
    foods_this_level=0
    golden_food=None
    powerup=None
    power_type=None
    power_timer=shield_timer=magnet_timer=turbo_timer=0
    create_obstacles()
    food=create_food()
    state=mode

def start_game():
    global daily_games,total_games
    reset_game("playing")
    daily_games+=1
    total_games+=1
    save_data()
    if music_channel:
        try: music_channel.unpause()
        except: pass

def change_direction(name):
    global next_direction,turn_locked
    if state!="playing" or turn_locked: return
    dirs={"UP":(0,-1),"DOWN":(0,1),"LEFT":(-1,0),"RIGHT":(1,0)}
    new=dirs[name]
    if new==(-direction[0],-direction[1]): return
    if new!=direction:
        next_direction=new
        turn_locked=True

def draw_snake():
    color=skins[selected_skin]["color"]
    for i,part in enumerate(snake):
        rect=cell_rect(part).inflate(-2,-2)
        if selected_skin in (1,3,5,6,7):
            pygame.draw.circle(screen,color,rect.center,max(3,SIZE//2-1))
        else:
            pygame.draw.rect(screen,color,rect,border_radius=5)
        if selected_skin==2: pygame.draw.rect(screen,YELLOW,rect,1,border_radius=4)
        if selected_skin==4:
            pygame.draw.circle(screen,(255,205,70),rect.center,3)
        if i==0:
            pygame.draw.circle(screen,WHITE,rect.center,3)
    if shield_timer>0 and snake:
        pygame.draw.circle(screen,CYAN,cell_rect(snake[0]).center,SIZE,2)

def draw_board():
    pygame.draw.rect(screen,(20,32,49),(BOARD_X,BOARD_Y,BOARD_W,BOARD_H_CELLS),border_radius=8)
    # Subtle grid
    for x in range(COLS+1):
        px=BOARD_X+x*SIZE
        pygame.draw.line(screen,(26,41,59),(px,BOARD_Y),(px,BOARD_Y+BOARD_H_CELLS),1)
    for y in range(ROWS+1):
        py=BOARD_Y+y*SIZE
        pygame.draw.line(screen,(26,41,59),(BOARD_X,py),(BOARD_X+BOARD_W,py),1)
    for p in obstacles:
        r=cell_rect(p).inflate(-2,-2)
        pygame.draw.rect(screen,(115,85,75),r,border_radius=4)
        pygame.draw.rect(screen,(175,125,95),r,2,border_radius=4)
    if food:
        pygame.draw.circle(screen,RED,cell_rect(food).center,SIZE//2-2)
        pygame.draw.circle(screen,(255,180,180),(cell_rect(food).centerx-2,cell_rect(food).centery-3),2)
    if golden_food:
        pygame.draw.circle(screen,GOLD,cell_rect(golden_food).center,SIZE//2-1)
        pygame.draw.circle(screen,WHITE,cell_rect(golden_food).center,SIZE//3,2)
    if powerup:
        c=cell_rect(powerup).center
        col={"shield":CYAN,"magnet":(255,100,190),"turbo":(255,150,50)}.get(power_type,YELLOW)
        pygame.draw.circle(screen,col,c,SIZE//2-1)
        symbol={"shield":"S","magnet":"M","turbo":"T"}.get(power_type,"?")
        draw_text(symbol,tiny,(20,25,35),c[0],c[1])
    if snake: draw_snake()

def draw_menu():
    draw_text("WELCOME!",big,YELLOW,CX,BOARD_Y+90)
    draw_text("SNAKE GAME",big,GREEN,CX,BOARD_Y+145)
    draw_text("Coins: "+str(coins),font,YELLOW,CX,BOARD_Y+205)
    draw_button(start_btn,"START",DARK_GREEN,38)
    draw_button(menu_store_btn,"STORE",BLUE,28)
    draw_button(menu_missions_btn,"MISSIONS",GRAY,27)
    draw_button(menu_chest_btn,"DAILY CHEST", (150,105,35),26)
    draw_button(menu_ach_btn,"ACHIEVEMENTS", (100,75,155),26)

def draw_shop():
    draw_text("GAME STORE",big,YELLOW,CX,BOARD_Y+42)
    draw_text("Coins: "+str(coins),font,WHITE,CX,BOARD_Y+60)
    draw_button(back_btn,"BACK",GRAY,25)
    draw_button(skin_tab,"SNAKE SKINS",BLUE if shop_category=="skins" else GRAY,22)
    draw_button(bg_tab,"BACKGROUNDS",BLUE if shop_category=="backgrounds" else GRAY,22)
    items=skins if shop_category=="skins" else backgrounds
    owned=owned_skins if shop_category=="skins" else owned_backgrounds
    selected=selected_skin if shop_category=="skins" else selected_background
    for i,item in enumerate(items):
        rect=item_rects[i]
        pygame.draw.rect(screen,(25,39,58),rect,border_radius=12)
        pygame.draw.rect(screen,item["color"],(rect.x+9,rect.y+9,42,54),border_radius=9)
        draw_text(item["name"],small,WHITE,rect.centerx+2,rect.y+21)
        label=("SELECTED" if selected==i else "USE") if i in owned else str(item["price"])+" COINS"
        draw_button(pygame.Rect(rect.right-112,rect.y+39,103,28),label,DARK_GREEN if i in owned else BLUE,18)

def draw_missions():
    draw_button(back_btn,"BACK",GRAY,25)
    draw_text("DAILY MISSIONS",big,YELLOW,CX,BOARD_Y+65)
    draw_text("Coins: "+str(coins),font,WHITE,CX,BOARD_Y+100)
    for i,m in enumerate(missions):
        rect=item_rects[i]
        pygame.draw.rect(screen,(25,39,58),rect,border_radius=12)
        progress=min(daily_food if m["type"]=="food" else daily_games,m["target"])
        draw_text(m["name"],small,WHITE,rect.centerx-20,rect.y+20)
        draw_text(str(progress)+"/"+str(m["target"]),small,YELLOW,rect.centerx-20,rect.y+49)
        label="CLAIMED" if i in claimed else ("CLAIM" if progress>=m["target"] else str(m["reward"])+" COINS")
        action=pygame.Rect(rect.right-112,rect.y+39,103,28)
        draw_button(action,label,DARK_GREEN if progress>=m["target"] and i not in claimed else GRAY,18)

def draw_chest():
    draw_button(back_btn,"BACK",GRAY,25)
    draw_text("DAILY REWARD",big,YELLOW,CX,BOARD_Y+95)
    pygame.draw.rect(screen,(100,65,25),(CX-75,BOARD_Y+155,150,105),border_radius=18)
    pygame.draw.rect(screen,GOLD,(CX-75,BOARD_Y+155,150,105),3,border_radius=18)
    pygame.draw.rect(screen,GOLD,(CX-8,BOARD_Y+155,16,105),border_radius=4)
    if chest_claimed:
        draw_text("COME BACK TOMORROW",font,WHITE,CX,BOARD_Y+310)
        draw_text("You already collected today's gift",small,YELLOW,CX,BOARD_Y+350)
    else:
        draw_text("A surprise gift is waiting!",font,WHITE,CX,BOARD_Y+305)
        draw_button(chest_claim_btn,"OPEN CHEST", (150,105,35),30)

def achievement_progress(a):
    return {"food":total_food,"games":total_games,"coins":total_coins_earned,
            "level":max_level,"score":best_score}.get(a["type"],0)

def draw_achievements():
    draw_button(back_btn,"BACK",GRAY,25)
    draw_text("ACHIEVEMENTS",big,YELLOW,CX,BOARD_Y+65)
    for i,a in enumerate(achievements):
        rect=item_rects[i]
        pygame.draw.rect(screen,(25,39,58),rect,border_radius=10)
        progress=min(achievement_progress(a),a["goal"])
        draw_text(a["name"],small,WHITE,rect.centerx-18,rect.y+16)
        draw_text(a["desc"],tiny,(190,200,215),rect.centerx-18,rect.y+39)
        draw_text(str(progress)+"/"+str(a["goal"]),tiny,YELLOW,rect.centerx-18,rect.y+59)
        label="CLAIMED" if i in achievement_claimed else ("CLAIM" if progress>=a["goal"] else str(a["reward"])+" COINS")
        draw_button(pygame.Rect(rect.right-108,rect.y+39,100,27),label,DARK_GREEN if progress>=a["goal"] and i not in achievement_claimed else GRAY,17)

def draw_controls():
    pygame.draw.rect(screen,(17,27,43),(0,BOARD_H,W,CONTROL_H))
    draw_button(pause_btn,"PAUSE",GRAY,24)
    draw_button(restart_btn,"RESTART",DARK_GREEN,24)
    draw_button(store_btn,"STORE",BLUE,24)
    draw_button(missions_btn,"MISSIONS",DARK_GREEN,24)
    labels=["MUSIC OFF","MUSIC LOW","MUSIC MID"]
    draw_button(music_btn,labels[music_index],[GRAY,DARK_GREEN,BLUE][music_index],20)
    for name,rect in buttons.items(): draw_arrow(rect,name)

def draw_game():
    bg = backgrounds[selected_background]["color"]
    screen.fill(bg)

    # Main menu and secondary pages use the whole screen. Do not draw
    # the active game board behind them (prevents stray food/obstacles).
    if state in ("menu", "shop", "missions", "chest", "achievements"):
        pygame.draw.rect(screen, (17, 29, 47), (0, 0, W, H))
        # Soft decorative background grid, without game objects.
        step = max(24, SIZE * 2)
        for x in range(0, W, step):
            pygame.draw.line(screen, (23, 38, 58), (x, 0), (x, H), 1)
        for y in range(0, H, step):
            pygame.draw.line(screen, (23, 38, 58), (0, y), (W, y), 1)

        if state == "menu":
            draw_text("SNAKE GAME", big, GREEN, CX, int(H*0.18))
            draw_text("WELCOME!", big, YELLOW, CX, int(H*0.27))
            draw_text("Coins: "+str(coins), font, YELLOW, CX, int(H*0.34))
            # Reposition menu buttons in a centered vertical stack.
            labels = [
                (start_btn, "START", DARK_GREEN),
                (menu_store_btn, "STORE", BLUE),
                (menu_missions_btn, "MISSIONS", GRAY),
                (menu_chest_btn, "DAILY CHEST", (150,105,35)),
                (menu_ach_btn, "ACHIEVEMENTS", (100,75,155))
            ]
            button_w = min(W-70, 250)
            button_h = min(62, max(48, int(H*0.045)))
            gap = max(12, int(H*0.012))
            total_h = len(labels)*button_h + (len(labels)-1)*gap
            y0 = int(H*0.47)
            if y0 + total_h > H-45:
                y0 = max(int(H*0.39), (H-total_h)//2)
            for i, (_, label, color) in enumerate(labels):
                r = pygame.Rect(CX-button_w//2, y0+i*(button_h+gap), button_w, button_h)
                draw_button(r, label, color, 29 if label != "START" else 36)
                # Keep hit areas synchronized with the visible buttons.
                if label == "START": start_btn = r
                elif label == "STORE": menu_store_btn = r
                elif label == "MISSIONS": menu_missions_btn = r
                elif label == "DAILY CHEST": menu_chest_btn = r
                elif label == "ACHIEVEMENTS": menu_ach_btn = r

        else:
            # Overlay pages are centered on the actual display, not the
            # smaller gameplay board. Rebase their controls for this page.
            page_top = max(100, int(H*0.12))
            draw_text("SNAKE GAME", big, GREEN, CX, int(H*0.07))
            if state == "shop":
                draw_text("GAME STORE", big, YELLOW, CX, page_top)
                draw_text("Coins: "+str(coins), font, WHITE, CX, page_top+42)
                back_btn = pygame.Rect(12, page_top-28, 100, 42)
                skin_tab = pygame.Rect(10, page_top+65, W//2-15, 42)
                bg_tab = pygame.Rect(W//2+5, page_top+65, W//2-15, 42)
                draw_button(back_btn, "BACK", GRAY, 25)
                draw_button(skin_tab, "SNAKE SKINS", BLUE if shop_category=="skins" else GRAY, 22)
                draw_button(bg_tab, "BACKGROUNDS", BLUE if shop_category=="backgrounds" else GRAY, 22)
                items = skins if shop_category=="skins" else backgrounds
                owned = owned_skins if shop_category=="skins" else owned_backgrounds
                selected = selected_skin if shop_category=="skins" else selected_background
                for i,item in enumerate(items):
                    y = page_top+125+i*min(82, int(H*0.062))
                    rect = pygame.Rect(15,y,W-30,68)
                    pygame.draw.rect(screen,(25,39,58),rect,border_radius=12)
                    pygame.draw.rect(screen,item["color"],(rect.x+9,rect.y+8,44,52),border_radius=9)
                    draw_text(item["name"],small,WHITE,rect.centerx,rect.y+20)
                    label=("SELECTED" if selected==i else "USE") if i in owned else str(item["price"])+" COINS"
                    draw_button(pygame.Rect(rect.right-115,rect.y+36,106,27),label,DARK_GREEN if i in owned else BLUE,17)
            elif state == "missions":
                draw_text("DAILY MISSIONS",big,YELLOW,CX,page_top)
                draw_text("Coins: "+str(coins),font,WHITE,CX,page_top+40)
                draw_button(back_btn,"BACK",GRAY,25)
                for i,m in enumerate(missions):
                    y=page_top+85+i*92
                    rect=pygame.Rect(15,y,W-30,78)
                    pygame.draw.rect(screen,(25,39,58),rect,border_radius=12)
                    progress=min(daily_food if m["type"]=="food" else daily_games,m["target"])
                    draw_text(m["name"],small,WHITE,CX-15,y+20)
                    draw_text(str(progress)+"/"+str(m["target"]),small,YELLOW,CX-15,y+51)
                    label="CLAIMED" if i in claimed else ("CLAIM" if progress>=m["target"] else str(m["reward"])+" COINS")
                    draw_button(pygame.Rect(rect.right-112,y+38,103,28),label,DARK_GREEN if progress>=m["target"] and i not in claimed else GRAY,17)
            elif state == "chest":
                draw_text("DAILY REWARD",big,YELLOW,CX,page_top+35)
                draw_button(back_btn,"BACK",GRAY,25)
                chest_rect=pygame.Rect(CX-75,page_top+100,150,105)
                pygame.draw.rect(screen,(100,65,25),chest_rect,border_radius=18)
                pygame.draw.rect(screen,GOLD,chest_rect,3,border_radius=18)
                pygame.draw.rect(screen,GOLD,(CX-8,page_top+100,16,105),border_radius=4)
                if chest_claimed:
                    draw_text("COME BACK TOMORROW",font,WHITE,CX,page_top+260)
                else:
                    draw_text("A surprise gift is waiting!",font,WHITE,CX,page_top+245)
                    chest_claim_btn = pygame.Rect(CX-105,page_top+290,210,58)
                    draw_button(chest_claim_btn,"OPEN CHEST",(150,105,35),28)
            elif state == "achievements":
                draw_text("ACHIEVEMENTS",big,YELLOW,CX,page_top)
                draw_button(back_btn,"BACK",GRAY,25)
                for i,a in enumerate(achievements):
                    y=page_top+65+i*min(88,int(H*0.064))
                    rect=pygame.Rect(12,y,W-24,72)
                    pygame.draw.rect(screen,(25,39,58),rect,border_radius=10)
                    progress=min(achievement_progress(a),a["goal"])
                    draw_text(a["name"],small,WHITE,CX-12,y+15)
                    draw_text(a["desc"],tiny,(190,200,215),CX-12,y+36)
                    draw_text(str(progress)+"/"+str(a["goal"]),tiny,YELLOW,CX-12,y+57)
                    label="CLAIMED" if i in achievement_claimed else ("CLAIM" if progress>=a["goal"] else str(a["reward"])+" COINS")
                    draw_button(pygame.Rect(rect.right-108,y+37,100,27),label,DARK_GREEN if progress>=a["goal"] and i not in achievement_claimed else GRAY,16)
        if notice_timer>0:
            draw_text(notice,font,YELLOW,CX,int(H*0.94))
        return

    # Gameplay screens retain the original board and touch controls.
    draw_text("SNAKE GAME",big,GREEN,CX,35)
    draw_text("Score: "+str(score),font,WHITE,W//4,78)
    draw_text("Best: "+str(best_score),font,YELLOW,W*3//4,78)
    draw_text("LEVEL "+str(level),small,CYAN,CX,103)
    draw_board()
    draw_controls()
    if state=="paused":
        draw_text("PAUSED",big,YELLOW,CX,BOARD_H//2)
    elif state=="over":
        draw_text("GAME OVER",big,RED,CX,BOARD_H//2-25)
        draw_text("Tap RESTART",font,WHITE,CX,BOARD_H//2+20)
    if shield_timer>0: status="SHIELD"
    elif magnet_timer>0: status="MAGNET"
    elif turbo_timer>0: status="TURBO"
    else: status=""
    if status: draw_text(status+" "+str(int(max(shield_timer,magnet_timer,turbo_timer)))+"s",small,CYAN,CX,BOARD_Y+BOARD_H_CELLS+18)
    if notice_timer>0:
        draw_text(notice,font,YELLOW,CX,BOARD_H-18)

# ---------- REWARDS ----------
def add_coins(amount):
    global coins,total_coins_earned
    coins+=amount
    total_coins_earned+=amount
    save_data()

def buy_item(index):
    global coins,selected_skin,selected_background
    items=skins if shop_category=="skins" else backgrounds
    owned=owned_skins if shop_category=="skins" else owned_backgrounds
    if index in owned:
        if shop_category=="skins": selected_skin=index
        else: selected_background=index
    elif coins>=items[index]["price"]:
        coins-=items[index]["price"]
        owned.append(index)
        if shop_category=="skins": selected_skin=index
        else: selected_background=index
    save_data()

def claim_mission(index):
    if index in claimed: return
    m=missions[index]
    progress=daily_food if m["type"]=="food" else daily_games
    if progress>=m["target"]:
        add_coins(m["reward"])
        claimed.append(index)
        save_data()

def claim_chest():
    global chest_claimed,notice,notice_timer
    if chest_claimed: return
    reward=random.randint(20,45)
    add_coins(reward)
    chest_claimed=True
    notice="DAILY CHEST: +"+str(reward)+" COINS!"
    notice_timer=2.5
    sound(gold_sound)
    save_data()

def claim_achievement(index):
    if index in achievement_claimed: return
    a=achievements[index]
    if achievement_progress(a)>=a["goal"]:
        add_coins(a["reward"])
        achievement_claimed.append(index)
        save_data()

# ---------- TOUCH ----------
chest_claim_btn=pygame.Rect(CX-105,BOARD_Y+390,210,58)

def page_back_rect():
    return pygame.Rect(12, max(100, int(H*0.12))-28, 100, 42)

def handle_touch(pos):
    global state,return_state,shop_category,music_index
    if state=="menu":
        if start_btn.collidepoint(pos): start_game()
        elif menu_store_btn.collidepoint(pos): return_state="menu";state="shop"
        elif menu_missions_btn.collidepoint(pos): return_state="menu";state="missions"
        elif menu_chest_btn.collidepoint(pos): return_state="menu";state="chest"
        elif menu_ach_btn.collidepoint(pos): return_state="menu";state="achievements"
    elif state=="shop":
        if back_btn.collidepoint(pos): state=return_state;return
        if skin_tab.collidepoint(pos): shop_category="skins";return
        if bg_tab.collidepoint(pos): shop_category="backgrounds";return
        items=skins if shop_category=="skins" else backgrounds
        for i in range(min(len(items),len(item_rects))):
            r=item_rects[i]
            if pygame.Rect(r.right-112,r.y+39,103,28).collidepoint(pos): buy_item(i);return
    elif state=="missions":
        if back_btn.collidepoint(pos): state=return_state;return
        for i,r in enumerate(item_rects[:3]):
            if pygame.Rect(r.right-112,r.y+39,103,28).collidepoint(pos): claim_mission(i);return
    elif state=="chest":
        if back_btn.collidepoint(pos): state=return_state;return
        if chest_claim_btn.collidepoint(pos): claim_chest()
    elif state=="achievements":
        if back_btn.collidepoint(pos): state=return_state;return
        for i,r in enumerate(item_rects[:len(achievements)]):
            if pygame.Rect(r.right-108,r.y+39,100,27).collidepoint(pos): claim_achievement(i);return
    elif state in ("playing","paused","over"):
        if store_btn.collidepoint(pos): return_state=state;state="shop";return
        if missions_btn.collidepoint(pos): return_state=state;state="missions";return
        if music_btn.collidepoint(pos): music_index=(music_index+1)%3;update_music();return
        if pause_btn.collidepoint(pos):
            if state=="playing":
                state="paused"
                if music_channel: music_channel.pause()
            elif state=="paused":
                state="playing"
                if music_channel: music_channel.unpause()
            return
        if restart_btn.collidepoint(pos): start_game();return
        if state=="playing":
            for name,r in buttons.items():
                if r.collidepoint(pos): change_direction(name);return

# ---------- GAME LOGIC ----------
def finish_game():
    global state
    state="over"
    sound(lose_sound)
    if music_channel:
        try: music_channel.pause()
        except: pass

def level_up():
    global level,foods_this_level,obstacles,notice,notice_timer
    global max_level,record_level,food,golden_food
    level+=1
    foods_this_level=0
    max_level=max(max_level,level)
    record_level=max(record_level,level)
    create_obstacles()
    food=create_food()
    golden_food=None
    notice="LEVEL "+str(level)+"!"
    notice_timer=2.0
    save_data()

def collect_food(is_gold=False):
    global score,coins,daily_food,total_food,food,golden_food
    global foods_this_level,power_timer
    if is_gold:
        score+=3
        add_coins(10)
        sound(gold_sound)
        golden_food=None
    else:
        score+=1
        add_coins(1)
        sound(eat_sound)
        daily_food+=1
        total_food+=1
        foods_this_level+=1
        food=create_food()
        if random.random()<0.18 and golden_food is None:
            golden_food=random_empty()
        if random.random()<0.16 and powerup is None:
            spawn_powerup()
        if foods_this_level>=5+(level-1)*2:
            level_up()
    if score>best_score:
        globals()["best_score"]=score
        save_best()
    save_data()

def activate_power():
    global powerup,power_type,shield_timer,magnet_timer,turbo_timer
    if not powerup: return
    if power_type=="shield": shield_timer=12
    elif power_type=="magnet": magnet_timer=10
    elif power_type=="turbo": turbo_timer=8
    powerup=None
    power_type=None
    sound(gold_sound)

def move_snake():
    global direction,turn_locked,food,golden_food,power_timer
    global shield_timer,magnet_timer,turbo_timer,notice,notice_timer
    direction=next_direction
    hx,hy=snake[0]
    head=(hx+direction[0],hy+direction[1])
    hit_wall=head[0]<0 or head[0]>=COLS or head[1]<0 or head[1]>=ROWS
    hit_obstacle=head in obstacles
    hit_body=head in snake[:-1]
    if hit_wall or hit_obstacle or hit_body:
        if shield_timer>0:
            shield_timer=0
            notice="SHIELD SAVED YOU!"
            notice_timer=1.8
            # Bounce back one cell and continue forward on next tick.
            head=snake[0]
            turn_locked=False
            return
        finish_game()
        return
    snake.insert(0,head)
    ate=False
    if head==food:
        collect_food(False)
        ate=True
    elif head==golden_food:
        collect_food(True)
        ate=True
    elif head==powerup:
        activate_power()
    # Magnet gives occasional bonus coins while active.
    if magnet_timer>0 and random.random()<0.12:
        add_coins(1)
    if not ate:
        snake.pop()
    turn_locked=False

# ---------- LOOP ----------
reset_game("menu")
running=True
while running:
    dt=clock.tick(60)/1000
    if notice_timer>0: notice_timer=max(0,notice_timer-dt)
    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE: running=False
            elif event.key==pygame.K_UP: change_direction("UP")
            elif event.key==pygame.K_DOWN: change_direction("DOWN")
            elif event.key==pygame.K_LEFT: change_direction("LEFT")
            elif event.key==pygame.K_RIGHT: change_direction("RIGHT")
            elif event.key==pygame.K_SPACE:
                if state=="menu": start_game()
                elif state=="playing": state="paused"
                elif state=="paused": state="playing"
        elif event.type==pygame.FINGERDOWN:
            handle_touch((int(event.x*W),int(event.y*H)))
        elif event.type==pygame.MOUSEBUTTONDOWN:
            handle_touch(event.pos)

    if state=="playing":
        shield_timer=max(0,shield_timer-dt)
        magnet_timer=max(0,magnet_timer-dt)
        turbo_timer=max(0,turbo_timer-dt)
        move_timer+=dt
        speed=max(0.045,0.12-score*0.0018)
        if turbo_timer>0: speed*=0.65
        while move_timer>=speed and state=="playing":
            move_timer-=speed
            move_snake()
    else:
        move_timer=0

    draw_game()
    pygame.display.flip()

save_data()
pygame.quit()
