import pygame
from gamestate import Action
import subprocess, os
from threading import Timer
from shutil import copyfile
from gamestate import *

class PlayerInteractionManager:
    ''' This class is mainly use for interact with player:
    - write game state
    - run player's program
    - read output actions
    '''

    def __init__(self, path, exec_name):
        self.path = path
        self.exec_name = exec_name
        
    def write_input(self, turn, game_state, color):
        gs = game_state
        with open('{}/player{}/{}.INP'.format(self.path, color, self.exec_name),'w') as f:
            f.write("{} {}\n".format(turn, color))
            
            f.write("{size} {moves} {wall_break} \n".format(
                    size=gs.size, 
                    moves=gs.players[color].avail_moves, 
                    wall_break=gs.players[color].avail_wall_break))
            
            # write the board state
            board = gs.board
            
                # color
            board_str = ""
            for i in range(gs.size):
                for j in range(gs.size):
                    board_str += str(board.cells[i][j].color) + ' '
                board_str += '\n'
            f.write(board_str)
            f.write('\n')
            
                # star, wall
            item_str = ""
            for i in range(gs.size):
                for j in range(gs.size):
                    wall = board.cells[i][j].has_wall
                    star = board.cells[i][j].has_star
                    idx = 2 if star else 1 if wall else 0
                    item_str += str(idx) + ' '
                item_str += '\n'
            f.write(item_str)
            f.write('\n')
            
                # point
            point_str = ""
            for i in range(gs.size):
                for j in range(gs.size):
                    point_str += str(board.cells[i][j].point) + ' '
                point_str += '\n'
            f.write(point_str)
            f.write('\n')
            
                # zones
            f.write("{nZones}\n".format(nZones=len(board.zones)))
            zones_str = ""
            for zone in board.zones:
                zones_str += "{} {} {} {} {}\n".format(zone.r, zone.c, zone.w, zone.h, zone.max_cells)
            f.write(zones_str)
        
    def read_output(self, game_state, color):
        try:
            with open('{}/player{}/{}.OUT'.format(self.path, color, self.exec_name),'r') as f:
                txt = f.readlines()
                
            gs = game_state
            nLines = len(txt)
            actions = []
            for i in range(min(gs.players[color].avail_moves, nLines)):
                line = txt[i]
                try:
                    tokens = line.split(' ')
                    r = int(tokens[0])
                    c = int(tokens[1])
                    actions.append(Action(r, c))
                except Exception as e:
                    print(e, 'at line {}'.format(i))
            return actions
        except Exception as e:
            print(e)
            return []
        
    def start_process(self, color, time_limit):
        t = Timer(time_limit, lambda: subprocess.run("taskkill /f /im {}.exe".format(self.exec_name),shell=False))
        t.start()
        os.chdir('{}/player{}'.format(self.path, color))
        subprocess.run("{}.exe".format(self.exec_name),shell=False)
        os.chdir('..')
        os.chdir('..')
        t.cancel()
        
    def remove_output(self, color):
        try:
            os.remove("{}/player{}/{}.OUT".format(self.path, color, self.exec_name))
        except Exception as e:
            pass