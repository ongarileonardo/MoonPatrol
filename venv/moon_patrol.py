import g2d
from actor import Arena
from moon_patrol_game import MoonPatrolGame
from moon_patrol_gui  import MoonPatrolGui

game = MoonPatrolGame('moon_patrol_game.csv')

def gui_play(game: MoonPatrolGame):
        g2d.init_canvas(game.arena().size())
        ui = MoonPatrolGui(game)
        g2d.main_loop(ui.tick)

def main():
    g2d.init_canvas(game.arena().size())
    g2d.main_loop(tick)

gui_play(game)
