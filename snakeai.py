import pyglet
import random
import torch
import numpy as np
from collections import deque
from environment import Game
from helper import plot
from agent import Agent

#device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device = torch.device('cpu')

MODE = 'Human'


# games = [Game(10, 1/30), Game(10, 1/30)]
GUISIZE = 400
WINDOWSIZE = 800
NUMBEROFGAMES = 3 #the number of games will be this number squared
DENSITY = 10

SPEED = 1/4

HIGHSCORE = 0

#other

plot_scores = []
plot_mean_scores = []
total_score = 0
total_steps = 0
N_frames = 0
record = 0
agent = Agent()
last_hundred = deque(maxlen=100)
short_mean = []

window = pyglet.window.Window(width=WINDOWSIZE + GUISIZE, height=WINDOWSIZE)

def InitGames(window, Windowsize, density, NoOfGAmes):
    size = Windowsize / NoOfGAmes
    locations = []
    games = []

    for i in range(NoOfGAmes):
        for j in range(NoOfGAmes):
            locations.append((i * size, j * size))

    for loc in locations:
        games.append(Game(window, Windowsize/ NoOfGAmes, loc, density))

    #print(locations, 'locations')
    return games

games = InitGames(window, WINDOWSIZE, DENSITY, 1)


# Create a window with a button

PlayGame = pyglet.shapes.Rectangle(x= 850, y=600, width=300, height=50, color=(255, 255, 255))
TrainAI = pyglet.shapes.Rectangle(x= 850, y=500, width=300, height=50, color=(255, 255, 255))
PlayAI = pyglet.shapes.Rectangle(x= 850, y=400, width=300, height=50, color=(255, 255, 255))

pyglet.font.add_file('retro_computer_personal_use.ttf')
customFont = pyglet.font.load('Retro Computer')

GameLabel = pyglet.text.Label("Snake AI",
                          font_name='Retro Computer',
                          font_size=32,
                          x=850, y = 700, color=(255, 255, 255, 255), bold=True)

PlayGameLabel = pyglet.text.Label("Play Game",
                          font_name='Retro Computer',
                          font_size=20,
                          x=PlayGame.x + 10, y = PlayGame.y + 15, color=(0, 0, 0, 255), bold=True)

TrainAILabel = pyglet.text.Label("Train AI",
                          font_name='Retro Computer',
                          font_size=20,
                          x=TrainAI.x + 10, y = TrainAI.y + 15, color=(0, 0, 0, 255), bold=True)
PlayAILabel = pyglet.text.Label("Play AI",
                          font_name='Retro Computer',
                          font_size=20,
                          x=PlayAI.x + 10, y = PlayAI.y + 15, color=(0, 0, 0, 255), bold=True)

HighScoreLabel = pyglet.text.Label(f'High Score: {HIGHSCORE}',
                          font_name='Retro Computer',
                          font_size=20,
                          x=850, y = 300, color=(255, 255, 255, 255), bold=True)

# Set up the event handler for button clicks
@window.event
def on_mouse_press(x, y, button, modifiers):
    global MODE,SPEED,HIGHSCORE, games, agent
    if button == pyglet.window.mouse.LEFT:
        if (x >= PlayGame.x and x <= PlayGame.x + PlayGame.width) and (y >= PlayGame.y and y <= PlayGame.y + PlayGame.height):
            print('Play Game')
            MODE = "Human"
            HIGHSCORE = 0
            SPEED = 1/4
            games = InitGames(window, WINDOWSIZE, DENSITY, 1)
            pyglet.clock.unschedule(update)
            pyglet.clock.schedule_interval(update, SPEED)
        if (x >= TrainAI.x and x <= TrainAI.x + TrainAI.width) and (y >= TrainAI.y and y <= TrainAI.y + TrainAI.height):
            print('Train Ai')
            MODE = "Training"
            SPEED = 1/30
            HIGHSCORE = 0
            agent = Agent()
            games = InitGames(window, WINDOWSIZE, DENSITY, NUMBEROFGAMES)
            pyglet.clock.unschedule(update)
            pyglet.clock.schedule_interval(update, SPEED)
        if (x >= PlayAI.x and x <= PlayAI.x + PlayAI.width) and (y >= PlayAI.y and y <= PlayAI.y + PlayAI.height):
            print('Play Ai')
            MODE = "AI"
            SPEED = 1/10
            HIGHSCORE = 0
            agent = Agent()
            agent.model.load_model()
            agent.model.eval()
            games = InitGames(window, WINDOWSIZE, DENSITY, 1)
            pyglet.clock.unschedule(update)
            pyglet.clock.schedule_interval(update, SPEED)


@window.event
def on_draw():
    global games, PlayGame
    window.clear()
    PlayGame.draw()
    TrainAI.draw()
    PlayAI.draw()
    GameLabel.draw()
    PlayGameLabel.draw()
    TrainAILabel.draw()
    PlayAILabel.draw()
    HighScoreLabel.text = f'High Score: {HIGHSCORE}'
    HighScoreLabel.draw()

    for game in games:
        game.on_draw()

@window.event
def on_key_press(symbol, modifiers):
    if MODE == "Human":
        game = games[0]
        game.on_key_press(symbol, modifiers)


def update(dt):
    if MODE == 'Human':
        play()
    elif MODE == 'Training':
        train()
    elif MODE == 'AI':
        playAI()

def play():
    global HIGHSCORE
    game = games[0]
    game.moveBody()
    game.head.move()
    done = game.checkCollision()
    game.checkApple()
    
    if done: 
        if game.score > HIGHSCORE:
            HIGHSCORE = game.score
        game.reset()

def playAI():
    global HIGHSCORE
    game = games[0]
    move = agent.get_action_testing(game.get_state())
    reward, done, score = game.play_step(move)
    
    if done:
        if game.score > HIGHSCORE:
            HIGHSCORE = game.score
        game.reset()

def train():

    global plot_scores, plot_mean_scores, total_score, total_steps, record, agent, N_frames, HIGHSCORE
    for game in games:
        state_old = game.get_state()
  
        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = game.get_state()

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)
        
        if done:
            if game.score > HIGHSCORE:
                HIGHSCORE = game.score
            game.reset()
            agent.n_games += 1

            if score > record:
                record = score
                agent.model.save()
                print('Game', agent.n_games, 'Score', score, 'Record:', record, 'Total Steps:', N_frames)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            last_hundred.append(score)
            short_mean.append(sum(last_hundred) / len(last_hundred))
        
        total_steps += 1
        N_frames += 1

    if total_steps > 400: 
        agent.train_long_memory()
        total_steps = 0

        plot(plot_scores, plot_mean_scores, short_mean)

pyglet.clock.schedule_interval(update, SPEED)
pyglet.app.run()

