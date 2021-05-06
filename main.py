import pygame, os, subprocess, time, sys, json
from gamestate import GameState
# from gamestate import * # debug
from manager import PlayerInteractionManager
from shutil import copyfile
class Game:
    # Some constants, hope that the code wont contain any literal beside these
    SPRITE_PATH  = './sprites'
    CONFIG_FILE = './config.json'
    DATA_PATH = './data'
    LOG_PATH = 'log'
    EXEC_NAME = 'GAME'
    
    C_WHITE = (255,255,255)
    C_BLACK = (0,0,0)
    C_BLUE = (0, 140, 255)
    C_DARKBLUE = (0, 0, 255)
    C_RED = (255, 100, 100)
    C_DARKRED = (255, 0 ,0)
    C_GRAY = (200,200,200,128)
    C_LIGHTGRAY = (211, 211, 211)
    C_NEUTRAL = (180, 200, 255)
    C_DARKGREEN = (0, 128, 0)
    C_WALLCOLOR = (100, 100, 100)
    C_STARCOLOR = (255, 255, 0)
    
    def __init__(self):
        
        self.conf_obj = None
        with open(self.CONFIG_FILE,'r') as f:
            self.conf_obj = json.load(f)
            
        self.players_names = self.conf_obj["players_names"]
        self.game_state = GameState(self.conf_obj["initial_moves"], self.conf_obj["initial_drills"], self.conf_obj['layout'])
        self.size = self.game_state.size
        self.game_end = False
        self.pim = PlayerInteractionManager(self.DATA_PATH, self.EXEC_NAME)
        self.output_actions = [None, None]
        
        self.time_limit_per_turn = self.conf_obj['time_limit_per_turn']
        self.MAX_TURN = self.conf_obj['max_turn']
        self.end_turn = self.MAX_TURN
        self.turn = 0
        
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,32)
        pygame.init()

        self.FPS = 60 # sua cai nay de chay nhanh / cham chuong trinh, o day fps = ups (update per second)
        
        self.WIDTH = 1366
        self.HEIGHT = 768
        
        self.screen = pygame.display.set_mode((self.WIDTH,self.HEIGHT))

        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill((255,255,255))
        self.background = self.background.convert()
        self.screen.blit(self.background, (0,0))
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.p0_name, self.p1_name = self.players_names
        
        self.font_name = "calibri"
        self.font_big = pygame.font.SysFont(self.font_name, 50)
        self.font_scores = pygame.font.SysFont(self.font_name, 50, 'bold')
        self.font_point = pygame.font.SysFont(self.font_name, 18)
        
        self.img_name = [
            self.font_big.render(self.p0_name, True, self.C_DARKRED),
            self.font_big.render(self.p1_name, True, self.C_DARKBLUE)
        ]
        
        # load some ugly self-made sprites        
        
        sprite_size = (64, 64)
        self.drill_sprite = pygame.image.load('{}/{}'.format(self.SPRITE_PATH, 'drill.png'))
        self.drill_sprite = pygame.transform.scale(self.drill_sprite, sprite_size)
        
        self.land_sprite = pygame.image.load('{}/{}'.format(self.SPRITE_PATH, 'landcount-2.png'))
        self.land_sprite = pygame.transform.scale(self.land_sprite, sprite_size)
        
        self.cell_sprite = pygame.image.load('{}/{}'.format(self.SPRITE_PATH, 'landpoint-2.png'))
        self.cell_sprite = pygame.transform.scale(self.cell_sprite, sprite_size)
        
        self.boot_sprite = pygame.image.load('{}/{}'.format(self.SPRITE_PATH, 'boot.png'))
        self.boot_sprite = pygame.transform.scale(self.boot_sprite, sprite_size)
        
    def run_player_program(self):
        # generate log file for each turn
        for turn in range(self.MAX_TURN):
            print('turn: {}'.format(turn))
            for plr_idx in range(2):   
                self.pim.write_input(self.turn, self.game_state, plr_idx)
                
                timer = time.time()
                self.pim.start_process(plr_idx, self.time_limit_per_turn)
                timer = time.time()-timer
                
                print('get output of {} in {:.4f} s'.format(plr_idx, timer))
                # copy file .OUT to file .log
                src = '{}/player{}/{}.OUT'.format(self.DATA_PATH,plr_idx,self.EXEC_NAME) \
                    if os.path.isfile('{}/player{}/{}.OUT'.format(self.DATA_PATH,plr_idx,self.EXEC_NAME)) else 'nul'
                dst = '{}/{:03d}_output{}.log'.format(self.LOG_PATH, turn, plr_idx)
                copyfile(src, dst)
                
                self.output_actions[plr_idx] = self.pim.read_output(self.game_state, plr_idx)
                self.pim.remove_output(plr_idx)
            # copy file .INP to file .log
            copyfile('{}/player0/{}.INP'.format(self.DATA_PATH, self.EXEC_NAME), \
                     '{}/{:03d}_input.log'.format(self.LOG_PATH, turn))
            
            # Update the game state
            self.game_state.update_intentions(self.output_actions[0], self.output_actions[1])
            self.game_state.update_actions()
            self.game_state.board.update_zones()
            self.game_state.board.remove_full_zones()
            
            if self.game_state.check_endgame():
                self.end_turn = turn
                break
            
        print('Game ends at turn {}'.format(turn))
            

    def run(self):
        self.game_state = GameState(self.conf_obj["initial_moves"], self.conf_obj["initial_drills"], self.conf_obj['layout']) # reset
        self.game_state.update_players_points()
        cycle = -1 # play: set cycle = -1
        update_phase_timer = 0
        phase_interval = self.conf_obj["time_per_display_phase"]

        clock = self.clock
        playtime = 0
        while self.running:
            miliseconds = clock.tick(self.FPS)
            playtime += miliseconds / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            text = "FPS: {0:2f}   Playtime: {1:2f}".format(clock.get_fps(), playtime)
            pygame.display.set_caption(text)
            
            # update by timer
            update_phase_timer += miliseconds/1000
            if self.turn < self.end_turn and update_phase_timer > phase_interval:
                update_phase_timer = 0 
                cycle += 1
                cycle %= 5
            
                if cycle == 0:
                    # simulate write input, run program, get output, ...
                    # actually just read log file gen from self.run_player_program()
                    for plr_idx in range(2):       
                        copyfile('{}/{:03d}_output{}.log'.format(self.LOG_PATH, self.turn, plr_idx), \
                                 '{}/player{}/{}.OUT'.format(self.DATA_PATH, plr_idx, self.EXEC_NAME))
                        self.output_actions[plr_idx] = self.pim.read_output(self.game_state, plr_idx)
                    self.turn += 1
                elif cycle == 1:
                    # display intention
                    self.game_state.update_intentions(self.output_actions[0], self.output_actions[1])
                    
                elif cycle == 2:
                    # display actions
                    self.game_state.update_actions()
                    self.game_state.update_players_points()  
                    self.game_state.intentions = [None, None]
                    
                elif cycle == 3:
                    # update_zones
                    self.game_state.board.update_zones()
                    self.game_state.update_players_points()
                    
                elif cycle == 4:
                    # remove full zones
                    self.game_state.board.remove_full_zones()
                    
            self.draw()
            pygame.display.flip()
    
    def update(self):
        pass
    
    def display(self):
        self.game_state.display()
    
    def draw(self):
        self.screen.blit(self.background, (0, 0)) # clear screen
        self.draw_board()
        self.draw_intentions()
        self.draw_scores()
        
    def draw_board(self):
        size = self.size
        board = self.game_state.board
        cells = board.cells
        zones = board.zones
        screen = self.screen
        HEIGHT = self.HEIGHT
        
        top, left = 10, 10
        
        cell_size = (HEIGHT-10) // size

        pygame.draw.rect(screen, self.C_LIGHTGRAY, (left-2, top-2, size * cell_size + 4, size * cell_size + 4))

        for i in range(size):
            for j in range(size):
                cell_color = [self.C_RED, self.C_BLUE, self.C_GRAY][cells[i][j].color]
                
                pygame.draw.rect(screen, cell_color, (left + j * cell_size+1, top + i * cell_size+1, cell_size-2, cell_size-2))
                
                if cells[i][j].has_wall:
                    pygame.draw.rect(screen, self.C_WALLCOLOR, (left + j * cell_size+3, top + i * cell_size+3, cell_size-6, cell_size-6))
                        
                if self.conf_obj["draw_cell_point"]:
                    img_point = self.font_point.render('{}'.format(cells[i][j].point), True, self.C_BLACK)
                    rect = img_point.get_rect()
                    rect.center = (left+j*cell_size+cell_size//2, top+i*cell_size+cell_size//2)
                    self.screen.blit(img_point, rect)
                    
        for zone in zones:
            r, c, w, h = zone.r, zone.c, zone.w, zone.h
            pygame.draw.rect(screen, (128,128,128), (left + c * cell_size, top + r * cell_size, w*cell_size, h*cell_size), 3)
        
    def draw_intentions(self):
        size = self.size
        screen = self.screen
        intentions = self.game_state.intentions
        HEIGHT = self.HEIGHT
        
        top, left = 10, 10
        cell_size = (HEIGHT-10) // size
        if intentions == [None, None]:
            return 
        color_cell = [(*self.C_DARKRED, 30), (*self.C_DARKBLUE, 30)]
        line_width = 4
        for i in range(size):
            for j in range(size):
                if intentions[0][i][j] != 0 and intentions[1][i][j] != 0:
                    top_p = top + i * cell_size+1
                    left_p = left + j * cell_size+1
                    right_p = left_p + cell_size-2
                    bot_p = top_p + cell_size-2
                    closed = False
                    pygame.draw.lines(screen, color_cell[0], closed, [(left_p, top_p), (left_p, bot_p), (right_p, bot_p)], line_width)
                    pygame.draw.lines(screen, color_cell[1], closed, [(right_p, bot_p), (right_p, top_p), (left_p, top_p)], line_width)
                else:
                    for color in range(2):
                        if intentions[color][i][j] != 0:
                            pygame.draw.rect(screen, color_cell[color], (top + j * cell_size+1, left + i * cell_size+1, cell_size-2, cell_size-2), line_width)
        
        
    def draw_scores(self):
        WIDTH = self.WIDTH
        players = self.game_state.players

        img_turn = self.font_big.render('Turn: {} {}'.format(self.turn, '(End)' if self.turn == self.MAX_TURN else ''), True, (80, 180, 255))

        right = 550
        self.screen.blit(img_turn, (WIDTH-right, 20))
        
        for plr_idx in range(2):
            offset = plr_idx*300
            self.screen.blit(self.img_name[plr_idx], (WIDTH-right, 100+offset))
            icons = [self.land_sprite, self.cell_sprite, self.boot_sprite, self.drill_sprite]
            points = [players[plr_idx].land_point, 
                    players[plr_idx].cell_point,
                    players[plr_idx].avail_moves,
                    players[plr_idx].avail_wall_break]
            for idx,icon in enumerate(icons):
                offset_icons = idx*150
                self.screen.blit(icon, (WIDTH-right + offset_icons, 175+offset))
                img_score = self.font_scores.render("{}".format(points[idx]), True, [self.C_DARKRED, self.C_DARKBLUE][plr_idx])
                rect = img_score.get_rect()
                rect.center = (WIDTH-right + 32 + offset_icons, 275+offset)
                self.screen.blit(img_score, rect)
            
if __name__ == '__main__':
    game = Game()
    if len(sys.argv) == 1:
        game.run_player_program()
        game.run()
    else:
        mode = int(sys.argv[1])
        if mode == 0:
            game.run_player_program()
        else:
            game.run()