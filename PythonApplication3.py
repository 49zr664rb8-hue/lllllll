import pygame
import sys
import random
import math
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("哈基米大冒险 - 摸金撤离")

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
GRAY = (128,128,128)
DARK_GRAY = (50,50,50)
LIGHT_GRAY = (200,200,200)
BROWN = (139,69,19)

clock = pygame.time.Clock()
FPS = 60

def get_font(size):
    font_names = ["simhei","microsoftyahei","pingfangsc","notosanscjk","arialunicode"]
    for name in font_names:
        try:
            font = pygame.font.SysFont(name, size)
            test_surf = font.render("测试", True, WHITE)
            if test_surf.get_width() > 10:
                return font
        except:
            continue
    return pygame.font.Font(None, size)

font_small = get_font(20)
font_medium = get_font(24)
font_large = get_font(48)
font_title = get_font(72)

def load_image(base_name, size, color, extensions=("png","jpg","jpeg","bmp")):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for ext in extensions:
        path = os.path.join(script_dir, f"{base_name}.{ext}")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                return pygame.transform.scale(img, size)
            except Exception as e:
                continue
    surf = pygame.Surface(size)
    surf.fill(color)
    return surf

# 战利品
LOOT_TYPES = [("金条",100),("古董",80),("武器零件",60),("医疗包",40),("情报文件",70)]
EQUIPMENT_LEVELS = {1:{"price":100,"damage_reduction":0.05},2:{"price":250,"damage_reduction":0.10},3:{"price":500,"damage_reduction":0.15},4:{"price":800,"damage_reduction":0.20},5:{"price":1200,"damage_reduction":0.25},6:{"price":1800,"damage_reduction":0.30}}
BULLET_LEVELS = {1:{"price":50,"damage_multiplier":1.0},2:{"price":150,"damage_multiplier":1.2},3:{"price":300,"damage_multiplier":1.4},4:{"price":500,"damage_multiplier":1.6},5:{"price":800,"damage_multiplier":1.8},6:{"price":1200,"damage_multiplier":2.0}}
WEAPONS = [
    {"name":"手枪","damage":10,"price":100,"ammo_type":"pistol","ammo_capacity":12,"image":"weapon_pistol","color":(150,150,150)},
    {"name":"冲锋枪","damage":15,"price":300,"ammo_type":"smg","ammo_capacity":30,"image":"weapon_smg","color":(100,100,200)},
    {"name":"步枪","damage":20,"price":600,"ammo_type":"rifle","ammo_capacity":30,"image":"weapon_rifle","color":(200,100,100)},
    {"name":"狙击枪","damage":30,"price":1000,"ammo_type":"sniper","ammo_capacity":5,"image":"weapon_sniper","color":(50,150,50)},
    {"name":"霰弹枪","damage":25,"price":800,"ammo_type":"shotgun","ammo_capacity":8,"image":"weapon_shotgun","color":(200,200,100)}
]
FIST_WEAPON = {"name":"拳头","damage":5,"ammo_type":None,"ammo_capacity":0,"price":0,"image":None,"color":(255,0,255)}
AMMO_TYPES = {"pistol":{"name":"手枪子弹","buy_amount":12,"price":20},"smg":{"name":"冲锋枪子弹","buy_amount":30,"price":40},"rifle":{"name":"步枪子弹","buy_amount":30,"price":50},"sniper":{"name":"狙击枪子弹","buy_amount":5,"price":60},"shotgun":{"name":"霰弹枪子弹","buy_amount":8,"price":45}}

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4
        self.health = 100
        self.max_health = 100
        self.inventory = []
        self.money = 0
        self.armor_level = 0
        self.bullet_level = 1
        self.weapon = FIST_WEAPON
        self.ammo_inventory = {atype:0 for atype in AMMO_TYPES}
        self.image = load_image("player",(40,40),BLUE)
        self.rect = self.image.get_rect(center=(x,y))
        self.damage_reduction = 0.0
        self.damage_multiplier = 1.0
        self.melee_cooldown = 0
        self.update_combat_stats()

    def update_combat_stats(self):
        if self.armor_level > 0:
            self.damage_reduction = EQUIPMENT_LEVELS[self.armor_level]["damage_reduction"]
        else:
            self.damage_reduction = 0.0
        self.damage_multiplier = BULLET_LEVELS[self.bullet_level]["damage_multiplier"]

    def move(self, dx, dy, obstacles):
        new_x = self.x + dx
        self.rect.centerx = new_x
        if self.collide_with_obstacles(obstacles):
            self.rect.centerx = self.x
        else:
            self.x = new_x
        new_y = self.y + dy
        self.rect.centery = new_y
        if self.collide_with_obstacles(obstacles):
            self.rect.centery = self.y
        else:
            self.y = new_y
        self.x = max(20, min(WIDTH-20, self.x))
        self.y = max(20, min(HEIGHT-20, self.y))
        self.rect.center = (self.x, self.y)

    def collide_with_obstacles(self, obstacles):
        for obs in obstacles:
            if self.rect.colliderect(obs.rect):
                return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y-10,40,5))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y-10,40*(self.health/self.max_health),5))

    def reset_for_new_round(self):
        self.x = WIDTH//2
        self.y = HEIGHT//2
        self.health = self.max_health
        self.inventory = []
        self.melee_cooldown = 0
        self.rect.center = (self.x, self.y)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.health = 50
        self.image = load_image("enemy",(30,30),RED)
        self.rect = self.image.get_rect(center=(x,y))
        self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.change_timer = 0
        self.attack_cooldown = 0

    def update(self, player, obstacles, attack_damage, attack_cooldown_frames):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx,dy)
        if dist < 200:
            if dist > 0:
                dx,dy = dx/dist,dy/dist
                self.try_move(dx*self.speed,dy*self.speed,obstacles)
        else:
            self.change_timer -= 1
            if self.change_timer <= 0:
                self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1),(0,0)])
                self.change_timer = random.randint(30,90)
            self.try_move(self.direction[0]*self.speed*0.5,self.direction[1]*self.speed*0.5,obstacles)
        self.x = max(15,min(WIDTH-15,self.x))
        self.y = max(15,min(HEIGHT-15,self.y))
        self.rect.center = (self.x,self.y)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def try_move(self,dx,dy,obstacles):
        old_x = self.x
        self.x += dx
        self.rect.centerx = self.x
        if self.collide_with_obstacles(obstacles):
            self.x = old_x
            self.rect.centerx = old_x
        old_y = self.y
        self.y += dy
        self.rect.centery = self.y
        if self.collide_with_obstacles(obstacles):
            self.y = old_y
            self.rect.centery = old_y

    def collide_with_obstacles(self,obstacles):
        for obs in obstacles:
            if self.rect.colliderect(obs.rect):
                return True
        return False

    def draw(self,surface):
        surface.blit(self.image,self.rect.topleft)
        pygame.draw.rect(surface,RED,(self.rect.x,self.rect.y-10,30,4))
        pygame.draw.rect(surface,GREEN,(self.rect.x,self.rect.y-10,30*(self.health/50),4))

class Obstacle:
    def __init__(self,x,y,width,height):
        self.rect = pygame.Rect(x,y,width,height)
        self.color = (100,100,100)
    def draw(self,surface):
        pygame.draw.rect(surface,self.color,self.rect)
        pygame.draw.rect(surface,WHITE,self.rect,2)

class LootBox:
    def __init__(self,x,y,special=False):
        self.x = x
        self.y = y
        self.special = special
        if special:
            self.image = load_image("special_box",(25,25),(200,150,50))
        else:
            self.image = load_image("box",(25,25),BROWN)
        self.rect = self.image.get_rect(center=(x,y))
        self.searched = False
    def draw(self,surface):
        if not self.searched:
            surface.blit(self.image,self.rect.topleft)

class Bullet:
    def __init__(self,x,y,angle,damage):
        self.x = x
        self.y = y
        self.speed = 10
        self.angle = angle
        self.radius = 4
        self.damage = damage
        self.rect = pygame.Rect(x-self.radius,y-self.radius,self.radius*2,self.radius*2)
    def update(self,obstacles):
        self.x += self.speed*math.cos(self.angle)
        self.y += self.speed*math.sin(self.angle)
        self.rect.center = (self.x,self.y)
        for obs in obstacles:
            if self.rect.colliderect(obs.rect):
                return False
        if self.x<0 or self.x>WIDTH or self.y<0 or self.y>HEIGHT:
            return False
        return True
    def draw(self,surface):
        pygame.draw.circle(surface,BLACK,(int(self.x),int(self.y)),self.radius)

class Button:
    def __init__(self,x,y,width,height,text,color,hover_color,action=None):
        self.rect = pygame.Rect(x,y,width,height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.hovered = False
    def draw(self,surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface,color,self.rect,border_radius=8)
        pygame.draw.rect(surface,WHITE,self.rect,2,border_radius=8)
        text_surf = font_medium.render(self.text,True,WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf,text_rect)
    def check_hover(self,mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
    def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                self.action()

class WarehouseItem:
    def __init__(self,item_type,name,value,level=None,weapon_data=None):
        self.item_type = item_type
        self.name = name
        self.value = value
        self.level = level
        self.weapon_data = weapon_data

class Game:
    def __init__(self):
        self.game_state = "menu"
        self.difficulty = None
        self.win = False
        self.player = Player(WIDTH//2,HEIGHT//2)
        self.warehouse = []
        self.warehouse_scroll = 0
        self.message = None
        self.message_timer = 0
        # 虚拟摇杆和按钮
        self.joystick_base = (120, HEIGHT-120)
        self.joystick_radius = 60
        self.joystick_pos = self.joystick_base
        self.joystick_active = False
        self.fire_button_rect = pygame.Rect(WIDTH-120, HEIGHT-120, 80, 80)
        self.search_button_rect = pygame.Rect(WIDTH-220, HEIGHT-120, 80, 80)
        self.fire_pressed = False
        self.search_pressed = False
        self.reset_game()

    def reset_game(self):
        self.player.reset_for_new_round()
        self.enemies = [Enemy(random.randint(50,WIDTH-50),random.randint(50,HEIGHT-50)) for _ in range(5)]
        self.boxes = [LootBox(random.randint(50,WIDTH-50),random.randint(50,HEIGHT-50)) for _ in range(10)]
        self.bullets = []
        self.obstacles = self.generate_obstacles()
        self.extract_point = (WIDTH-50,HEIGHT-50)
        self.extract_radius = 30
        self.extract_timer = 0
        self.extracting = False
        self.game_over = False
        self.win = False

    def generate_obstacles(self):
        obstacles = []
        birth_x,birth_y = WIDTH//2,HEIGHT//2
        safe_radius = 100
        for _ in range(random.randint(5,8)):
            attempts = 0
            while attempts < 50:
                w = random.randint(40,100)
                h = random.randint(20,60)
                x = random.randint(100,WIDTH-w-100)
                y = random.randint(100,HEIGHT-h-100)
                center_x = x+w/2
                center_y = y+h/2
                dist = math.hypot(center_x-birth_x,center_y-birth_y)
                if dist > safe_radius:
                    obstacles.append(Obstacle(x,y,w,h))
                    break
                attempts += 1
        return obstacles

    def show_message(self,text):
        self.message = text
        self.message_timer = 2*FPS

    def start_game(self,difficulty):
        if difficulty == "basic":
            if self.player.armor_level > 3:
                self.show_message("装备等级超过3级，无法进入基础模式！")
                return False
        elif difficulty == "advanced":
            if self.player.armor_level < 4:
                self.show_message("装备等级低于4级，无法进入进阶模式！")
                return False
        elif difficulty == "expert":
            if self.player.armor_level < 5:
                self.show_message("装备等级低于5级，无法进入高手模式！")
                return False
        self.difficulty = difficulty
        self.game_state = "playing"
        self.reset_game()
        return True

    def open_shop(self): self.game_state = "shop"
    def open_warehouse(self): self.game_state = "warehouse"; self.warehouse_scroll = 0
    def open_difficulty_select(self): self.game_state = "difficulty_select"
    def open_town(self): self.game_state = "town"; self.player.reset_for_new_round(); self.show_message("进入哈基镇，自由活动吧！")
    def return_to_menu(self): self.game_state = "menu"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # 处理摇杆和按钮（playing 和 town 状态）
            if self.game_state in ("playing", "town"):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pos = event.pos
                        # 摇杆按下
                        if math.hypot(pos[0]-self.joystick_base[0], pos[1]-self.joystick_base[1]) <= self.joystick_radius:
                            self.joystick_active = True
                            self.joystick_pos = pos
                        # 开火按钮（只在 playing 状态）
                        if self.game_state == "playing" and self.fire_button_rect.collidepoint(pos):
                            self.fire_pressed = True
                        # 搜索按钮（只在 playing 状态）
                        if self.game_state == "playing" and self.search_button_rect.collidepoint(pos):
                            self.search_pressed = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.joystick_active = False
                        self.joystick_pos = self.joystick_base
                        self.fire_pressed = False
                        self.search_pressed = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.joystick_active:
                        self.joystick_pos = event.pos

                # 键盘备用
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.return_to_menu()
                    if self.game_state == "playing" and event.key == pygame.K_f:
                        self.search_box()

            # 其他界面事件
            if self.game_state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.rect.collidepoint(event.pos): self.open_difficulty_select()
                    elif shop_button.rect.collidepoint(event.pos): self.open_shop()
                    elif warehouse_button.rect.collidepoint(event.pos): self.open_warehouse()
                    elif town_button.rect.collidepoint(event.pos): self.open_town()
                    elif quit_button.rect.collidepoint(event.pos): pygame.quit(); sys.exit()

            elif self.game_state == "difficulty_select":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if basic_button.rect.collidepoint(event.pos): self.start_game("basic")
                    elif advanced_button.rect.collidepoint(event.pos): self.start_game("advanced")
                    elif expert_button.rect.collidepoint(event.pos): self.start_game("expert")
                    elif back_to_menu_button.rect.collidepoint(event.pos): self.return_to_menu()

            elif self.game_state == "shop":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_shop_click(event.pos)
                    if back_button.rect.collidepoint(event.pos): self.return_to_menu()

            elif self.game_state == "warehouse":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.handle_warehouse_click(event.pos): continue
                    if back_button.rect.collidepoint(event.pos): self.return_to_menu()
                if event.type == pygame.MOUSEWHEEL:
                    self.warehouse_scroll = max(0, self.warehouse_scroll - event.y*3)

            elif self.game_state == "town":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if town_back_button.rect.collidepoint(event.pos): self.return_to_menu()

            elif self.game_state == "game_over":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.return_to_menu()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if game_over_back_button.rect.collidepoint(event.pos):
                        self.return_to_menu()

    def melee_attack(self):
        attack_range = 40
        for enemy in self.enemies[:]:
            dist = math.hypot(self.player.x-enemy.x, self.player.y-enemy.y)
            if dist < attack_range:
                enemy.health -= self.player.weapon["damage"]
                if enemy.health <= 0:
                    self.boxes.append(LootBox(enemy.x,enemy.y,special=True))
                    self.enemies.remove(enemy)
                break

    def search_box(self):
        for box in self.boxes:
            if not box.searched:
                dist = math.hypot(self.player.x-box.x, self.player.y-box.y)
                if dist < 40:
                    if len(self.player.inventory) < 6:
                        if box.special:
                            if self.difficulty == "basic":
                                roll = random.random()
                                if roll < 0.2:
                                    weapon = random.choice(WEAPONS[:2]); self.warehouse.append(WarehouseItem("weapon",weapon["name"],weapon["price"],weapon_data=weapon)); self.show_message(f"获得武器: {weapon['name']}")
                                elif roll < 0.5:
                                    level = random.randint(1,2); self.warehouse.append(WarehouseItem("equipment",f"护甲等级{level}",EQUIPMENT_LEVELS[level]["price"],level=level)); self.show_message(f"获得护甲等级{level}")
                                else:
                                    level = random.randint(1,2); self.warehouse.append(WarehouseItem("bullet",f"子弹等级{level}",BULLET_LEVELS[level]["price"],level=level)); self.show_message(f"获得子弹等级{level}")
                            elif self.difficulty == "advanced":
                                roll = random.random()
                                if roll < 0.4:
                                    weapon = random.choice(WEAPONS[:4]); self.warehouse.append(WarehouseItem("weapon",weapon["name"],weapon["price"],weapon_data=weapon)); self.show_message(f"获得武器: {weapon['name']}")
                                elif roll < 0.7:
                                    level = random.randint(1,4); self.warehouse.append(WarehouseItem("equipment",f"护甲等级{level}",EQUIPMENT_LEVELS[level]["price"],level=level)); self.show_message(f"获得护甲等级{level}")
                                else:
                                    level = random.randint(1,4); self.warehouse.append(WarehouseItem("bullet",f"子弹等级{level}",BULLET_LEVELS[level]["price"],level=level)); self.show_message(f"获得子弹等级{level}")
                            else:
                                roll = random.random()
                                if roll < 0.5:
                                    weapon = random.choice(WEAPONS); self.warehouse.append(WarehouseItem("weapon",weapon["name"],weapon["price"],weapon_data=weapon)); self.show_message(f"获得武器: {weapon['name']}")
                                elif roll < 0.8:
                                    level = random.randint(1,6); self.warehouse.append(WarehouseItem("equipment",f"护甲等级{level}",EQUIPMENT_LEVELS[level]["price"],level=level)); self.show_message(f"获得护甲等级{level}")
                                else:
                                    level = random.randint(1,6); self.warehouse.append(WarehouseItem("bullet",f"子弹等级{level}",BULLET_LEVELS[level]["price"],level=level)); self.show_message(f"获得子弹等级{level}")
                        else:
                            item_name,item_value = random.choice(LOOT_TYPES); self.player.inventory.append(item_name); self.show_message(f"搜索到: {item_name}")
                        box.searched = True
                    else:
                        self.show_message("背包已满")
                    break

    def handle_shop_click(self,mouse_pos):
        # 弹药购买
        ammo_y = 150
        ammo_keys = list(AMMO_TYPES.keys())
        for i, atype in enumerate(ammo_keys):
            x = 50 + i * 150
            rect = pygame.Rect(x, ammo_y, 140, 50)
            if rect.collidepoint(mouse_pos):
                info = AMMO_TYPES[atype]
                if self.player.money >= info["price"]:
                    self.player.money -= info["price"]
                    self.player.ammo_inventory[atype] += info["buy_amount"]
                    self.show_message(f"购买 {info['name']} x{info['buy_amount']}")
                else:
                    self.show_message("鼠鼠币不足")
                return
        # 装备等级
        for level in range(1,7):
            x = 50 + (level-1)*110
            rect = pygame.Rect(x, 250, 100, 50)
            if rect.collidepoint(mouse_pos):
                price = EQUIPMENT_LEVELS[level]["price"]
                if self.player.money >= price:
                    self.player.money -= price
                    self.warehouse.append(WarehouseItem("equipment", f"护甲等级{level}", price, level=level))
                    self.show_message(f"购买护甲等级{level}，已存入仓库")
                else:
                    self.show_message("鼠鼠币不足")
                return
        # 子弹等级
        for level in range(1,7):
            x = 50 + (level-1)*110
            rect = pygame.Rect(x, 350, 100, 50)
            if rect.collidepoint(mouse_pos):
                price = BULLET_LEVELS[level]["price"]
                if self.player.money >= price:
                    self.player.money -= price
                    self.warehouse.append(WarehouseItem("bullet", f"子弹等级{level}", price, level=level))
                    self.show_message(f"购买子弹等级{level}，已存入仓库")
                else:
                    self.show_message("鼠鼠币不足")
                return
        # 枪械
        for i, weapon in enumerate(WEAPONS):
            x = 50 + (i % 5) * 150
            y = 450 + (i // 5) * 60
            rect = pygame.Rect(x, y, 140, 50)
            if rect.collidepoint(mouse_pos):
                if self.player.money >= weapon["price"]:
                    self.player.money -= weapon["price"]
                    self.warehouse.append(WarehouseItem("weapon", weapon["name"], weapon["price"], weapon_data=weapon))
                    self.show_message(f"购买 {weapon['name']}，已存入仓库")
                else:
                    self.show_message("鼠鼠币不足")
                return

    def handle_warehouse_click(self, mouse_pos):
        start_index = self.warehouse_scroll
        visible_count = min(len(self.warehouse) - start_index, (HEIGHT - 200) // 40)
        for i in range(visible_count):
            item_index = start_index + i
            item = self.warehouse[item_index]
            y = 100 + i * 40
            if item.item_type in ("equipment", "bullet", "weapon"):
                use_rect = pygame.Rect(250, y, 80, 30)
                if use_rect.collidepoint(mouse_pos):
                    self.use_warehouse_item(item_index)
                    return True
            sell_rect = pygame.Rect(340, y, 80, 30)
            if sell_rect.collidepoint(mouse_pos):
                self.sell_warehouse_item(item_index)
                return True
        return False

    def use_warehouse_item(self, index):
        item = self.warehouse[index]
        if item.item_type == "equipment":
            if item.level > self.player.armor_level:
                self.player.armor_level = item.level
                self.player.update_combat_stats()
                self.show_message(f"已装备护甲等级{item.level}")
            else:
                self.show_message("当前护甲等级更高或相同")
            self.warehouse.pop(index)
        elif item.item_type == "bullet":
            if item.level > self.player.bullet_level:
                self.player.bullet_level = item.level
                self.player.update_combat_stats()
                self.show_message(f"已装备子弹等级{item.level}")
            else:
                self.show_message("当前子弹等级更高或相同")
            self.warehouse.pop(index)
        elif item.item_type == "weapon":
            if self.player.weapon["name"] != "拳头":
                old_weapon = self.player.weapon
                self.warehouse.append(WarehouseItem("weapon", old_weapon["name"], old_weapon["price"], weapon_data=old_weapon))
                self.show_message(f"{old_weapon['name']} 已放回仓库")
            self.player.weapon = item.weapon_data
            self.show_message(f"装备 {item.name}")
            self.warehouse.pop(index)

    def sell_warehouse_item(self, index):
        item = self.warehouse.pop(index)
        self.player.money += item.value
        self.show_message(f"出售 {item.name}，获得 {item.value} 鼠鼠币")

    def update(self):
        if self.game_state == "town":
            dx, dy = self.get_joystick_movement()
            self.player.move(dx, dy, [])
            if self.message_timer > 0: self.message_timer -= 1
            return

        if self.game_state != "playing":
            if self.message_timer > 0: self.message_timer -= 1
            return

        if self.player.melee_cooldown > 0: self.player.melee_cooldown -= 1

        # 摇杆移动
        dx, dy = self.get_joystick_movement()
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, self.obstacles)

        # 开火按钮
        if self.fire_pressed:
            if self.player.weapon["ammo_type"] is None:
                if self.player.melee_cooldown <= 0:
                    self.melee_attack()
                    self.player.melee_cooldown = 15
            else:
                ammo_type = self.player.weapon["ammo_type"]
                if self.player.ammo_inventory[ammo_type] > 0:
                    self.player.ammo_inventory[ammo_type] -= 1
                    # 默认向右射击，手机版可后续调整方向
                    angle = 0
                    damage = self.player.weapon["damage"] * self.player.damage_multiplier
                    self.bullets.append(Bullet(self.player.x, self.player.y, angle, damage))
                else:
                    self.show_message("没有弹药！")

        # 搜索按钮
        if self.search_pressed:
            self.search_box()
            self.search_pressed = False

        # 敌人更新
        if self.difficulty == "basic":
            attack_damage=1; attack_cooldown_frames=5*FPS
        elif self.difficulty == "advanced":
            attack_damage=5; attack_cooldown_frames=2*FPS
        else:
            attack_damage=10; attack_cooldown_frames=1*FPS

        for enemy in self.enemies:
            enemy.update(self.player, self.obstacles, attack_damage, attack_cooldown_frames)

        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect) and enemy.attack_cooldown <= 0:
                actual_damage = attack_damage * (1 - self.player.damage_reduction)
                self.player.health -= actual_damage
                enemy.attack_cooldown = attack_cooldown_frames
                if self.player.health <= 0:
                    self.game_over=True; self.win=False; self.game_state="game_over"; break

        for bullet in self.bullets[:]:
            if not bullet.update(self.obstacles):
                self.bullets.remove(bullet); continue
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.health -= bullet.damage
                    if enemy.health <= 0:
                        self.boxes.append(LootBox(enemy.x,enemy.y,special=True)); self.enemies.remove(enemy)
                    if bullet in self.bullets: self.bullets.remove(bullet)
                    break

        dist = math.hypot(self.player.x-self.extract_point[0], self.player.y-self.extract_point[1])
        if dist < self.extract_radius:
            if not self.extracting:
                self.extracting=True; self.extract_timer=5*FPS
            else:
                self.extract_timer -= 1
                if self.extract_timer <= 0: self.complete_extraction()
        else:
            self.extracting=False; self.extract_timer=0

        if self.message_timer > 0: self.message_timer -= 1

    def get_joystick_movement(self):
        if not self.joystick_active:
            return 0,0
        dx = self.joystick_pos[0] - self.joystick_base[0]
        dy = self.joystick_pos[1] - self.joystick_base[1]
        dist = math.hypot(dx,dy)
        if dist == 0:
            return 0,0
        max_speed = self.player.speed
        if dist > self.joystick_radius:
            dx = dx / dist * max_speed
            dy = dy / dist * max_speed
        else:
            dx = dx / self.joystick_radius * max_speed
            dy = dy / self.joystick_radius * max_speed
        return dx, dy

    def complete_extraction(self):
        loot_values = dict(LOOT_TYPES)
        for item_name in self.player.inventory:
            value = loot_values.get(item_name,0)
            self.warehouse.append(WarehouseItem("loot",item_name,value))
        self.player.inventory.clear()
        self.game_over=True; self.win=True; self.game_state="game_over"

    def draw(self):
        screen.fill(DARK_GRAY)
        if self.game_state == "menu": self.draw_menu()
        elif self.game_state == "difficulty_select": self.draw_difficulty_select()
        elif self.game_state == "shop": self.draw_shop()
        elif self.game_state == "warehouse": self.draw_warehouse()
        elif self.game_state == "town": self.draw_town()
        elif self.game_state == "playing": self.draw_game()
        elif self.game_state == "game_over": self.draw_game(); self.draw_game_over()

        if self.message and self.message_timer>0:
            msg_surf = font_medium.render(self.message,True,YELLOW)
            msg_rect = msg_surf.get_rect(center=(WIDTH//2,30))
            bg_rect = msg_rect.inflate(20,10)
            bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surf.fill((0,0,0,150))
            screen.blit(bg_surf,bg_rect.topleft)
            screen.blit(msg_surf,msg_rect)
        pygame.display.flip()

    def draw_menu(self):
        title_text = font_title.render("哈基米大冒险",True,YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH//2,100))
        screen.blit(title_text,title_rect)
        sub_text = font_medium.render("摸金撤离",True,WHITE)
        sub_rect = sub_text.get_rect(center=(WIDTH//2,160))
        screen.blit(sub_text,sub_rect)
        mouse_pos = pygame.mouse.get_pos()
        start_button.check_hover(mouse_pos); shop_button.check_hover(mouse_pos); warehouse_button.check_hover(mouse_pos); town_button.check_hover(mouse_pos); quit_button.check_hover(mouse_pos)
        start_button.draw(screen); shop_button.draw(screen); warehouse_button.draw(screen); town_button.draw(screen); quit_button.draw(screen)
        money_text = font_medium.render(f"鼠鼠币: {self.player.money}",True,YELLOW)
        screen.blit(money_text,(10,10))
        if self.player.weapon["ammo_type"]:
            ammo_count = self.player.ammo_inventory[self.player.weapon["ammo_type"]]
            attr_text = font_small.render(f"护甲:{self.player.armor_level} 子弹等级:{self.player.bullet_level} 武器:{self.player.weapon['name']} 弹药:{ammo_count}",True,WHITE)
        else:
            attr_text = font_small.render(f"护甲:{self.player.armor_level} 子弹等级:{self.player.bullet_level} 武器:{self.player.weapon['name']}",True,WHITE)
        screen.blit(attr_text,(10,40))

    def draw_difficulty_select(self):
        title = font_large.render("选择难度", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        mouse_pos = pygame.mouse.get_pos()
        basic_button.check_hover(mouse_pos); advanced_button.check_hover(mouse_pos); expert_button.check_hover(mouse_pos); back_to_menu_button.check_hover(mouse_pos)
        basic_button.draw(screen); advanced_button.draw(screen); expert_button.draw(screen); back_to_menu_button.draw(screen)
        info1 = font_small.render("基础模式：敌人伤害1，攻击间隔5秒，装备上限3级", True, WHITE)
        info2 = font_small.render("进阶模式：敌人伤害5，攻击间隔2秒，需要护甲4级", True, WHITE)
        info3 = font_small.render("高手模式：敌人伤害10，攻击间隔1秒，需要护甲5级", True, WHITE)
        screen.blit(info1, (100, 300)); screen.blit(info2, (100, 340)); screen.blit(info3, (100, 380))
        armor_text = font_small.render(f"当前护甲等级: {self.player.armor_level}", True, YELLOW)
        screen.blit(armor_text, (100, 420))

    def draw_shop(self):
        title = font_large.render("商店", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        money_text = font_medium.render(f"鼠鼠币: {self.player.money}", True, YELLOW)
        screen.blit(money_text, (WIDTH//2 - money_text.get_width()//2, 100))
        mouse_pos = pygame.mouse.get_pos()
        ammo_title = font_medium.render("购买弹药", True, WHITE)
        screen.blit(ammo_title, (50, 120))
        ammo_keys = list(AMMO_TYPES.keys())
        for i, atype in enumerate(ammo_keys):
            x = 50 + i * 150
            rect = pygame.Rect(x, 150, 140, 50)
            pygame.draw.rect(screen, GRAY if not rect.collidepoint(mouse_pos) else LIGHT_GRAY, rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
            info = AMMO_TYPES[atype]
            text = font_small.render(f"{info['name']} x{info['buy_amount']}", True, BLACK)
            screen.blit(text, (rect.x+10, rect.y+5))
            price_text = font_small.render(f"{info['price']}鼠鼠币", True, YELLOW)
            screen.blit(price_text, (rect.x+10, rect.y+30))
        equip_title = font_medium.render("装备等级 (减伤)", True, WHITE)
        screen.blit(equip_title, (50, 220))
        for level in range(1,7):
            x = 50 + (level-1)*110
            rect = pygame.Rect(x, 250, 100, 50)
            pygame.draw.rect(screen, GRAY if not rect.collidepoint(mouse_pos) else LIGHT_GRAY, rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
            price = EQUIPMENT_LEVELS[level]["price"]
            red = EQUIPMENT_LEVELS[level]["damage_reduction"] * 100
            lv_text = font_small.render(f"Lv{level}", True, BLACK)
            pct_text = font_small.render(f"{red:.0f}%", True, BLACK)
            screen.blit(lv_text, (rect.x+10, rect.y+5))
            screen.blit(pct_text, (rect.x+10, rect.y+25))
            price_text = font_small.render(f"{price}", True, YELLOW)
            screen.blit(price_text, (rect.x+10, rect.y+35))
        bullet_title = font_medium.render("子弹等级 (伤害倍率)", True, WHITE)
        screen.blit(bullet_title, (50, 320))
        for level in range(1,7):
            x = 50 + (level-1)*110
            rect = pygame.Rect(x, 350, 100, 50)
            pygame.draw.rect(screen, GRAY if not rect.collidepoint(mouse_pos) else LIGHT_GRAY, rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
            price = BULLET_LEVELS[level]["price"]
            mult = BULLET_LEVELS[level]["damage_multiplier"]
            lv_text = font_small.render(f"Lv{level}", True, BLACK)
            mult_text = font_small.render(f"{mult:.1f}x", True, BLACK)
            screen.blit(lv_text, (rect.x+10, rect.y+5))
            screen.blit(mult_text, (rect.x+10, rect.y+25))
            price_text = font_small.render(f"{price}", True, YELLOW)
            screen.blit(price_text, (rect.x+10, rect.y+35))
        weapon_title = font_medium.render("枪械", True, WHITE)
        screen.blit(weapon_title, (50, 420))
        for i, weapon in enumerate(WEAPONS):
            x = 50 + (i % 5) * 150
            y = 450 + (i // 5) * 60
            rect = pygame.Rect(x, y, 140, 50)
            pygame.draw.rect(screen, GRAY if not rect.collidepoint(mouse_pos) else LIGHT_GRAY, rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
            name_text = font_small.render(weapon["name"], True, BLACK)
            dmg_text = font_small.render(f"伤害{weapon['damage']}", True, BLACK)
            screen.blit(name_text, (rect.x+5, rect.y+5))
            screen.blit(dmg_text, (rect.x+5, rect.y+25))
            price_text = font_small.render(f"{weapon['price']}", True, YELLOW)
            screen.blit(price_text, (rect.x+5, rect.y+35))
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)

    def draw_warehouse(self):
        title = font_large.render("仓库", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        money_text = font_medium.render(f"鼠鼠币: {self.player.money}", True, YELLOW)
        screen.blit(money_text, (10, 10))
        if not self.warehouse:
            empty_text = font_medium.render("仓库为空", True, GRAY)
            screen.blit(empty_text, (WIDTH//2 - empty_text.get_width()//2, 200))
        else:
            mouse_pos = pygame.mouse.get_pos()
            start_index = self.warehouse_scroll
            visible_count = min(len(self.warehouse) - start_index, (HEIGHT - 200) // 40)
            for i in range(visible_count):
                item_index = start_index + i
                item = self.warehouse[item_index]
                y = 100 + i * 40
                name_text = font_small.render(f"{item.name}", True, WHITE)
                screen.blit(name_text, (50, y))
                if item.item_type in ("equipment", "bullet", "weapon"):
                    use_rect = pygame.Rect(250, y, 80, 30)
                    if use_rect.collidepoint(mouse_pos):
                        pygame.draw.rect(screen, LIGHT_GRAY, use_rect, border_radius=5)
                    else:
                        pygame.draw.rect(screen, BLUE, use_rect, border_radius=5)
                    pygame.draw.rect(screen, WHITE, use_rect, 2, border_radius=5)
                    use_text = font_small.render("使用", True, WHITE)
                    screen.blit(use_text, (use_rect.x+20, use_rect.y+5))
                sell_rect = pygame.Rect(340, y, 80, 30)
                if sell_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, LIGHT_GRAY, sell_rect, border_radius=5)
                else:
                    pygame.draw.rect(screen, RED, sell_rect, border_radius=5)
                pygame.draw.rect(screen, WHITE, sell_rect, 2, border_radius=5)
                sell_text = font_small.render("出售", True, WHITE)
                screen.blit(sell_text, (sell_rect.x+20, sell_rect.y+5))
                value_text = font_small.render(f"{item.value}鼠鼠币", True, YELLOW)
                screen.blit(value_text, (430, y))
            total_items = len(self.warehouse)
            if total_items > visible_count:
                scroll_bar_x = 500
                scroll_bar_y = 100
                scroll_bar_height = HEIGHT - 200
                thumb_h = max(20, int(scroll_bar_height * visible_count / total_items))
                thumb_y = scroll_bar_y + int((scroll_bar_height - thumb_h) * (self.warehouse_scroll / max(1, total_items - visible_count)))
                pygame.draw.rect(screen, GRAY, (scroll_bar_x, scroll_bar_y, 10, scroll_bar_height))
                pygame.draw.rect(screen, LIGHT_GRAY, (scroll_bar_x, thumb_y, 10, thumb_h))
        back_button.check_hover(pygame.mouse.get_pos())
        back_button.draw(screen)

    def draw_town(self):
        screen.fill(WHITE)
        self.player.draw(screen)
        mouse_pos = pygame.mouse.get_pos()
        town_back_button.check_hover(mouse_pos)
        town_back_button.draw(screen)
        # 显示摇杆
        pygame.draw.circle(screen, LIGHT_GRAY, self.joystick_base, self.joystick_radius, 2)
        pygame.draw.circle(screen, GRAY, self.joystick_pos, 30)

    def draw_game(self):
        pygame.draw.circle(screen, GREEN, self.extract_point, self.extract_radius)
        extract_text = font_small.render("撤离点", True, WHITE)
        screen.blit(extract_text, (self.extract_point[0]-20, self.extract_point[1]-40))
        if self.extracting:
            timer_text = font_medium.render(f"撤离中: {self.extract_timer // FPS + 1}秒", True, GREEN)
            screen.blit(timer_text, (self.extract_point[0]-40, self.extract_point[1]-70))
        for obs in self.obstacles: obs.draw(screen)
        for box in self.boxes: box.draw(screen)
        for enemy in self.enemies: enemy.draw(screen)
        self.player.draw(screen)
        for bullet in self.bullets: bullet.draw(screen)
        ammo_type = self.player.weapon["ammo_type"]
        if ammo_type:
            ammo_count = self.player.ammo_inventory[ammo_type]
            ammo_text = font_small.render(f"弹药: {ammo_count} ({AMMO_TYPES[ammo_type]['name']})", True, WHITE)
        else:
            ammo_text = font_small.render("武器: 拳头", True, WHITE)
        health_text = font_small.render(f"生命: {self.player.health}/{self.player.max_health}", True, WHITE)
        money_text = font_small.render(f"鼠鼠币: {self.player.money}", True, YELLOW)
        inv_text = font_small.render(f"背包: {len(self.player.inventory)}/6", True, WHITE)
        screen.blit(ammo_text, (10,10)); screen.blit(health_text, (10,40)); screen.blit(money_text, (10,70)); screen.blit(inv_text, (10,100))
        # 绘制摇杆和按钮
        pygame.draw.circle(screen, LIGHT_GRAY, self.joystick_base, self.joystick_radius, 2)
        pygame.draw.circle(screen, GRAY, self.joystick_pos, 30)
        pygame.draw.rect(screen, RED if self.fire_pressed else (200,50,50), self.fire_button_rect, border_radius=10)
        fire_text = font_medium.render("开火", True, WHITE)
        screen.blit(fire_text, (self.fire_button_rect.x+20, self.fire_button_rect.y+25))
        pygame.draw.rect(screen, GREEN if self.search_pressed else (50,150,50), self.search_button_rect, border_radius=10)
        search_text = font_medium.render("搜索", True, WHITE)
        screen.blit(search_text, (self.search_button_rect.x+15, self.search_button_rect.y+25))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        screen.blit(overlay, (0,0))
        if self.win:
            msg = "撤离成功！战利品已存入仓库！"
            color = GREEN
        else:
            msg = "你死了... 游戏结束"
            color = RED
        text = font_large.render(msg, True, color)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2-40))
        screen.blit(text, text_rect)

        # 绘制返回按钮
        mouse_pos = pygame.mouse.get_pos()
        game_over_back_button.check_hover(mouse_pos)
        game_over_back_button.draw(screen)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

# 按钮定义
start_button = Button(WIDTH//2-100, 220, 200, 50, "开始游戏", BLUE, (70,130,200))
shop_button = Button(WIDTH//2-100, 290, 200, 50, "商店", GREEN, (70,200,130))
warehouse_button = Button(WIDTH//2-100, 360, 200, 50, "仓库", (150,100,200), (180,130,230))
town_button = Button(WIDTH//2-100, 430, 200, 50, "进入哈基镇", (255,165,0), (255,200,100))
quit_button = Button(WIDTH//2-100, 500, 200, 50, "退出游戏", RED, (200,70,70))
back_button = Button(WIDTH//2-100, HEIGHT-80, 200, 50, "返回主菜单", BLUE, (70,130,200))

basic_button = Button(WIDTH//2-100, 150, 200, 50, "基础模式", GREEN, (70,200,130))
advanced_button = Button(WIDTH//2-100, 220, 200, 50, "进阶模式", (255,165,0), (255,200,100))
expert_button = Button(WIDTH//2-100, 290, 200, 50, "高手模式", RED, (255,100,100))
back_to_menu_button = Button(WIDTH//2-100, 450, 200, 50, "返回主菜单", BLUE, (70,130,200))

town_back_button = Button(WIDTH-120, 10, 100, 40, "回到摸金", BLUE, (70,130,200))
game_over_back_button = Button(WIDTH//2-100, HEIGHT//2+60, 200, 50, "返回主菜单", BLUE, (70,130,200))

if __name__ == "__main__":
    game = Game()
    game.run()