import pygame, sys
from random import random, randint, choices
import models

WaitOneSec = pygame.USEREVENT + 1

effects_dict = {
    "heal":models.HEAL,
    "recharge":models.RECHARGE,
    "HOT":models.HEALOVERTIME,
    "ROT":models.RECHARGEOVERTIME,
    "damage":models.DAMAGE,
    "elecdamage":models.ELECDAMAGE,
    "poison":models.POISON,
    "flee":models.FLEE,
    "summon":models.SUMMON,
    "self":models.SELF,
    "field":models.FIELD,
    "enemies":models.ENEMIES,
    "delay1":models.DELAY1,
    "ondeath":models.ONDEATH,
    "afterbattle":models.AFTERBATTLE
}

colours = {
    'RED':(255,0,0),
    'YELLOW':(255,255,0),
    'GREEN':(0,255,0),
    'BLEEN':(0,255,255),
    'BLUE':(0,0,255),
    'PURPLE':(255,0,255)
}

def GetItem(itemID):
    if itemID[0] == 'I':
        with open("text/items.txt", 'r') as file:
            for item in file:
                item = item.strip().split('|')
                if item[0] == itemID:
                    effects = []
                    for effect in item[3:]:
                        effect = effect.split(',')
                        new_effect = []
                        for x in effect:
                            if x in effects_dict.keys():
                                new_effect.append(effects_dict[x])
                            else:
                                new_effect.append(x)
                        effects.append(new_effect)
                    return models.Item(Name = item[1], effects = effects, desc = item[2])
                    

    elif itemID[0] == 'T':
        with open("text/tools.txt", 'r') as file:
            for tool in file:
                tool = tool.strip().split('|')
                if tool[0] == itemID:
                    effects = []
                    for effect in tool[5:]:
                        effect = effect.split(',')
                        new_effect = []
                        for x in effect:
                            if x in effects_dict.keys():
                                new_effect.append(effects_dict[x])
                            else:
                                new_effect.append(x)
                        effects.append(new_effect)
                    return models.Tool(Name = tool[1], cost = int(tool[2]), cooldown = int(tool[3]), effects = effects, desc = tool[4])
    else:
        return None

def GetThreat(enemyID):
    with open("text/enemies.txt", 'r') as file:
        for enemy in file:
            if enemy[0] == '#':
                continue
            enemy = enemy.strip().split('|')
            if enemy[0] == enemyID:
                return int(enemy[3])

def GetEnemy(enemyID):
    with open("text/enemies.txt", 'r') as file:
        for enemy in file:
            if enemy[0] == '#':
                continue
            enemy, lootpool = enemy.strip().split('$')
            enemy = enemy.split('|')
            if enemy[0] == enemyID:
                Name, species, img, desc = enemy[1].strip(), enemy[2], enemy[10], enemy[11]
                stats = []
                for i in range(4,10):
                    if '~' in enemy[i]:
                        lo, hi = enemy[i].split('~')
                        stats.append(randint(int(lo), int(hi)))
                    else:
                        stats.append(int(enemy[i]))

                if len(enemy) > 12:
                    items = []
                    for thing in enemy[12:]:
                        if thing:
                            itemID, probability = thing.split(',')
                            if randint(1,100) <= int(probability):
                                items.append(GetItem(itemID))
                        

                lootpool = lootpool.split('|')
                loot = []
                for thing in lootpool:
                    itemID, probability = thing.split(',')
                    if randint(1,100) <= int(probability):
                        loot.append(GetItem(itemID))

                Enemy = models.Enemy(Name = Name, hp = stats[0], ep = stats[1], df = stats[2], atk = stats[3], lk = stats[4], desc = desc, xp = stats[5], loot = loot, species = species, img = img)

                for item in items:
                    if item.type == models.ITEM:
                        Enemy.GainItem(item)
                    elif item.type == models.TOOL:
                        Enemy.GainTool(item)

                return Enemy


                

def SetUpBattle(SceneID, threat):
    '''returns img, rgb colour, list of enemy objects'''
    with open("text/scenes.txt", 'r') as file:
        for scene in [x for x in file if x[0] != '#']:
            filler = None
            if '+' in scene:
                scene, filler = scene.strip().split('+')
                filler = filler.strip().split('|')
            scene = scene.strip().split('|')
            if scene[0].lower() == SceneID.lower():
                Name, colour, img, desc = scene[1], colours[scene[2]], scene[3], scene[4]
                enemiesID = scene[5:]
                enemies = []

                if filler: #add default enemies, then fill the rest with the filler
                    for enemyID in enemiesID:
                        enemies.append(GetEnemy(enemyID))
                        threat -= GetThreat(enemyID)

                    #add supports
                    weights = []
                    for enemyID in filler:
                        weights.append(GetThreat(enemyID))
                    while threat > 0.9 and len(enemies) < 5:
                        choice = choices(filler, weights)[0]
                        enemy_threat = GetThreat(choice)
                        if enemy_threat <= threat:
                            enemies.append(GetEnemy(choice))
                            threat -= enemy_threat

                else: #rolls enemies
                    weights = []
                    for enemyID in enemiesID:
                        weights.append(GetThreat(enemyID))
                    while threat > 0.9 and len(enemies) < 5:
                        choice = choices(enemiesID, weights)[0]
                        enemy_threat = GetThreat(choice)
                        if enemy_threat <= threat:
                            enemies.append(GetEnemy(choice))
                            threat -= enemy_threat

    return Name, colour, img, desc, enemies

def StartBattle(title, img, bg_colour, player, enemies):
    '''Starts a Battle.
    title should be title, img should be bg img, player should be entity object, enemies should be list of entity objects
    Returns True if match won, False if match lost'''

    announcements = ["It's your turn."]

    #initialise pygame
    pygame.init()
    WIDTH, HEIGHT = 1440, 810
    FPS, VOLUME = 60, 1
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Courier New", 20, bold = True)
    header_font = pygame.font.SysFont("Courier New", 24, bold = True)

    ### set up scene (backgrounds, sounds)
    pygame.display.set_caption(title)
    bg_img = pygame.image.load(img).convert_alpha()
    bg_img = pygame.transform.scale(bg_img, screen.get_rect().size)
    screen.blit(bg_img, (0,0))
    pygame.mixer.init()
    if title.strip() == "Street":
        pygame.mixer.music.load("audio/fight.wav")
    elif title.strip() == "Zouquee GoGo":
        pygame.mixer.music.load("audio/club.wav")
    elif title.strip() == "Riverboat":
        pygame.mixer.music.load("audio/chill.wav")
    pygame.mixer.music.set_volume(VOLUME)
    pygame.mixer.music.play(-1)

    #set up UI
    info_surf = pygame.Surface((300, 200), pygame.SRCALPHA)
    info_surf.fill((0, 0, 0, 200))
    text_surf = pygame.Surface((int(WIDTH*0.9), int(HEIGHT*0.3)), pygame.SRCALPHA) #SRCALPHA enables per-pixel alpha, allowing each pixel to have its own alpha value
    text_surf.fill((0,0,0,100))
    bottom_surf = pygame.Surface((int(WIDTH), 50), pygame.SRCALPHA)
    bottom_surf.fill((0,0,0,255))
    
    screen.blit(text_surf, (WIDTH*0.05, HEIGHT*0.65))

    #set up enemies and hitboxes
    HITBOXPOS = [(60,60), (340,160), (620,60), (900,160), (1180,60)]
    enemypos = [None, None, None, None, None]
    for i in range(len(enemies)):
        pos = randint(0, len(enemypos)-1)
        while enemypos[pos] != None:
            pos = randint(0, len(enemypos)-1)
        enemypos[pos] = enemies[i].Name
        enemies[i] = [pos, pygame.Rect(HITBOXPOS[pos][0], HITBOXPOS[pos][1], 200, 200), enemies[i]]
        
    #set up turn order (player has an id of 0, rest are the enemy's positions
    turnOrder = [-1] + [enemies[i][0] for i in range(len(enemies))]

    #battle loop
    isBattling = True
    battleMode = 0 #0 = player's turn/player defending, 1 = player attacking, 2 = player using item, 3 = enemy attacking, 4 = player using tool
    selectedItem = 0
    while isBattling:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass #don't let player quit out of battle

            elif event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_1: #if key 1 pressed:
                    if battleMode == 1:
                        battleMode = 0
                        announcements.append("Attack deselected.")
                    elif battleMode != 3: #don't let player select modes while enemies are fighting
                        battleMode = 1
                        announcements.append("Attack selected. Click on an enemy to attack.") 

                elif event.key == pygame.K_2: #if key 2 pressed:
                    if battleMode != 3:
                        announcements.append(f"You brace yourself for attacks. Defence increased by {player.Defend()} for this turn.")
                        battleMode = 3
                        turnOrder.append(turnOrder.pop(0))

                elif event.key == pygame.K_3: #if key 3 pressed:
                    if battleMode == 2:
                        selectedItem += 1
                        if selectedItem > len(player.inv):
                            selectedItem = 0
                    elif battleMode != 3:
                        battleMode = 2
                        selectedItem = 0
                elif event.key == pygame.K_4: #if key 4 pressed:
                    if battleMode == 4:
                        selectedItem += 1
                        if selectedItem > len(player.tools):
                            selectedItem = 0
                    elif battleMode != 3:
                        battleMode = 4
                        selectedItem = 0
                    
            elif event.type == pygame.MOUSEBUTTONDOWN: #if screen clicked
                if battleMode == 2: #select and use Item
                    if selectedItem == 0:
                        battleMode = 0
                    else:
                        itemName = player.GetInventory()[selectedItem-1][0]
                        item = player.RemoveItem(itemName)
                        isUsedOnEnemy = False
                        for enemy in enemies: #check if item was used on an enemy
                            if enemy[1].collidepoint(event.pos):
                                isUsedOnEnemy = True
                                output = item.UseItem(enemy[2])
                        if not isUsedOnEnemy:
                            output = item.UseItem(player)
                        for line in output.split('\n'):
                            if line:
                                announcements.append(line)
                        battleMode = 3
                        turnOrder.append(turnOrder.pop(0))

                elif battleMode == 4: #select and use Tool
                    if selectedItem == 0:
                        battleMode = 0
                    else:
                        toolName = player.GetTools()[selectedItem-1][0]
                        tool = player.UseTool(toolName)
                        if tool == False:
                            announcements.append(f"You cannot use {toolName}. Check your EP and your tool's cooldown.")
                            battleMode = 0
                        else:
                            isUsedOnEnemy = False
                            for enemy in enemies: #check if item was used on an enemy
                                if enemy[1].collidepoint(event.pos):
                                    isUsedOnEnemy = True
                                    output = tool.UseTool(player, enemy[2], enemies)
                            if not isUsedOnEnemy:
                                output = tool.UseTool(player, player, enemies)
                            for line in output.split('\n'):
                                if line:
                                    announcements.append(line)
                            battleMode = 0
                            announcements.append("It's still your turn.")
                        
                elif battleMode == 3: #progress enemy text
                    next_enemy = turnOrder.pop(0)
                    turnOrder.append(next_enemy)
                    for enemy in enemies:
                        if enemy[0] == next_enemy:
                            next_enemy = enemy[2]
                            break

                    output = next_enemy.DoTurn(player, enemies)
                    if type(output[-1]) == type(""):
                        announcements.extend(output[-1].strip().split('\n'))
                    if type(output[0]) == type((0,0)):
                        hasCrit, rawDamage = output[0]
                        announcements.append(f"{next_enemy.Name} attacks for {rawDamage} damage.{' Critical Hit!' if hasCrit else ''}")
                        recv_damage = player.RecvDamage(rawDamage)
                        if recv_damage == False:
                            announcements.append(f"You dodged the attack!")
                        else:
                            announcements.append(f"You took {recv_damage} damage from {next_enemy.Name}.")
                        
                    if turnOrder[0] == -1:
                        battleMode = 0
                        player.GameTick()
                        for enemy in enemies:
                            enemy[2].GameTick()
                        announcements.append(f"It's your turn. What will you do?")

                else:
                    for enemy in enemies:
                        if enemy[1].collidepoint(event.pos):
                            if battleMode == 1:
                                hasCrit, rawDamage = player.DealDamage()
                                announcements.append(f"You strike at {enemy[2].Name}, attacking for {rawDamage} damage.{' Critical Hit!' if hasCrit else ''}")
                                recv_damage = enemy[2].RecvDamage(rawDamage)
                                if recv_damage == False:
                                    announcements.append(f"The {enemy[2].Name} dodged the attack!")
                                else:
                                    announcements.append(f"The {enemy[2].Name} took {recv_damage} damage.")
                                battleMode = 3
                                turnOrder.append(turnOrder.pop(0))
                            else: #inspect enemy
                                desc = enemy[2].desc.split(r'\n')
                                for line in desc:
                                    announcements.append(line)
                                pass

        #check if enemies are dead
        for enemy in enemies:
            if enemy[2].IsDead():
                announcements.append(f"{enemy[2].Name} died!")
                xp, loot = enemy[2].dropLoot()
                announcements.append(f"{enemy[2].Name} dropped {xp} xp! {'Level Up!' if player.gainXP(xp) else ''}")
                if loot: #handle loot collection
                    for item in loot:
                        announcements.append(f"{enemy[2].Name} dropped {item.Name}!")
                        if item.type == models.TOOL:
                            player.GainTool(item)
                        elif item.type == models.ITEM:
                            player.GainItem(item)
                turnOrder.remove(enemy[0])
                enemies.remove(enemy)

        #check if player has won or lost
        if player.IsDead():
            announcements.append(f"You died!!")
        elif len(enemies) == 0:
            announcements.append(f"You won!!")

        #draw in the order bg > enemy > tint > text > bottomline > infotext
        screen.blit(bg_img, (0,0))
        for enemy in enemies:
            if enemy[2].img:
                enemy_img = pygame.image.load(enemy[2].img).convert_alpha()
                enemy_img = pygame.transform.scale(enemy_img, enemy[1].size)
                screen.blit(enemy_img, enemy[1])  
                
            else:
                pygame.draw.rect(screen, (255, 0, 0), enemy[1])

        #tint screen
        tint_surf = screen.copy()
        tint_surf.fill(bg_colour)
        tint_surf.set_alpha(64)
        screen.blit(tint_surf, (0,0))


        text_surf.fill((0,0,0,100))

        if battleMode == 2: #print inventory
            text_render = header_font.render("INVENTORY (CLICK ON ENEMY TO USE ON ENEMY, CLICK ANYWHERE ELSE TO USE ON SELF)", True, (255,220,100) if selectedItem == 0 else (255,255,255))
            text_surf.blit(text_render, (10, 10))
            inv = player.GetInventory()
            for i in range(len(inv)):
                text_render = font.render(f"{inv[i][0]:<25}{inv[i][1]:<5}{inv[i][2]}", True, (255,255,255) if i != (selectedItem-1) else (255,220,100))
                text_surf.blit(text_render, (12, 40+(25*i)))
        elif battleMode == 4: #print tools
            text_render = header_font.render("TOOLS (CLICK ON ENEMY TO USE ON ENEMY, CLICK ANYWHERE ELSE TO USE ON SELF)", True, (255,220,100) if selectedItem == 0 else (255,255,255))
            text_surf.blit(text_render, (10, 10))
            tools = player.GetTools()
            for i in range(len(tools)):
                text_render = font.render(f"{tools[i][0]:<20}Cost:{str(tools[i][1])+'EP':<5}{'READY   ' if tools[i][2] else 'COOLDOWN'}  {tools[i][3]}", True, (255,255,255) if i != (selectedItem-1) else (255,220,100))
                text_surf.blit(text_render, (12, 40+(25*i)))
        else:
            for i in range(1,10):
                text_render = font.render("" if len(announcements) < i else announcements[-i], True, (255,255,255))
                text_surf.blit(text_render, (10, int(HEIGHT*0.3)-5-(25*i)))
        screen.blit(text_surf, (WIDTH*0.05, HEIGHT*0.70-60))

        #bottom bar
        bottom_surf.fill((0,0,0,255))
        HP, MaxHP, EP, MaxEP, DF, TempDF, ATK, TempATK, LVL, XP, XP_REQ, effects = player.GetStats()
        bottom_render = header_font.render(f"HP:{f'{HP}/{MaxHP}':<8}EP:{f'{EP}/{MaxEP}':<8}DF:{f'{DF}' if TempDF == 0 else f'{DF} + {TempDF}':<8}ATK:{f'{ATK}' if TempATK == 0 else f'{ATK} + {TempATK}':<8}LVL:{LVL:<6}XP:{f'{XP}/{XP_REQ}':<8}{f'{effects}' if effects else ''}", True, (255, 255, 255))
        bottom_surf.blit(bottom_render, (10, 10))
        screen.blit(bottom_surf, (0, HEIGHT-50))

        mousepos = pygame.mouse.get_pos()
        for enemy in enemies:
            if enemy[1].collidepoint(mousepos):
                info_surf.fill((0, 0, 0, 200))
                info_header_render = header_font.render(enemy[2].Name, True, (255, 220, 100))
                info_surf.blit(info_header_render, (10, 10))
                lines = enemy[2].GetInfoText().split('\n')
                for i in range(len(lines)):
                    info_render = font.render(lines[i], True, (255, 255, 255))
                    info_surf.blit(info_render, (10, 45+(i*30)))
                screen.blit(info_surf, mousepos)

        pygame.display.flip()
        clock.tick(FPS)

        #leave text on screen for 2 seconds, then quit the battle
        if player.IsDead():
            pygame.time.delay(2000)
            pygame.quit()
            return False
        elif len(enemies) == 0:
            player.effects = []
            player.GameTick()
            pygame.time.delay(2000)
            pygame.quit()
            return True

    pygame.quit()
