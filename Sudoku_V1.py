import pygame as pg
import random
import copy
import time as time

# ------------------------ CONFIG ------------------------ #
WINDOW_SIZE   = (1000, 700)      # Tamanho da janela principal
BOARD_TOPLEFT = (50, 50)         # Coordenadas de início do tabuleiro (canto superior esquerdo)
CELL_SIZE     = 67               # Tamanho de cada célula do tabuleiro
GRID_SIZE     = CELL_SIZE * 9    # Tamanho total da grade (9x9 células)
FPS           = 60               # Taxa de atualização (frames por segundo)

# Tabela de cores
WHITE    = (245, 245, 245)
BLACK    = (30, 30, 30)
GRAY     = (200, 200, 200)
DARKGRAY = (100, 100, 100)
GREEN    = (0, 160, 100)
L_GREEN  = (0, 200, 130)
SKY      = (220, 230, 250)
BLUE     = (80, 130, 255)
RED      = (200, 60, 60)

# -------------------- PYGAME INIT ---------------------- #
pg.init()
window = pg.display.set_mode(WINDOW_SIZE)                    # Cria a janela do jogo
pg.display.set_caption("Sudoku – Maicon Alves e Leonardo Marcondeli")          # Define o título da janela
clock = pg.time.Clock()                                      # Controla a taxa de frames

pg.font.init()
BIG   = pg.font.SysFont("Segoe UI", 48, bold=True)           # Fonte grande para os números
SMALL = pg.font.SysFont("Segoe UI", 28)                      # Fonte pequena para botões e mensagens

# ----------------------- DATA -------------------------- #
EMPTY = "n"  # Valor que representa uma célula vazia

def new_board():
    # Cria um tabuleiro 9x9 vazio
    return [[EMPTY for _ in range(9)] for _ in range(9)]

board         = new_board()      # Estado atual do tabuleiro
input_locked  = False            # Indica se o tabuleiro está bloqueado (ex: após resolver)
message       = ""               # Mensagem a ser exibida ao jogador
msg_color     = GREEN            # Cor da mensagem
selected      = (-1, -1)         # Célula atualmente selecionada

game_phase    = "menu"           # Fase atual do jogo: "menu" ou "play"

# ------------------ SUDOKU HELPERS --------------------- #
def row(b, y): return b[y]                         # Retorna uma linha

def col(b, x): return [b[i][x] for i in range(9)] # Retorna uma coluna

def block(b, x, y):                                # Retorna o bloco 3x3 da célula (x, y)
    bx, by = (x//3)*3, (y//3)*3
    return [b[j][i] for j in range(by, by+3) for i in range(bx, bx+3)]

def valid_number(b, x, y, n):                      # Verifica se n pode ser colocado em (x, y)
    return n not in row(b, y) and n not in col(b, x) and n not in block(b, x, y)

def is_board_consistent(b):                        # Verifica se não há conflitos no tabuleiro
    for y in range(9):
        vals = [v for v in row(b, y) if v != EMPTY]
        if len(vals) != len(set(vals)):
            return False
    for x in range(9):
        vals = [b[y][x] for y in range(9) if b[y][x] != EMPTY]
        if len(vals) != len(set(vals)):
            return False
    for by in range(0, 9, 3):
        for bx in range(0, 9, 3):
            vals = [b[yy][xx] for yy in range(by, by+3) for xx in range(bx, bx+3) if b[yy][xx] != EMPTY]
            if len(vals) != len(set(vals)):
                return False
    return True

def solve_backtracking(b, randomize=False):        # Algoritmo de backtracking para resolver o tabuleiro
    global solve_attempts  # <- necessário para contar corretamente
    for y in range(9):
        for x in range(9):
            if b[y][x] == EMPTY:
                nums = list(range(1, 10))
                if randomize:
                    random.shuffle(nums)
                for n in nums:
                    if valid_number(b, x, y, n):
                        solve_attempts += 1  # <-- conta tentativa
                        b[y][x] = n
                        if solve_backtracking(b, randomize):
                            return True
                        b[y][x] = EMPTY
                return False
    return True

def generate_puzzle(clues=35):                     # Gera um tabuleiro com "clues" pistas
    full = new_board()
    solve_backtracking(full, randomize=True)
    puzzle = copy.deepcopy(full)
    cells = list(range(81))
    random.shuffle(cells)
    for _ in range(81 - clues):
        idx = cells.pop()
        y, x = divmod(idx, 9)
        puzzle[y][x] = EMPTY
    return puzzle

# ----------------------- DRAWERS ----------------------- #
def draw_board(surf):                              # Desenha o tabuleiro e as linhas
    bx, by = BOARD_TOPLEFT
    surf.fill(WHITE)
    pg.draw.rect(surf, DARKGRAY, (bx, by, GRID_SIZE, GRID_SIZE), 4)
    for i in range(1, 3):
        pg.draw.line(surf, DARKGRAY, (bx, by + i*CELL_SIZE*3), (bx + GRID_SIZE, by + i*CELL_SIZE*3), 4)
        pg.draw.line(surf, DARKGRAY, (bx + i*CELL_SIZE*3, by), (bx + i*CELL_SIZE*3, by + GRID_SIZE), 4)
    for i in range(1, 9):
        if i % 3:
            pg.draw.line(surf, GRAY, (bx, by + i*CELL_SIZE), (bx + GRID_SIZE, by + i*CELL_SIZE), 1)
            pg.draw.line(surf, GRAY, (bx + i*CELL_SIZE, by), (bx + i*CELL_SIZE, by + GRID_SIZE), 1)

def draw_numbers(surf):                            # Desenha os números dentro das células
    bx, by = BOARD_TOPLEFT
    for y in range(9):
        for x in range(9):
            val = board[y][x]
            if val != EMPTY:
                img = BIG.render(str(val), True, BLACK)
                img_rect = img.get_rect(center=(bx + x*CELL_SIZE + CELL_SIZE//2, by + y*CELL_SIZE + CELL_SIZE//2))
                surf.blit(img, img_rect)

def highlight_cell(surf, x, y, color):             # Destaca uma célula com uma cor
    bx, by = BOARD_TOPLEFT
    pg.draw.rect(surf, color, (bx + x*CELL_SIZE, by + y*CELL_SIZE, CELL_SIZE, CELL_SIZE), border_radius=4)

def draw_button(surf, rect, text):                 # Desenha um botão com texto centralizado
    mouse = pg.mouse.get_pos()
    hovered = rect.collidepoint(mouse)
    color = L_GREEN if hovered else GREEN
    pg.draw.rect(surf, color, rect, border_radius=12)
    lbl = SMALL.render(text, True, WHITE)
    surf.blit(lbl, (rect.x + (rect.width - lbl.get_width())//2, rect.y + (rect.height - lbl.get_height())//2))

def draw_message(surf):
    if message:
        # Quebra em várias linhas se o texto for muito longo
        lines = []
        words = message.split()
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if SMALL.size(test_line)[0] < 250:  # Limite de largura
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)  # Última linha

        x = 700  # Alinhado com os botões da direita
        y = 270  # Começa abaixo dos botões

        for i, line in enumerate(lines):
            lbl = SMALL.render(line, True, msg_color)
            surf.blit(lbl, (x, y + i * 30))  # 30 px de espaçamento vertical por linha

# ---------- MENU DRAW ---------- #
MENU_RANDOM_RECT = pg.Rect(300, 200, 400, 80)
MENU_CUSTOM_RECT = pg.Rect(300, 320, 400, 80)

def draw_menu(surf):                               # Tela de menu com opções de jogo
    surf.fill(WHITE)
    title = BIG.render("Escolha o modo", True, BLACK)
    surf.blit(title, ((WINDOW_SIZE[0]-title.get_width())//2, 80))
    draw_button(surf, MENU_RANDOM_RECT, "Puzzle Aleatório")
    draw_button(surf, MENU_CUSTOM_RECT, "Montar Manualmente")

# ---------- GAME BUTTONS ---------- #
SOLVE_RECT = pg.Rect(700, 50, 250, 80)
CLEAR_RECT = pg.Rect(700, 150, 250, 80)

# ---------------- MAIN LOOP -------------------------- #
running = True
while running:
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            running = False

        if game_phase == "menu":
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                if MENU_RANDOM_RECT.collidepoint(ev.pos):
                    solve_attempts = 0
                    board = generate_puzzle(clues=35)
                    game_phase = "play"
                    message = ""
                    input_locked = False
                elif MENU_CUSTOM_RECT.collidepoint(ev.pos):
                    board = new_board()
                    game_phase = "play"
                    message = "Insira suas pistas e clique Solve"
                    msg_color = BLACK
                    input_locked = False
            continue

        if game_phase == "play":
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                bx, by = BOARD_TOPLEFT
                if bx <= mx <= bx+GRID_SIZE and by <= my <= by+GRID_SIZE and not input_locked:
                    selected = ((mx-bx)//CELL_SIZE, (my-by)//CELL_SIZE)
                else:
                    selected = (-1, -1)

                if SOLVE_RECT.collidepoint(ev.pos):
                    if is_board_consistent(board):
                        temp = copy.deepcopy(board)
                        start_time = time.time()
                        solve_attempts = 0
                        if solve_backtracking(temp):
                            elapsed = time.time() - start_time
                            board[:] = temp
                            message = f"Resolvido em {elapsed:.5f}s ({solve_attempts} tentativas)"
                            msg_color = GREEN
                            input_locked = True
                        else:
                            message = "Sem solução."
                            msg_color = RED
                    else:
                        message = "Conflitos nas pistas!"
                        msg_color = RED

                if CLEAR_RECT.collidepoint(ev.pos):
                    board = new_board()
                    message = ""
                    input_locked = False

            if ev.type == pg.KEYDOWN and selected != (-1, -1) and not input_locked:
                key = pg.key.name(ev.key)
                sx, sy = selected
                if key in "123456789":
                    board[sy][sx] = int(key)
                elif ev.key in (pg.K_BACKSPACE, pg.K_SPACE):
                    board[sy][sx] = EMPTY

    # ---------------- RENDER ---------------- #
    if game_phase == "menu":
        draw_menu(window)
    else:
        draw_board(window)
        mx, my = pg.mouse.get_pos()
        bx, by = BOARD_TOPLEFT
        if bx <= mx <= bx+GRID_SIZE and by <= my <= by+GRID_SIZE:
            hx, hy = (mx-bx)//CELL_SIZE, (my-by)//CELL_SIZE
            highlight_cell(window, hx, hy, SKY)
        if selected != (-1, -1):
            highlight_cell(window, *selected, BLUE)
        draw_numbers(window)
        draw_button(window, SOLVE_RECT, "Solve / Check")
        draw_button(window, CLEAR_RECT, "Clear Board")
        draw_message(window)

    pg.display.flip()
    clock.tick(FPS)

pg.quit()