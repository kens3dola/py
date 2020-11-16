import pygame


class Menu:
    def __init__(self, game):
        self.game = game
        self.mid_w, self.mid_h = self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.offset = -100

    def draw_cursor(self):
        self.game.draw_text('*', 30, self.cursor_rect.x, self.cursor_rect.y)

    def blit_screen(self):
        self.game.scale_screen()


class MainMenu(Menu):

    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = 'Start'
        self.startx, self.starty = self.mid_w, self.mid_h + 40
        self.optionsx, self.optionsy = self.mid_w, self.mid_h + 80
        self.creditsx, self.creditsy = self.mid_w, self.mid_h + 120
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.event_handling()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text('Main Menu', 60, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 - 20)
            self.game.draw_text("Start Game", 40, self.startx, self.starty)
            self.game.draw_text("Options", 40, self.optionsx, self.optionsy)
            self.game.draw_text("Credits", 40, self.creditsx, self.creditsy)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
        elif self.game.UP:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'

    def check_input(self):
        self.move_cursor()
        if self.game.START:
            if self.state == 'Start':
                self.run_display = False
                self.game.playing = True
            elif self.state == 'Options':
                self.game.curr_menu = self.game.options
            elif self.state == 'Credits':
                self.game.curr_menu = self.game.credits
                self.run_display = False
