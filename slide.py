import math, os
import random
import pygame
from pygame.locals import *

DIR_LEFT, DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_INVALID, DIR_BUTTON =range (6)

GAME_STOPPED, GAME_START, GAME_SCRAMBLE, GAME_ACTIVE, GAME_WIN, GAME_STOP =range (6)
red=(255,0,0)


class s:
    board_siz = [600, 600]

    puzzle_xsiz, puzzle_ysiz = [500, 500]
    puzzle_x, puzzle_y = [
        (board_siz[0] - puzzle_xsiz) /2,
        (board_siz[1] - puzzle_ysiz) /2]
    puzzle_dim = 0
    puzzle_border = 0.1

    power_pos, power_blit_pos, power_siz = [[0, 0], [3, 3], [0, 0]]

    piece_n, piece_xsiz, piece_ysiz = [0, 0, 0]
    piece_pos, spiece_srcrects, piece_dstrects = [[],[],[]]

    grid_dstrects, grid_color, grid_halfsiz = [[], [], 2]

    arrow_dir, arrow_pos, arrow_halfsiz = [0, [0, 0], 0]

    mouse_pos = [0,0]

    game_state, game_level, game_tick, game_scram_speed, game_win_len = [0, 0, 0, 30, 50]

    img_board, img_puzzle, img_arrow, img_power, img_win =[[], [], [], [], []]

    win_imgc, win_imgn, win_imgpos = [0, 5, []]

    surface_puzzle, surface_grid = [[],[]]

    sound_slide_n = 6;
    sound_win, sound_buzz, sound_slide = [[],[],[]]

def calc_piece_dstrects ():
    s.piece_dstrects = []
    for i in range (s.piece_n):
        s.piece_dstrects += [Rect (
            s.puzzle_x +(s.piece_pos[i][0] *s.piece_xsiz),
            s.puzzle_y +(s.piece_pos[i][1] *s.piece_ysiz),
            s.piece_xsiz,
            s.piece_ysiz )]

def set_puzzle_dim (n):
    s.puzzle_dim = n
    s.piece_n = s.puzzle_dim ** 2
    s.piece_xsiz, s.piece_ysiz = [
        s.puzzle_xsiz /s.puzzle_dim,
        s.puzzle_ysiz /s.puzzle_dim]
    s.piece_pos, s.piece_srcrects = [[], []]

    for y in range (s.puzzle_dim):
        for x in range (s.puzzle_dim):
            s.piece_pos += [[x, y]]
            s.piece_srcrects += [Rect (
                x *s.piece_xsiz,
                y *s.piece_ysiz,
                s.piece_xsiz,
                s.piece_ysiz )]

    s.grid_dstrects = []
    for i in range (1, s.puzzle_dim):
        s.grid_dstrects += [Rect (
            s.puzzle_x +(i *s.piece_xsiz) -s.grid_halfsiz,
            s.puzzle_y,
            s.grid_halfsiz *2,
            s.puzzle_ysiz )]
        s.grid_dstrects += [Rect (
            s.puzzle_x,
            s.puzzle_y +(i *s.piece_ysiz) -s.grid_halfsiz,
            s.puzzle_xsiz,
            s.grid_halfsiz *2 )]

    repaint_grid()
    calc_piece_dstrects()
    repaint_puzzle()

def mouse_i_dir ():
    x, y = [s.mouse_pos[0] -s.puzzle_x, s.mouse_pos[1] -s.puzzle_y]
    col, row = [x /s.piece_xsiz, y /s.piece_ysiz]

    try:
        i = s.piece_pos.index ([col,row])
    except:
        return [-1,-1]

    if x < s.puzzle_xsiz *s.puzzle_border:
        dr = DIR_LEFT
    elif y < s.puzzle_ysiz *s.puzzle_border:
        dr = DIR_UP
    elif x > s.puzzle_xsiz *(1.0 -s.puzzle_border):
        dr = DIR_RIGHT
    elif y > s.puzzle_ysiz *(1.0 -s.puzzle_border):
        dr = DIR_DOWN
    else:
        return [-1,-1]

    return i, dr

def in_box (p, b1, b2):
    if p[0] >= b1[0] and p[1] >= b1[1] and p[0] < b2[0] and p[1] < b2[1]:
        return True
    return False

def set_arrow ():
    p = s.mouse_pos
    s.arrow_pos = [p[0] -s.arrow_halfsiz, p[1] -s.arrow_halfsiz]

    if in_box (p, s.power_pos, s.power_siz):
        s.arrow_dir = DIR_BUTTON
        return

    if GAME_ACTIVE is s.game_state:
        i, s.arrow_dir = mouse_i_dir ()
        if i < 0:
            s.arrow_dir = DIR_INVALID

    elif GAME_STOPPED is s.game_state:
        s.arrow_dir = DIR_INVALID

    else:
        s.arrow_dir = DIR_BUTTON

def is_win ():
    i, j = [0, 0]
    for y in range (s.puzzle_dim):
        for x in range (s.puzzle_dim):
            if s.piece_pos[i] == [x, y]:
                j += 1
            i += 1

    if j is i:
        return True
    return False

def win ():
    s.sound_win.play()
    s.game_state = GAME_WIN
    set_arrow ()

def move_piece (col, row, d):
    if DIR_LEFT is d:
        for p in s.piece_pos:
            if p[1] is not row:
                continue
            p[0] -= 1
            if p[0] < 0:
                p[0] = s.puzzle_dim -1

    elif DIR_RIGHT is d:
        for p in s.piece_pos:
            if p[1] is not row:
                continue
            p[0] += 1
            if p[0] >= s.puzzle_dim:
                p[0] = 0

    elif DIR_UP is d:
        for p in s.piece_pos:
            if p[0] is not col:
                continue
            p[1] -= 1
            if p[1] < 0:
                p[1] = s.puzzle_dim -1

    elif DIR_DOWN is d:
        for p in s.piece_pos:
            if p[0] is not col:
                continue
            p[1] += 1
            if p[1] >= s.puzzle_dim:
                p[1] = 0

def slide (col, row, d):
    s.sound_slide[random.randrange (s.sound_slide_n)].play()
    move_piece (col, row, d)
    calc_piece_dstrects()
    repaint_puzzle()

def rnd_slide ():
    d = random.randrange (4);
    col, row = s.piece_pos[random.randrange (s.piece_n)]

    saved_pp = []
    for pp in s.piece_pos:
        saved_pp += [list(pp)]

    move_piece (col, row, d)
    if is_win ():
        if DIR_LEFT is d or DIR_RIGHT is d:
            row += 1
            if row >= s.puzzle_dim:
                row = 0
        else:
            col += 1
            if col >= s.puzzle_dim:
                col = 0


    s.piece_pos = []
    for pp in saved_pp:
        s.piece_pos += [list(pp)]

    slide (col, row, d)

def main ():
    init ()
    pygame.mixer.music.load('Adventures - A Himitsu - SoundCloud (No Copyright Music).mp3')
    pygame.mixer.music.play(-1)
    done = False
    while not done:
        e = pygame.event.poll()
        while e.type != NOEVENT:
            if e.type is QUIT or (e.type is KEYUP and e.key is K_ESCAPE):
                done = True
                break
            elif e.type is MOUSEBUTTONDOWN and e.button is 1:
                onclick (e.pos)
            elif e.type is MOUSEMOTION:
                onmove (e.pos)

            e = pygame.event.poll()
        tick ()

def init ():
    global screen, clock

    random.seed()

    pygame.mixer.pre_init (frequency=48000)
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption ("Photo Puzzle")
    pygame.mouse.set_visible (False)

    flags = pygame.SRCALPHA | pygame.HWACCEL | pygame.HWSURFACE |\
        pygame.ASYNCBLIT

    screen = pygame.display.set_mode (s.board_siz, flags)
    s.surface_puzzle = pygame.Surface (s.board_siz, flags)
    s.surface_grid = pygame.Surface (s.board_siz, flags)

    clock = pygame.time.Clock()

    s.img_board = pygame.image.load( "board.png")
    s.img_puzzle = pygame.image.load( "Animals01.jpg")
    gameIcon = pygame.image.load('download.png')
    pygame.display.set_icon(gameIcon)
    for i in range (6):
        s.img_arrow += [pygame.image.load( "arrow" +str(i) +".png")]

    for i in range (2):
        s.img_power += [pygame.image.load("power" +str(i) +".png")]

    for i in range (5):
        s.img_win += [pygame.image.load("win" +str(i)+".png")]

    s.power_siz = list (s.img_power[0].get_size())
    s.arrow_halfsiz = list (s.img_arrow[0].get_size())[0] /2

    x, y = list (s.img_win[0].get_size())
    s.win_imgpos = [(s.board_siz[0] /2) - (x /2),(s.board_siz[1] /2) - (y /2)]

    s.sound_win = pygame.mixer.Sound("win.ogg")
    s.sound_buzz = pygame.mixer.Sound("buzz.ogg")
    for i in range (s.sound_slide_n):
        s.sound_slide += [
            pygame.mixer.Sound ("sl"+str(i)+".ogg")
        ]
    pygame.draw.rect(screen, red, (550, 450, 100, 50))
    s.game_state = GAME_STOP

    set_arrow ()

def tick ():
    # stabalize fps at 30
    clock.tick (30)

    if GAME_STOPPED is s.game_state:
        pass

    elif GAME_START is s.game_state:
        rnd_slide()
        s.game_tick = 0
        s.game_level = 0
        s.game_state = GAME_SCRAMBLE

    elif GAME_SCRAMBLE is s.game_state:
        s.game_tick += 1
        if not (s.game_tick % s.game_scram_speed):
            if s.game_tick /s.game_scram_speed is s.game_level + 1:
                s.game_tick = 0
                s.game_state = GAME_ACTIVE
                set_arrow ()
            else:
                rnd_slide()

    elif GAME_STOP is s.game_state:
        set_puzzle_dim (2)
        s.game_state = GAME_STOPPED

    elif GAME_WIN is s.game_state:
        s.game_tick += 1
        if not (s.game_tick % s.game_win_len):
            s.game_tick = 0
            s.win_imgc += 1
            if s.win_imgc is s.win_imgn:
                s.win_imgc = 0
            s.game_level += 1
            if s.game_level is s.puzzle_dim:
                set_puzzle_dim (s.puzzle_dim +1)
                s.game_level = 0
            rnd_slide()
            s.game_state = GAME_SCRAMBLE

    repaint ()

def repaint_puzzle ():
    for i in range (s.piece_n):
        s.surface_puzzle.blit (
            s.img_puzzle,
            s.piece_dstrects[i],
            area=s.piece_srcrects[i])

    s.surface_puzzle.blit (s.surface_grid, [0,0])
    s.surface_puzzle.blit (s.img_board, [0,0])

def repaint_grid ():
    s.grid_color = [255, 255, 255, 100]
    s.surface_grid.fill ([0,0,0,0])
    for i in range ((s.puzzle_dim -1) *2):
        s.surface_grid.fill (s.grid_color, s.grid_dstrects[i])

def repaint ():
    screen.blit (s.surface_puzzle, [0,0]);

    if GAME_WIN is s.game_state:
        screen.blit (s.img_win[s.win_imgc], s.win_imgpos)

    if GAME_STOPPED is s.game_state:
        screen.blit (s.img_power[1], s.power_blit_pos)
    else:
        screen.blit (s.img_power[0], s.power_blit_pos)

    screen.blit (s.img_arrow[s.arrow_dir], s.arrow_pos)

    pygame.display.update ()

def onclick (p):
    s.mouse_pos = p

    if in_box (p, s.power_pos, s.power_siz):
        if GAME_STOPPED is s.game_state:
            s.game_state = GAME_START
        else:
            s.game_state = GAME_STOP
        return

    if GAME_ACTIVE is not s.game_state:
        s.sound_buzz.play()
        return

    i, dr = mouse_i_dir ()
    if i < 0:
        s.sound_buzz.play()
        return

    col, row = s.piece_pos[i]
    slide (col, row, dr)
    if is_win():
        win()

def onmove (p):
    s.mouse_pos = p
    set_arrow ()

if __name__ == '__main__':
    main ()

