import pyglet
import random
import math
import numpy as np

class Apple:
    def __init__(self, size, density, location):
        self.location = location
        self.pos = {'x': 0, 'y': 0}
        self.temp = size
        self.density = density
        self.size = size - 5
        self.square = pyglet.shapes.Rectangle(x=size/2, y=size/2, width=self.size, height=self.size, color=(213, 32, 39))
        self.square.anchor_position = self.size/2, self.size/2
        
        
    def randomize(self, body):
        occupied = []
        for i in body:
            occupied.append((i.pos['x'], i.pos['y']))
        
        positions = []
        for i in range(self.density):
            for j in range(self.density):
                if (i , j) not in occupied:
                    positions.append((i, j))
        
        pos = random.choice(positions)
        self.pos['x'] = pos[0]
        self.pos['y'] = pos[1]

    def draw(self):
        self.square.position = (self.pos['x'] * self.temp) + self.temp/2 + self.location[0], (self.pos['y'] * self.temp) + self.temp/2 + self.location[1]
        self.square.draw()

class CubeHead:
    def __init__(self, size, density, location):
        self.location = location
        self.pos = {'x': random.randint(0, density - 1), 'y': random.randint(0, density - 1)}
        self.temp = size
        self.direction = 'Up'
        self.size = size - 5
        self.square = pyglet.shapes.Rectangle(x=size/2, y=size/2, width=self.size, height=self.size, color=(248, 238, 227))
        self.square.anchor_position = self.size/2, self.size/2

    def move(self):
        if self.direction == 'Up':
            self.pos['y'] += 1
        elif self.direction == 'Right':
            self.pos['x'] += 1
        elif self.direction == 'Down':
            self.pos['y'] -= 1
        elif self.direction == 'Left':
            self.pos['x'] -= 1

    def draw(self):
        self.square.position = (self.pos['x'] * self.temp) + self.temp/2 + self.location[0], (self.pos['y'] * self.temp) + self.temp/2 + self.location[1]
        self.square.draw()

class Cube:
    def __init__(self, size, x, y, location):
        self.location = location
        self.pos = {'x': x, 'y': y}
        self.new = True
        self.temp = size
        self.direction = 'Up'
        self.size = size - 5
        self.sizeinner = self.size - 20
        self.square = pyglet.shapes.Rectangle(x=size/2, y=size/2, width=self.size, height=self.size, color=(255, 176, 73))
        self.square.anchor_position = self.size/2, self.size/2
    def draw(self):
        self.square.position = (self.pos['x'] * self.temp) + self.temp/2 + self.location[0], (self.pos['y'] * self.temp) + self.temp/2 + self.location[1]
        self.square.draw()

class Game:
    def __init__(self, window, windowSize, location, density = 4):
        self.location = location
        self.score = 0
        self.NoWork= 0
        self.N_frames = 0
        self.end = False

        self.body = []
        self.changeDelay = False
        self.density = density

        self.size = windowSize
        self.window = window
        self.cubeSize = self.size / self.density
    
        pyglet.font.add_file('retro_computer_personal_use.ttf')
        customFont = pyglet.font.load('Retro Computer')

        self.scoreLabel = pyglet.text.Label(f'Score: {self.score}',
                          font_name='Retro Computer',
                          font_size=16,
                          x=self.size - 150 + location[0], y = 10 + location[1], color=(255, 255, 255, 255), bold=False)

        self.head = CubeHead(self.cubeSize, self.density, location)
        self.body.append(self.head)
        self.apple = Apple(self.cubeSize, self.density, location)
        self.apple.randomize(self.body)

        #self.window.event(self.on_key_press)

        # Set update function to run every 1/60 seconds
        
    def on_key_press(self, symbol, modifiers):
        if self.changeDelay == False:
            if symbol == pyglet.window.key.UP and self.head.direction != 'Down':
                self.head.direction = 'Up'
                #self.update()
            elif symbol == pyglet.window.key.DOWN and self.head.direction != 'Up':
                self.head.direction = 'Down'
                #self.update()
            elif symbol == pyglet.window.key.RIGHT and self.head.direction != 'Left':
                self.head.direction = 'Right'
                #self.update()
            elif symbol == pyglet.window.key.LEFT and self.head.direction != 'Right':
                self.head.direction = 'Left'
                #self.update()

    def play_step(self, final_move):
        
        if final_move[0] == 1 and self.head.direction != 'Down':
            self.head.direction = 'Up'
        elif final_move[1] == 1 and self.head.direction != 'Up':
            self.head.direction = 'Down'
        elif final_move[2] == 1 and self.head.direction != 'Left':
            self.head.direction = 'Right'
        elif final_move[3] == 1 and self.head.direction != 'Right':
            self.head.direction = 'Left'

        old_distance = math.sqrt(pow(self.apple.pos['x'] - self.head.pos['x'], 2) + pow(self.apple.pos['y'] - self.head.pos['y'], 2))

        self.moveBody()
        self.head.move()
        done = self.checkCollision()
        previousScore = self.score 
        reward = (self.checkApple() - (self.NoWork / 14))

        new_distance = math.sqrt(pow(self.apple.pos['x'] - self.head.pos['x'], 2) + pow(self.apple.pos['y'] - self.head.pos['y'], 2))

        if reward != 10 and new_distance < old_distance:
            reward = 5
        
        if previousScore == self.score:
            self.NoWork += 1
        self.changeDelay = False

        self.N_frames += 1

        if self.NoWork > 100:
            print('Stuck in loop')
            done = True
        
        if done == True: 
            reward = -20
        return (reward, done, self.score)
        
    def reset(self):
        self.score = 0
        self.body = []
        self.NoWork = 0

        self.head.pos = {'x': random.randint(0, self.density - 1), 'y': random.randint(0, self.density - 1)}
        self.body.append(self.head)
        self.apple.randomize(self.body)
        
    def checkCollision(self):
        x = self.head.pos['x']
        y = self.head.pos['y']
        if x < 0 or y < 0 or x > (self.density - 1) or y > (self.density - 1):
            #print("Game Over")
            return 1
            
        occupied = []
        for i in range(1, len(self.body)):
            occupied.append((self.body[i].pos['x'], self.body[i].pos['y']))
        if (x, y) in occupied:           
            #print("Game Over")
            return 1
        return 0
            
    def moveBody(self):
        for i in reversed(range(1, len(self.body))):
            self.body[i].pos['x'] = self.body[i - 1].pos['x']
            self.body[i].pos['y'] = self.body[i - 1].pos['y']
            self.body[i].direction = self.body[i - 1].direction

    def checkApple(self):
        if self.apple.pos['x'] == self.head.pos['x'] and self.apple.pos['y'] == self.head.pos['y']:
            self.score += 1
            self.NoWork = 0
            if self.score == self.density * self.density:
                print("Game Completed")
                self.reset()
                return 10
            self.apple.randomize(self.body)
            cube = Cube(self.cubeSize, self.body[-1].pos['x'], self.body[-1].pos['y'], self.location)
            self.body.append(cube)
            return 10
        return 0

    def get_state(self):
        x, y = (self.head.pos['x'], self.head.pos['y'])  
        directions = [(x-1, y+1), (x, y+1), (x+1, y+1), (x+1, y), (x+1, y -1), (x, y - 1), (x -1, y -1), (x-1, y)]
        # print('x and y', x, y)
        # print('DIRECTIONS', directions)

        state = []
        occupied = []
        for i in self.body:
            occupied.append((i.pos['x'], i.pos['y']))
        #empty space
        for i in directions:
            if i[0] >= 0 and i[0] < self.density and i[1] >= 0 and i[1] < self.density and i not in occupied:
                state.append(1)
            else:
                state.append(0)
        #snake detections
        for i in directions:
            if i in occupied:
                state.append(1)
            else:
                state.append(0)
        applex, appley = (self.apple.pos['x'], self.apple.pos['y'])
        # print('APPLE', applex, appley)
        #snake
        if applex < x and appley > y and (abs(applex - x) == abs(appley -y)):
            state.append(1)
        else:
            state.append(0)

        if applex == x and appley > y:
            state.append(1)
        else:
            state.append(0)
        
        if applex > x and appley > y and (abs(applex - x) == abs(appley -y)):
            state.append(1)
        else:
            state.append(0)

        if applex > x and appley == y:
            state.append(1)
        else:
            state.append(0)

        if applex > x and appley < y and (abs(applex - x) == abs(appley -y)):
            state.append(1)
        else:
            state.append(0)

        if applex == x and appley < y:
            state.append(1)
        else:
            state.append(0)

        if applex < x and appley < y and (abs(applex - x) == abs(appley -y)):
            state.append(1)
        else:
            state.append(0)

        if applex < x and appley == y:
            state.append(1)
        else:
            state.append(0)

        #head direction
        if self.head.direction == 'Up':
            state.append(1)
        else:
            state.append(0)
        if self.head.direction == 'Right':
            state.append(1)
        else:
            state.append(0)
        if self.head.direction == 'Down':
            state.append(1)
        else:
            state.append(0)
        if self.head.direction == 'Left':
            state.append(1)
        else:
            state.append(0)
        #head direction
        if self.body[-1].direction == 'Up':
            state.append(1)
        else:
            state.append(0)
        if self.body[-1].direction == 'Right':
            state.append(1)
        else:
            state.append(0)
        if self.body[-1].direction == 'Down':
            state.append(1)
        else:
            state.append(0)
        if self.body[-1].direction == 'Left':
            state.append(1)
        else:
            state.append(0)

        return np.array(state, dtype=int)

    def on_draw(self):
        # Set background color to black
        #self.window.clear()
        for i in self.body: 
            i.draw()
        self.head.draw()
        self.apple.draw()
        self.scoreLabel.text = f'Score: {self.score}'
        self.scoreLabel.draw()
    