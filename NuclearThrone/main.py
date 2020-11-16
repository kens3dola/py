from NuclearThrone.game import Game

game = Game()

while game.running:
    game.cur_menu.display_menu()
    game.game_loop()
