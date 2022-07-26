import g2d
from moon_patrol_game import MoonPatrolGame
from moon_patrol_game import Background

HEROES_SYMBOLS = [[(247,159,32,23),(48,153,27,27),(81,154,28,27),(193, 143, 10, 4),(225,142,6,7)],
                  [(211,159,32,23),(46,104,27,27),(79,105,28,27),(193, 143, 10, 4),(225,142,6,7)],
                  [(16,244,29,25),(20,274,18,27),(21,309,21,20),(260,19,30,26),(258,223,28,31)],
                  [(57,256,30,25),(51,290,27,39),(44,334,38,29),(11,53,29,25),(8,5,20,41)],
                  [(235,299,41,23),(242,332,30,30),(248,371,32,24),(239,48,18,13),(225,12,17,16)]]

BACKGROUNDS_SYMBOLS = [[(0,0,512,256),(0,258,512,127),(0,513,512,127)],
                       [(0,0,512,256),(0,385,512,127),(0,513,512,127)],
                       [(0,804,512,243),(0,258,512,127),(0,656,512,132)]]

class MoonPatrolGui:
    def __init__(self,game):
        self._game = game
        self._sprite_img = g2d.load_image("moon-patrol-sprites.png")
        self._bg_image = g2d.load_image("moon_patrol_bg.png")
        self._game_over_img = g2d.load_image("game_over.png")
        self._level_complete_img = g2d.load_image("level_complete.png")
        self._level = 1
        self._i_heroes = 0
        self._i = 0

    def tick(self):
        self.update_image()
        if self._game.started():
            if not self._game.hero().is_game_over() and (not self._game.is_level_finished() or self._level >= len(BACKGROUNDS_SYMBOLS)):
                if not self._game.hero().is_explode():
                    if g2d.key_pressed("ArrowUp"):
                        self._game.hero().fly_up()

                    if g2d.key_pressed("ArrowDown"):
                        self._game.hero().fly_down()

                    if g2d.key_pressed("ArrowLeft"):
                        self._game.hero().go_left()

                    if g2d.key_pressed("ArrowRight"):
                        self._game.hero().go_right()

                    if g2d.key_released("ArrowRight") or g2d.key_released("ArrowLeft"):
                        if self._game.hero().is_transformed():
                            self._game.hero().stay()
                        else:
                            self._game.hero().go_mid()

                    if g2d.key_released("ArrowUp") or g2d.key_released("ArrowDown"):
                        self._game.hero().stay()

                    if g2d.key_pressed("x") or g2d.key_pressed("X"):
                        self._game.hero().shoot()
                          
                    if g2d.key_pressed("Spacebar"):
                        self._game.hero().go_up()
                            
                    if g2d.key_pressed("p") or g2d.key_pressed("P"):
                        self._game.hero().transform()

                    self._game.add_actor()
                    self._game.move_all()
                    
            elif self._game.is_level_finished():
                if g2d.key_pressed("Enter"):
                    self._level += 1
                    self.change_bg_symbol()
                    self._game.next_level()
            else:
                if g2d.key_pressed("Enter"):
                    self._level = 1
                    self._game.restart()
        else:
            if g2d.key_pressed("ArrowRight") and self._i_heroes < len(HEROES_SYMBOLS)-1:
                self._i_heroes += 1
            if g2d.key_pressed("ArrowLeft") and self._i_heroes > 0:
                self._i_heroes -= 1
            if g2d.key_pressed("Enter"):
                self.change_bg_symbol()
                self.change_hero_csv()
                self._game.start()
    
    def change_hero_csv(self):
        with open("hero_symbol.csv","w") as f1:
            for r in HEROES_SYMBOLS[self._i_heroes]:
                sx,sy,sw,sh = r
                f1.write(str(sx)+","+str(sy)+","+str(sw)+","+str(sh)+"\n")
        self._game.change_hero()
        
    def change_bg_symbol(self):
        with open("background.csv","w") as f1:
            for r in BACKGROUNDS_SYMBOLS[self._level-1]:
                sx,sy,sw,sh = r
                f1.write(str(sx)+","+str(sy)+","+str(sw)+","+str(sh)+"\n")
        self._game.change_bg()
        

    def draw_score(self):
        ARENA_W,ARENA_H = self._game.arena().size()
        BORDER = 30
        H_RECT = 30
        TEXT_SIZE = (30,20)
        SCORE_RECT = (0,ARENA_H - H_RECT,ARENA_W,H_RECT)
        
        g2d.set_color((0,0,255))
        g2d.fill_rect(SCORE_RECT)
        g2d.set_color((255,255,255))
        g2d.draw_text(str(self._game.get_score())+ 'm',(BORDER,ARENA_H-H_RECT+BORDER/6),TEXT_SIZE)
        g2d.draw_text('Best: ' + str(self._game.get_record()) + 'm',(ARENA_W - BORDER*4,ARENA_H-H_RECT+BORDER/6),TEXT_SIZE)
        if self._level < len(BACKGROUNDS_SYMBOLS):
            text = 'reach 400 to advance'
        else:
            text = 'Go for the record'
        g2d.draw_text((text),(ARENA_W/2 - BORDER*3,ARENA_H-H_RECT+BORDER/6),TEXT_SIZE)
        
        
    def update_image(self):
        ARENA_W,ARENA_H = self._game.arena().size()
        g2d.clear_canvas()
        if self._game.started() and not self._game.hero().is_game_over():
            if not self._game.is_level_finished() or self._level >= len(BACKGROUNDS_SYMBOLS):
                for b in self._game.get_background():
                    g2d.draw_image_clip(self._bg_image, b.symbol(), b.position1())
                    g2d.draw_image_clip(self._bg_image, b.symbol(), b.position2())
                
                for a in self._game.arena().actors():
                    if not a is(self._game.hero()):
                        g2d.draw_image_clip(self._sprite_img, a.symbol(), a.position())
                if not self._game.is_game_over():   
                    g2d.draw_image_clip(self._sprite_img,self._game.hero().symbol(),self._game.hero().position())
                self.draw_score()
            else:
                g2d.draw_image(self._level_complete_img,(0,0,ARENA_W,ARENA_H))
        elif self._game.hero().is_game_over():
            g2d.draw_image(self._game_over_img,(0,0,ARENA_W,ARENA_H))
            if self._game.new_best():
                name = g2d.prompt('NUOVO RECORD!!! INSERISCI IL TUO NOME')
                self._game.subscribe_best(name)
            self._level = 1
            self.change_bg_symbol()
        else:
            LOGO_W,LOGO_H = 136,81
            hx,hy,hw,hh = HEROES_SYMBOLS[self._i_heroes][0]
            g2d.set_color((0,0,0))
            g2d.fill_rect((0,0,ARENA_W,ARENA_H))
            g2d.draw_image_clip(self._sprite_img,(75,5,LOGO_W,LOGO_H),(ARENA_W/2-LOGO_W/2,ARENA_H/8,LOGO_W,LOGO_H))
            if self._i >= 20:
                if self._i >= 40:
                     g2d.set_color((0,0,0))
                     self._i = 0
                else:
                    g2d.set_color((0,255,0))
            g2d.draw_image_clip(self._sprite_img,(hx,hy,hw,hh),(ARENA_W/2-hw*1.5,ARENA_H/2,hw*2,hh*3))
            g2d.draw_text('PRESS ENTER TO START',(ARENA_W/6,300),(30,30))
            self._i += 1
        
