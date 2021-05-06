class Color:
    ''' enum color '''
    RED = 0
    BLUE = 1
    NONE = 2
    
class Action:
    ''' data class for an action '''
    def __init__(self, r, c):
        self.r = r 
        self.c = c
    def __repr__(self):
        return "Action({}, {})".format(self.r, self.c)

class Zone:
    ''' data class for a zone '''
    def __init__(self, r, c, w, h, max_cells):
        self.r = r 
        self.c = c
        self.w = w
        self.h = h
        self.max_cells = max_cells
        self.full = False
        self.indices = []
        for i in range(r,r+h):
            for j in range(c,c+w):
                self.indices.append((i,j))

class Cell:
    ''' data class for a cell '''
    def __init__(self):
        self.color = Color.NONE
        self.point = 0
        self.has_wall = False
        self.has_star = False

class Board:
    ''' Board: consists of cells and zones '''
    def __init__(self, size, zones, players):
        self.size = size
        self.cells = [[Cell() for j in range(size)] for i in range(size)]
        self.zones = zones
        self.players = players
        
    def inside(self, r, c):
        size = self.size
        return 0 <= r < size and 0 <= c < size
    
    def check_neighbor(self, r, c, color):
        '''
            return True if a neighbor has the same color with argument color
        '''
        td = [0, 1, 0, -1]
        tc = [1, 0, -1, 0]
        cells = self.cells
        for k in range(4):
            vr = r + td[k] 
            vc = c + tc[k]
            if self.inside(vr, vc) and cells[vr][vc].color == color:
                return True
        return False
        
    def update_zones(self):
        '''
            Update all the zones follow by rules
        '''
        cells = self.cells
        players = self.players
        
        def count_cells(zone):
            count = [0, 0]
            for i,j in zone.indices:
                if cells[i][j].color != Color.NONE:
                    count[cells[i][j].color] += 1
            return count
                
        for idx, zone in enumerate(self.zones):
            red_cells, blue_cells = count_cells(zone)
            if red_cells == blue_cells and red_cells + blue_cells >= 2*zone.max_cells: # both will die out, turn this zone to all wall
                for i, j in zone.indices:
                    cells[i][j].color = Color.NONE
                    cells[i][j].has_wall = True
                    
                    
                zone.full = True
            else: # one color claim this zone
                for color, cell_cnt in enumerate([red_cells, blue_cells]):
                    if cell_cnt >= zone.max_cells:
                        for i, j in zone.indices:
                            cells[i][j].color = [Color.RED, Color.BLUE][color]
                                
                            cells[i][j].has_wall = False
                        
                        zone.full = True
                 
    def remove_full_zones(self):
        # remove 'triggered' zone 
        self.zones = [zone for zone in self.zones if not zone.full]
            
    def calculate_points(self):
        points = [[0,0], [0,0]]
        size = self.size
        cells = self.cells
        for i in range(size):
            for j in range(size):
                if cells[i][j].color != Color.NONE:
                    points[cells[i][j].color][0] += 1
                    points[cells[i][j].color][1] += cells[i][j].point
                    
        return points
    
    def display(self):
        size = self.size
        cells = self.cells
        for i in range(size):
            for j in range(size):
                print("(r,c) = {} | {}".format((i, j), cells[i][j].__dict__))

class Player:
    def __init__(self, color, avail_moves, avail_wall_break):
        self.color = color
        self.land_point = 0
        self.cell_point = 0
        self.avail_moves = avail_moves
        self.avail_wall_break = avail_wall_break
        
    def __repr__(self):
        return "{} | {}".format((self.land_point, self.cell_point), (self.avail_moves, self.avail_wall_break))
            
    def display(self):
        print()
        print("PLAYER {}".format(self.color))
        print("land, point = {}, {}".format(self.land_point, self.cell_point))
        print("moves = {}".format(self.avail_moves))
        print("wall_break = {}".format(self.avail_wall_break))
        

class GameState:
    ''' This class contains the current game state'''
    def __init__(self, initial_moves, initial_drills, layout_file=None):
                    
        layout_file = 'maps/{}'.format(layout_file)
        content = None
        with open(layout_file, 'r') as f:
            content = f.read().split('\n')
            
        self.size = int(content[0])
        self.players = [Player(color, initial_moves, initial_drills) for color in [Color.RED, Color.BLUE]]
        
        self.intentions = [None, None]
        
        self.board = Board(self.size, [], self.players)
        
        for i in range(self.size):
            line = content[i+1].split(' ')
            for j in range(self.size):
                self.board.cells[i][j].color = int(line[j])
                
        for i in range(self.size):
            line = content[i+self.size+2].split(' ')
            for j in range(self.size):
                if line[j] == '1':
                    self.board.cells[i][j].has_star = True
                elif line[j] == '2':
                    self.board.cells[i][j].has_wall = True
                    
        for i in range(self.size):
            line = content[i+2*self.size+3].split(' ')
            for j in range(self.size):
                self.board.cells[i][j].point = int(line[j])
                
        nZone = int(content[3*self.size+4])
        for i in range(nZone):
            line = content[i+3*self.size+5].split(' ')
            self.board.zones.append(Zone(*[int(s) for s in line]))
                    
            
    def convert_actions_to_buffer(self, color, actions):
        board = self.board
        size = self.size
        cells = board.cells
        
        buff = [[0 for j in range(size)] for i in range(size)]
        for action in actions:
            r = action.r 
            c = action.c 
            color_name = ['RED', 'BLUE']
            msg = ""
            # check conditions to set 
            if not board.inside(r, c):
                msg += '{} not inside board'.format((r, c))
                
            elif not board.check_neighbor(r, c, color):
                msg += '{} dont have color {} in neighbors'.format((r, c), color)
                buff[r][c] = -1
                
            elif cells[r][c].color != Color.NONE:
                msg += '{} has been occupied by {}'.format((r, c), cells[r][c].color)
                buff[r][c] = -2
                
            else: # blank cell, can set here
                msg += '{} can be set'.format((r, c))
                if cells[r][c].has_wall:
                    msg += ',has wall'
                if cells[r][c].has_star:
                    msg += ',has star'
                
                buff[r][c] = 1
                
            # print("{}, {}".format(color_name[color], msg))
            
        return buff
    
    ''' Two craps functions, should have written better''' 
    def update_intentions(self, red_actions, blue_actions):
        
        self.intentions = [None, None]
        self.intentions[0] = self.convert_actions_to_buffer(Color.RED, red_actions)
        self.intentions[1] = self.convert_actions_to_buffer(Color.BLUE, blue_actions)
    
    def update_actions(self, red_actions=None, blue_actions=None):
        
        buff = [None, None]
        if red_actions is None and blue_actions is None:
            buff = [self.intentions[0], self.intentions[1]]
        else:
            buff[0] = self.convert_actions_to_buffer(Color.RED, red_actions)
            buff[1] = self.convert_actions_to_buffer(Color.BLUE, blue_actions)
        
        size = self.size
        cells = self.board.cells
        
        for i in range(size):
            for j in range(size):
                if buff[0][i][j] == 1 and buff[1][i][j] == 1: # conflict
                                    
                    if cells[i][j].has_wall: 
                        pass # nothing happened 
                      

                else: # just one player move into this cell
                    for color in range(2):
                        if buff[color][i][j] == 1:
                            can_move = True
                            
                            if cells[i][j].has_wall:
                                if self.players[color].avail_wall_break > 0: # can move if have drills left
                                    self.players[color].avail_wall_break -= 1
                                    cells[i][j].has_wall = False
                                else:
                                    can_move = False
                                    
                            
                            
                            if can_move:
                                cells[i][j].color = color
      
    def update_players_points(self):
        points = self.board.calculate_points()
        for idx, player in enumerate(self.players):
            player.land_point, player.cell_point = points[idx]

    def check_endgame(self):
        cells = self.board.cells
        players = self.players
        
        for color in range(2):
            for i in range(self.size):
                for j in range(self.size):
                    if cells[i][j].color == Color.NONE:
                        if self.board.check_neighbor(i, j, color):
                            return False
                    elif cells[i][j].has_wall:
                        if players[color].avail_wall_break > 0:
                            return False
        return True
                                
    def display(self):
        self.board.display()
        for player in self.players:
            player.display()