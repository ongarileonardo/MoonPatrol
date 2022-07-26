from actor import Actor
from actor import Arena
import random

FLOOR = 310
FLOOR_SPEED = 3
GOAL = 400 #punti da raggiungere per il livello successivo

class MoonPatrolGame:
    def __init__(self,file:str):
        with open(file,"r") as f1:
            csv = f1.read()
            row = csv.split("\n")
            for r in row:
                element = r.split('=')
                if element[0] == 'ARENA':
                    size = element[1].split(',')
                    self._arena = Arena((int(size[0]),int(size[1])))
                elif element[0] == 'ROVER':
                    size = element[1].split(',')
                    self._hero = Bounce(self._arena,(int(size[0]),int(size[1])))
                                         #0.4 velocità primo strato(Montagne)  2.5 velocità secondo strato(colline)
        self._background = [Background(0, 0.4, 0,self._arena), Background(200, 2.5, 1,self._arena), Background(FLOOR,FLOOR_SPEED,2,self._arena)]
        self._delay_spawn = 0
        self._photogram = 0
        self._level = 1
        self._record = 0
        with open("best.txt","r") as f1:
            txt = f1.read()
            best_score = txt.split("=")
            self._record =  int(best_score[1])
        self._level_finished = False
        self._game_start = False
        self._game_over = False
        self._points = 0

    def change_hero(self):
        self._hero.change_symbol()

    def change_bg(self):
        for b in self._background:
            b.change_bg()


    def get_record(self) -> int:
        return self._record
    
    def new_best(self) -> bool:
        if self._record < self._points:
            return True
        else:
            return False

    def subscribe_best(self,name:str):
        with open("best.txt","w") as f1:
            f1.write(name + "=" + str(self._points))
        self._record = self._points
    
    def is_level_finished(self)->bool:
        return self._level_finished

    def next_level(self):
        self._level += 1
        self.restart()
    
    def restart(self):
        for a in self._arena.actors():
            if not isinstance(a,Bounce):
                self._arena.remove(a)
        if not self._level_finished:
            self._level = 1
        self._level_finished = False
        self._points = 0
        self._hero.restart()
    
    def add_actor(self):
        rand = random.randrange(201)
        wait = 200      #soglia minima entro il quale deve essere generata o una roccia o una buca
        if rand % 50 == 0 and self._delay_spawn > wait//self._level:
            Hole(FLOOR,512, FLOOR_SPEED,self._arena)
            Bonus(self._arena, self._hero)
            self._delay_spawn = 0
        if rand % (90//self._level) == 0 and self._delay_spawn > wait//self._level:
            # +3 per evitare di veder fluttuare le rocce a causa delle disconnessioni del terreno
            Rock(FLOOR + 3,self._arena) 
            self._delay_spawn = 0
        if rand % (100 // self._level) == 0:
            Alien(self._arena)

    def is_game_over(self):
        return self._game_over
    
    def move_all(self):
        self.game_over = self._hero.is_game_over()
        for b in self._background:
            b.move()
        self._arena.move_all()
        self._photogram += 1
        self._delay_spawn += 1
        self._points += 1
        if self._points >= GOAL:
            self._level_finished = True
            

    def get_score(self) -> int:
        return self._points

    def get_background(self):
        return self._background
    
    def started(self) -> bool:
        return self._game_start
    
    def arena(self) -> Arena:
        return self._arena

    def hero(self) -> Actor:
        return self._hero

    def start(self) -> bool:
        self._game_start = True



#CLASSE ALIENI
class Alien(Actor):
    def __init__(self,arena:Arena):
        self._w = 25
        self._h = 15
        self._x = 80
        self._y = -self._h
        self._movement=[-5,0,5]
        self._dx = random.choice(self._movement)
        self._dy = random.choice(self._movement)
        self._buffer = 0
        arena.add(self)
        self._i = 0
        self._explode = False
        self._explosion = [(124,270,12,12),(141,269,13,14),(156,268,16,16)]
        self._arena = arena

    def move(self):
        if not self._explode:
            self._x += self._dx
            self._y += self._dy
            if self._y < 0:
                self._y = 0
            elif self._y > 150:
                self._dy = -self._dy
            if self._x < 30:
                self._dx = -self._dx
            elif self._x > 300:
                self._dx = -self._dx
            if self._buffer >= 15:
                self._dx = random.choice(self._movement)
                self._dy = random.choice(self._movement)
                self._buffer = 0
            self._buffer += 1
            if random.randrange(0,100) == 50:
                self._arena.add(Bullet(self._arena,(self._x+self._w/2,self._y+self._h +5),0,4))

        if self._explode and self._i >= len(self._explosion):
            self._arena.remove(self)

    def collide(self,other:Actor):
        explosion_range = 40
        if isinstance(other,Bullet):
            b_dx,b_dy = other.direction()
            if b_dy <= 0:
                self._explode = True
                self._w = explosion_range
                self._h = explosion_range
        elif not isinstance(other,Alien):
            self._explode = True
            self._w = explosion_range
            self._h = explosion_range
    
    def position(self):
        return self._x,self._y,self._w,self._h

    def symbol(self):
        if self._explode and self._i < len(self._explosion): #consuma lista contenente symbol dell'esplosione
            x,y,w,h = self._explosion[self._i]
            self._i += 1
            return x,y,w,h
        return 66,231,15,8


#CLASSE BACKGROUND
class Background:
    def __init__(self,y:int,speed:int,bg_type:int,arena:Arena):
        self._w,self._h = arena.size()
        self._y = y
        self._x1 = 0
        self._x2 = self._w
        self._speed = speed
        self._dx = -speed
        self._bg_type = bg_type #BG type if is 0 means the montains, 1 the climb, 2 floor
        self._backgrounds = []
        self.change_bg()
        if self._bg_type == 0:
            self._h = 280
        else:
            self._h = 127
        self._symbol = self._backgrounds[self._bg_type]

    def move(self):
        if self._x1 < -self._w and self._x2 < 0:
            self._x1 = 0
            self._x2 = self._w
        self._x1 += self._dx
        self._x2 += self._dx

    def change_bg(self):
        self._backgrounds = []
        with open("background.csv","r") as f1:
            csv = f1.read()
            row = csv.split("\n")
            for r in row:
                if r != "":
                    s = r.split(",")
                    self._backgrounds.append((int(s[0]),int(s[1]),int(s[2]),int(s[3])))
        self._symbol = self._backgrounds[self._bg_type]
    
    def position1(self):
        return self._x1,self._y,self._w,self._h
    def position2(self):
        return self._x2,self._y,self._w,self._h
    def symbol(self):
        return self._symbol
    def stay(self):
        self._dx = 0

    def restart(self):
        self._dx = -self._speed

#CLASSE BONUS
class Bonus(Actor):
    def __init__(self, arena, hero):
        self._arena = arena
        arena_w, arena_h = arena.size()
        self._x, self._y = arena_w, arena_h//2
        self._dx = -20
        self._w, self._h = 25, 15
        self._explode = False
        self._explosion = [(124, 270, 12, 12), (141, 269, 13, 14), (156, 268, 16, 16)]
        self._i = 0

    def move(self):
        self._x += self._dx

    def position(self):
        return self._x, self._y, self._w, self._h

    def symbol(self):
        if self._explode and self._i < len(self._explosion): #consuma lista contenente symbol dell'esplosione
            x,y,w,h = self._explosion[self._i]
            self._i += 1
            return x,y,w,h

        return 887, 228, 14, 14

    def collide(self, other):
        if isinstance(other, Bullet):
            b_dx,b_dy = other.direction()
            if b_dx == 0 and b_dy < 0:
                self._explode = True
                hero.transform()

#CLASSE BOUNCE
class Bounce(Actor):
    def __init__(self, arena, pos):
        self._start_x,self._start_y = pos
        self._x, self._y = self._start_x,self._start_y
        self._w, self._h = 40, 40
        self._speed = 5
        self._dx, self._dy = 0, 20
        self._arena = arena
        self._game_over = False
        self._explode = False
        self._hit_hole = False
        self._explosion=[(113,101,46,32),(165,101,42,32),(214,102,41,30),
                         (165,101,42,32),(214,102,41,30),(165,101,42,32),
                         (214,102,41,30),(263,117,32,16),(263,117,32,16)]
        self._symbol = []
        self._symbol_bullet = []
        self.change_symbol
        self._buffer = 0
        self._i_explosion = 0
        self._superman = False
        self._time_superman = 0
        arena.add(self)

    def move(self):
        arena_w, arena_h = self._arena.size()
        self._buffer += 1
        self._y += self._dy
        self._x += self._dx

        if not self._superman:
            self._dy += 0.2  # 0.2 è l'accelerazione gravitazionale

            if self._y > FLOOR - self._h - 1 and not self._hit_hole:
                self._y = FLOOR - self._h + 1

            if self._x >= 150 or self._x <= 50 or self._x == 100:
                self._dx = 0

            if self._y > 325 - self._h:
                self._dy = 0
                self._explode = True

            if self._explode and self._i_explosion >= len(self._explosion):
                self._game_over = True
        else:
            self._time_superman += 1

            if self._x >= 150:
                self._x = 149

            if self._x <= 50:
                self._x = 51

            if self._y >= FLOOR - self._h + 1:
                self._y = FLOOR - self._h + 1

            if self._time_superman > 300:
                self._time_superman = 0
                self._superman = False
                self._dy = 1

            if self._y <= 0:
                self._y = 0

            if self._x <= 0:
                self._x = 0

    def change_symbol(self):
        with open("hero_symbol.csv","r") as f1:
            csv = f1.read()
            row = csv.split("\n")
            for i,r in enumerate(row):
                if r != "":
                    s = r.split(",")
                    if i < 3:
                        self._symbol.append((int(s[0]),int(s[1]),int(s[2]),int(s[3])))
                    else:
                        self._symbol_bullet.append((int(s[0]),int(s[1]),int(s[2]),int(s[3])))

     
    def is_game_over(self) -> bool:
        return self._game_over

    def is_explode(self) -> bool:
        return self._explode
    
    def shoot(self):
        bx,by,bw,bh = self.position()
        if self._buffer > 10:
            Bullet(self._arena, (bx + bw + 1, by + bh / 2), 10, 0,self)
            self._buffer = 0
        Bullet(self._arena, (bx + bw / 4, by), 0, -15, self)
    
    def go_left(self):
        self._dx = -self._speed

    def go_right(self):
        self._dx = +self._speed

    def go_mid(self):
        if self._x < 100:
            self._dx = self._speed

        if self._x > 100:
            self._dx = -self._speed

    def fly_up(self):
        if self._superman:
            self._dy -= self._speed

    def fly_down(self):
        if self._superman:
            self._dy += self._speed

    def go_up(self):
        if not self._superman:
            arena_w, arena_h = self._arena.size()
            if self._y >= FLOOR - self._h and not self._explode and not self._hit_hole:
                self._dx, self._dy = 0, -self._speed

    def go_down(self):
        self._dx, self._dy = 0, +self._speed

    def stay(self):
        if self._superman:
            self._dx, self._dy = 0, 0

    def collide(self, other):
        if not self._superman:
            if isinstance(other,Hole) and not self._hit_hole:
                hx,hy,hw,hh = other.position()
                #self._x -= self._x - hx
                self._x -= self._x + self._w - hx
                self._hit_hole = True
                self._dy = 1
            elif not isinstance(other,Hole):
                self._explode = True

    def restart(self):
        self._game_over = False
        self._superman = False
        self._explode = False
        self._hit_hole = False
        self._i_explosion = 0
        self._x, self._y = self._start_x,self._start_y
        self._dx, self._dy = 0, 20
    
    def position(self):
        return self._x, self._y, self._w, self._h

    def symbol(self):
        arena_w, arena_h = self._arena.size()
        if self._explode and self._i_explosion < len(self._explosion):
            x,y,w,h = self._explosion[self._i_explosion]
            self._i_explosion += 1
            return x,y,w,h
        elif self._i_explosion >= len(self._explosion):
            self._game_over = True
        if not self._hit_hole:
            if self._y < arena_h - 90 - self._h:
                return self._symbol[1]
            else:
                return self._symbol[0]
        else:
            return self._symbol[2]
        
    def get_bullet_symbols(self):
        return self._symbol_bullet

    def transform(self):
        self._dy = 0
        self._superman = True

    def is_transformed(self):
        return self._superman

#CLASSE BULLET
class Bullet(Actor):
    def __init__(self, arena:Arena,pos:(int,int),dx:int,dy:int,hero=None):
        self._x, self._y = pos
        self._w, self._h = 15, 10
        self._dy, self._dx = dy, dx
        arena.add(self)
        if self._dx > 0 or dy < 0:
            self._explosion = [(225,142,6,7),(239,140,8,10),(253,138,12,14),(269,142,8,8),(283,140,10,12)]
        else:
            self._explosion = [(89,304,16,14),(106,304,16,14),(123,302,16,16),(143,296,26,22),(174,287,28,31)]
        if hero != None:
            self._bullet_symbol = hero.get_bullet_symbols()
        self._arena = arena
        self._i_explosion = 0
        self._explode = False
        self._movement = 0

    def move(self): 
        if not self._explode:
            self._x += self._dx
            self._y += self._dy
            if self._movement >= 25 and self._dx > 0:
                self.collide(self)
            if self._y + self._h < 0:
                self._arena.remove(self)
            if self._y >= FLOOR + 1:
                self.collide(self)
            self._movement += 1
        else:
            if self._i_explosion >= len(self._explosion):
                if self._dy > 0 and self._y >= 277 and random.randrange(10)==7:
                    self._arena.add(Hole(FLOOR,self._x-15,FLOOR_SPEED,self._arena))
                self._arena.remove(self)

    def collide(self,other):
        if isinstance(other,Bounce) or isinstance(other,Alien):
            self._arena.remove(self)
        else:
            if isinstance(other,Bullet):
                if self.direction() == other.direction() and self.direction() == (0,-10):
                    return
            self._explode = True
            if self._dy > 0:
                self._w = 25
                self._h = 30
                self._y -= self._h - 4
            else:
                self._w = 15
                self._h = 15

    def direction(self)->(int,int):
        return self._dx,self._dy
            
    def isExploded(self):
        return self._explode

    def position(self):
        return self._x, self._y, self._w, self._h

    def symbol(self):
        if self._dx > 0 and self._dy == 0 and not self._explode:
            return self._bullet_symbol[0]
        elif self._dy < 0 and self._dx == 0 and not self._explode:
            return self._bullet_symbol[1]
        elif self._dy >0 and self._dx == 0 and not self._explode:
            return 213,231,5,6
        
        if self._explode and self._i_explosion < len(self._explosion):
            x,y,w,h = self._explosion[self._i_explosion]
            self._i_explosion += 1
            return x,y,w,h

        return 0,0,0,0 

#CLASSE HOLE
class Hole(Actor):
    
    def __init__(self,y:int,x:int,speed:float,arena:Arena):
        self._arena = arena
        arena_w,arena_y = self._arena.size()
        self._x = x
        self._y = y
        self._dx = -speed
        self._arena.add(self)
        self._type = random.randrange(0,2)
        self._w = 60
        if self._type % 2 == 0:
            self._h = 30
        else:
            self._h = 26
    
    def move(self):
        self._x += self._dx
        if self._x < -self._w:
            self._arena.remove(self)

    def collide(self, other: 'Actor'):
            pass

    def position(self) -> (int, int, int, int):
        return self._x,self._y,self._w,self._h


    def symbol(self) -> (int, int, int, int):
        if self._type % 2 == 0:
            return 130,168,26,26
        else:
            return 153,141,25,21


#CLASSE ROCK
class Rock(Actor):
    def __init__(self,y:int,arena:Arena):
        arena_w,arena_h = arena.size()
        self._x = arena_w
        self._type = random.randrange(0,2)
        if self._type % 2 == 0:
            self._symbol = (95,201,15,15)
            self._w = 25
            self._h = 25
            self._life = 1
        else:
            self._symbol = (79,204,14,12)
            self._w = 45
            self._h = 40
            #esplosione bullet crea diverse collisioni, con life=8 servono 2 colpi per abbattere la roccia
            self._life = 8
        self._y = y - self._h
        self._dx = FLOOR_SPEED
        self._explosion = [(113,101,46,32),(165,101,42,32),(214,102,41,30),(263,117,32,16)]
        self._i_explosion = 0
        self._explode = False
        arena.add(self)
        self._arena = arena

    def move(self):
        self._x -= self._dx
        if self._x < -self._w:
            self._arena.remove(self)
        if self._explode and self._i_explosion >= len(self._explosion):
            self._arena.remove(self)
            
    def collide(self,other):
        if isinstance(other,Hole):
            self._x += 40
        elif not isinstance(other,Bounce): 
            self._life -= 1
            if self._life <= 0:
                self._explode = True
        
        
    def position(self):
        return self._x,self._y,self._w,self._h

    def symbol(self):
        if self._explode and self._i_explosion < len(self._explosion):
            x,y,w,h = self._explosion[self._i_explosion]
            self._i_explosion += 1
            return x,y,w,h
        
        return self._symbol



