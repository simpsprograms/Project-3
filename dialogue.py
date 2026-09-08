import pygame, sys

story_values = {}

def performResult(text):
    if '=' in text:
        text = text.strip().split('=')
        story_values[text[0]] = text[1]

def checkCondition(text):
    '''Evaluates whether the condition is true or false'''
    text = text.strip('\n').strip('?')
    if 'True' in text:
        return True
    if '=' in text:
        text = text.strip().split('=')
        if not text[0] in story_values.keys():
            return False
        return story_values[text[0]] == text[1]


def dispStory(story_path):
    #initialise pygame
    pygame.init()
    WIDTH, HEIGHT = 1440, 810
    FPS, SCROLLSPEED, VOLUME = 60, 2, 1
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Project 3")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Courier New", 24, bold = True)
    header_font = pygame.font.SysFont("Courier New", 28, bold = True)

    #dialogue box setup
    box_width, box_height = int(WIDTH*0.9), int(HEIGHT*0.3)
    text_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA) #SRCALPHA enables per-pixel alpha, allowing each pixel to have its own alpha value
    text_surf.fill((0,0,0,200))

    #speaker img setup
    speaker_rect = pygame.Rect(WIDTH*0.1, HEIGHT*0.15, HEIGHT*0.5, HEIGHT*0.5) 

    #options setup
    option_width, option_height = int(WIDTH*0.3), int(HEIGHT*0.3)
    option1_surf = pygame.Surface((option_width, option_height), pygame.SRCALPHA)
    option1_surf.fill((0,0,0,200))
    option1_rect = option1_surf.get_rect()
    option1_rect.topleft = (int(WIDTH*0.025), int(HEIGHT*0.1))

    option2_surf = pygame.Surface((option_width, option_height), pygame.SRCALPHA)
    option2_surf.fill((0,0,0,200))
    option2_rect = option2_surf.get_rect()
    option2_rect.topleft = (int(WIDTH*0.35), int(HEIGHT*0.1))

    option3_surf = pygame.Surface((option_width, option_height), pygame.SRCALPHA)
    option3_surf.fill((0,0,0,200))
    option3_rect = option3_surf.get_rect()
    option3_rect.topleft = (int(WIDTH*0.675), int(HEIGHT*0.1))

    options = [
        (option1_surf, option1_rect),
        (option2_surf, option2_rect),
        (option3_surf, option3_rect)
    ]

    story = []
    with open(story_path, 'r') as file:
        story = file.readlines()

    bgimg, bg_music = story.pop(0).strip().split('|')
    if bgimg:
        bg_img = pygame.image.load(bgimg).convert_alpha()
        bg_img = pygame.transform.scale(bg_img, screen.get_rect().size)
        screen.blit(bg_img, (0,0))
    if bg_music:
        pygame.mixer.init()
        pygame.mixer.music.load(bg_music)
        pygame.mixer.music.set_volume(VOLUME)
        pygame.mixer.music.play(-1)

    start_time = pygame.time.get_ticks()
    output = []
    speaker_img = None
    isRunning = True
    while isRunning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass #don't let player quit out of dialogue

            elif event.type == pygame.MOUSEBUTTONDOWN: #mouse button clicked
                if len(story) != 0:
                    if story[0][0] == '$':
                        start_time = 0
                        for option, result in options_available:
                            if options[option][1].collidepoint(event.pos):
                                performResult(result)
                                story.pop(0)
                                options_available = []
                                break
                    else:
                        if text_progress != 1:
                            start_time = 0
                        else:
                            story.pop(0)
                            start_time = pygame.time.get_ticks()
                while len(story) != 0 and story[0][0] == '#': #skip comments
                    story.pop(0)

        #display text
        if len(story) == 0:
            isRunning = False
        else:
            if story[0][0] == '$':
                if options_available:
                    pass
                else:
                    start_time = pygame.time.get_ticks()
                    options_available = []
                    line = story[0]
                    line = line.strip('\n').strip('$')
                    img, header, text = line.strip().split('|')
                    while story[1][0].isnumeric():
                        line = story.pop(1)
                        option, option_text, result = line.split('|')
                        options_available.append([int(option)-1,result])
                        option_surf = options[int(option)-1][0]
                        text_render = font.render(option_text, True, (255,255,255))
                        text_rect = text_render.get_rect(center=option_surf.get_rect().center) #centre text to surface
                        option_surf.fill((0,0,0,220))
                        option_surf.blit(text_render, text_rect)
            
            elif story[0][0] == '?':
                condition = checkCondition(story.pop(0))
                if condition:
                    continue
                else:
                    while len(story) != 0 and story[0][0] != '?': #ignores text until it reaches another ?
                        story.pop(0)
            elif story[0][0] == '>':
                commands = story[0].strip().strip('>').split('>')
                for command in commands:
                    mode, value = command.split('|')
                    output.append([mode,value])
                isRunning = False
            else:
                options_available = []
                elapsed_timems = pygame.time.get_ticks() - start_time
                text_progress = min(1, elapsed_timems/1000*SCROLLSPEED)
                img, header, text = story[0].strip().split('|')
                if img:
                    if img.strip() == "None":
                        speaker_img = None
                    else:
                        speaker_img = pygame.image.load(img).convert_alpha()
                        speaker_img = pygame.transform.scale(speaker_img, speaker_rect.size)

            header_render = header_font.render(header, True, (255, 220, 100))
            text_render = font.render(text[:int(len(text)*text_progress)], True, (255, 255, 255))

            # Blit onto dialogue surface
            text_surf.fill((0,0,0,200))
            text_surf.blit(header_render, (20, 15))
            text_surf.blit(text_render, (20, 55))

        screen.fill((64, 64, 64))
        if bgimg:
            screen.blit(bg_img, (0,0))
        if speaker_img:
            screen.blit(speaker_img, speaker_rect) 
        screen.blit(text_surf, (WIDTH*0.05, HEIGHT*0.65))

        if options_available:
            for option, result in options_available:
                screen.blit(options[option][0], options[option][1])

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    return output
