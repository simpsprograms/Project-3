import pygame, sys
from random import random
import battle
import models
import dialogue
import puzzlebox

#initialise pygame
pygame.init()
WIDTH, HEIGHT = 1440, 810
FPS,VOLUME = 60,1
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Project 3")
clock = pygame.time.Clock()

menu_font = pygame.font.SysFont("Courier_New", 48, bold = True)

#initialise music
pygame.mixer.init()
pygame.mixer.music.load("audio/chill.wav")
pygame.mixer.music.set_volume(VOLUME)
pygame.mixer.music.play(-1)

#menu buttons setup
play_surf = pygame.Surface((int(WIDTH*0.5), int(HEIGHT*0.1)), pygame.SRCALPHA)
play_surf.fill((0, 0, 0, 200))
play_render = menu_font.render("PLAY", True, (255,255,255))
text_rect = play_render.get_rect(center=play_surf.get_rect().center) #centre text to surface
play_surf.blit(play_render, text_rect)
play_rect = play_surf.get_rect()
play_rect.topleft = (int(WIDTH*0.25), int(HEIGHT*0.5))

settings_surf = pygame.Surface((int(WIDTH*0.5), int(HEIGHT*0.1)), pygame.SRCALPHA)
settings_surf.fill((0, 0, 0, 200))
settings_render = menu_font.render("SETTINGS", True, (255,255,255))
text_rect = settings_render.get_rect(center=settings_surf.get_rect().center)
settings_surf.blit(settings_render, text_rect)
settings_rect = settings_surf.get_rect()
settings_rect.topleft = (int(WIDTH*0.25), int(HEIGHT*0.65))

exit_surf = pygame.Surface((int(WIDTH*0.5), int(HEIGHT*0.1)), pygame.SRCALPHA)
exit_surf.fill((0, 0, 0, 200))
exit_render = menu_font.render("EXIT", True, (255,255,255))
text_rect = exit_render.get_rect(center=exit_surf.get_rect().center)
exit_surf.blit(exit_render, text_rect)
exit_rect = exit_surf.get_rect()
exit_rect.topleft = (int(WIDTH*0.25), int(HEIGHT*0.8))

screen.fill((64,64,64))
screen.blit(play_surf, (int(WIDTH*0.25), int(HEIGHT*0.5)))
screen.blit(settings_surf, (int(WIDTH*0.25), int(HEIGHT*0.65)))
screen.blit(exit_surf, (int(WIDTH*0.25), int(HEIGHT*0.8)))

pygame.display.flip()

#main menu loop
isMenu, isPlaying = True, False
while isMenu:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isMenu = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_rect.collidepoint(event.pos):
                isMenu, isPlaying = False, True
            elif settings_rect.collidepoint(event.pos):
                pass
            elif exit_rect.collidepoint(event.pos):
                isMenu = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

#game loop
#check for previous progress
try:
    with open('text/saves.txt', 'r') as file:
        lines = file.readlines()
        if len(lines) > 0 and lines[0].isnumeric:
            respawns = int(lines[0])
        else:
            respawns = 0
except Exception as e:
    respawns = 0


while isPlaying:
    Player = models.Player(Name = "Player", hp = 40, ep = 10, df = 2, atk = 10, lk = 5)
    Player.GainItem(battle.GetItem("I02"), 5)
    Player.GainItem(battle.GetItem("I04"), 5)
    Player.GainItem(battle.GetItem("I05"), 5)

    Player.GainTool(battle.GetItem("T09"))
    Player.GainTool(battle.GetItem("T04"))
    Player.GainTool(battle.GetItem("T06"))
    Player.GainTool(battle.GetItem("T13"))
    Player.GainTool(battle.GetItem("T15"))
    
    isAlive = True
    commands = [['D', 'video1.txt']]
    threat = 7
    
    while isAlive:
        if len(commands) == 0:
            print("commands empty")
            isAlive = False
        else:
            next_command = commands.pop(0)
            if next_command[0] == 'D':
                commands.extend(dialogue.dispStory('text/story/' + next_command[1]))
            elif next_command[0] == 'B':
                Name, colour, img, desc, enemies = battle.SetUpBattle(next_command[1], threat)       
                isAlive = battle.StartBattle(Name, img, colour, Player, enemies)
                threat += 1.5
            elif next_command[0] == 'M':
                puzzlebox.puzzlebox()
            else:
                print("Invalid command")
                isPlaying, isAlive = False, False

    respawns += 1

    result = dialogue.dispStory('text/story/badendscreen.txt')
    if result[0][0] == 'Y':
        print("player continues")
        continue
    
    elif result[0][0] == 'N':
        with open('text/saves.txt', 'w') as file:
            file.write(str(respawns))
        isPlaying = False

pygame.quit()
sys.exit()
