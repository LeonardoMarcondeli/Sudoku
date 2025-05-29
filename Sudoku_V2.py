import pygame as pg
import random
import copy
import time as time

# ========================================================
#               CONFIGURAÇÕES GERAIS / CORES
# ========================================================
WINDOW_SIZE = (1000, 700)    # Janela fixa
FPS         = 60

WHITE    = (245, 245, 245)
BLACK    = ( 30,  30,  30)
GRAY     = (200, 200, 200)
DARKGRAY = (100, 100, 100)
GREEN    = (  0, 160, 100)
L_GREEN  = (  0, 200, 130)
SKY      = (220, 230, 250)
BLUE     = ( 80, 130, 255)
RED      = (200,  60,  60)

EMPTY = "n"                  # Sentinela para célula vazia

# ========================================================
#           TAMANHOS DISPONÍVEIS E FUNÇÃO configure()
# ========================================================
SIZE_OPTIONS = [9, 12, 18]   # Outras dimensões? basta adicionar aqui
size_idx     = 0             # Índice selecionado no menu

def configure(sz: int):
    """Ajusta variáveis globais de acordo com o tamanho do tabuleiro."""
    global SIZE, BOX_ROWS, BOX_COLS
    global CELL_SIZE, GRID_SIZE, BOARD_TOPLEFT
    global BIG, SMALL

    SIZE       = sz
    BOX_ROWS   = 3                   # Linhas por bloco fixo
    BOX_COLS   = SIZE // BOX_ROWS    # Colunas por bloco (3×3, 3×4, 3×6…)

    # Calcula CELL_SIZE para caber na janela
    CELL_SIZE  = min((WINDOW_SIZE[0] - 300) // SIZE,
                     (WINDOW_SIZE[1] - 100) // SIZE)
    GRID_SIZE  = CELL_SIZE * SIZE
    BOARD_TOPLEFT = (50, 50)         # canto sup-esq. do tabuleiro

    # Fontes dimensionadas ao novo CELL_SIZE
    BIG   = pg.font.SysFont("Segoe UI",
                            max(18, int(CELL_SIZE * 0.8)),
                            bold=True)
    SMALL = pg.font.SysFont("Segoe UI", 28)

# ========================================================
#              INICIALIZA PYGAME (ANTES de configure)
# ========================================================
pg.init()
pg.font.init()                # ← agora o módulo de fontes está pronto
configure(SIZE_OPTIONS[size_idx])

# ========================================================
#           FUNÇÕES DE TABULEIRO E LÓGICA SUDOKU
# ========================================================
def new_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def row(b, y): return b[y]
def col(b, x): return [b[i][x] for i in range(SIZE)]

def block(b, x, y):
    bx = (x // BOX_COLS) * BOX_COLS
    by = (y // BOX_ROWS) * BOX_ROWS
    return [b[j][i]
            for j in range(by, by + BOX_ROWS)
            for i in range(bx, bx + BOX_COLS)]

def valid_number(b, x, y, n):
    return (n not in row(b, y) and
            n not in col(b, x) and
            n not in block(b, x, y))

def is_board_consistent(b):
    for y in range(SIZE):
        vals = [v for v in b[y] if v != EMPTY]
        if len(vals) != len(set(vals)):
            return False
    for x in range(SIZE):
        vals = [b[y][x] for y in range(SIZE) if b[y][x] != EMPTY]
        if len(vals) != len(set(vals)):
            return False
    for by in range(0, SIZE, BOX_ROWS):
        for bx in range(0, SIZE, BOX_COLS):
            vals = [b[yy][xx]
                    for yy in range(by, by + BOX_ROWS)
                    for xx in range(bx, bx + BOX_COLS)
                    if b[yy][xx] != EMPTY]
            if len(vals) != len(set(vals)):
                return False
    return True

def solve_backtracking(b, randomize=False):
    global solve_attempts
    for y in range(SIZE):
        for x in range(SIZE):
            if b[y][x] == EMPTY:
                nums = list(range(1, SIZE + 1))
                if randomize:
                    random.shuffle(nums)
                for n in nums:
                    if valid_number(b, x, y, n):
                        solve_attempts += 1
                        b[y][x] = n
                        if solve_backtracking(b, randomize):
                            return True
                        b[y][x] = EMPTY
                return False
    return True

def generate_puzzle(clue_ratio=0.45):
    full = new_board()
    solve_backtracking(full, randomize=True)
    puzzle = copy.deepcopy(full)

    total    = SIZE * SIZE
    clues    = int(total * clue_ratio)
    to_blank = total - clues

    cells = list(range(total))
    random.shuffle(cells)
    for _ in range(to_blank):
        idx = cells.pop()
        y, x = divmod(idx, SIZE)
        puzzle[y][x] = EMPTY
    return puzzle

# ========================================================
#                    FUNÇÕES DE DESENHO
# ========================================================
def draw_board(surf):
    bx, by = BOARD_TOPLEFT
    surf.fill(WHITE)

    # Moldura externa
    pg.draw.rect(surf, DARKGRAY, (bx, by, GRID_SIZE, GRID_SIZE), 4)

    # Linhas horizontais / verticais
    for i in range(1, SIZE):
        # Horizontal
        y = by + i * CELL_SIZE
        color_h = DARKGRAY if i % BOX_ROWS == 0 else GRAY
        width_h = 4 if i % BOX_ROWS == 0 else 1
        pg.draw.line(surf, color_h, (bx, y), (bx + GRID_SIZE, y), width_h)
        # Vertical
        x = bx + i * CELL_SIZE
        color_v = DARKGRAY if i % BOX_COLS == 0 else GRAY
        width_v = 4 if i % BOX_COLS == 0 else 1
        pg.draw.line(surf, color_v, (x, by), (x, by + GRID_SIZE), width_v)

def draw_numbers(surf, board):
    bx, by = BOARD_TOPLEFT
    for y in range(SIZE):
        for x in range(SIZE):
            val = board[y][x]
            if val != EMPTY:
                img = BIG.render(str(val), True, BLACK)
                surf.blit(img, img.get_rect(
                    center=(bx + x*CELL_SIZE + CELL_SIZE//2,
                            by + y*CELL_SIZE + CELL_SIZE//2)))

def highlight_cell(surf, x, y, color):
    bx, by = BOARD_TOPLEFT
    pg.draw.rect(
        surf, color,
        (bx + x*CELL_SIZE, by + y*CELL_SIZE, CELL_SIZE, CELL_SIZE),
        border_radius=4
    )

def draw_button(surf, rect, text):
    hovered = rect.collidepoint(pg.mouse.get_pos())
    color   = L_GREEN if hovered else GREEN
    pg.draw.rect(surf, color, rect, border_radius=12)
    lbl = SMALL.render(text, True, WHITE)
    surf.blit(lbl, (rect.x + (rect.width  - lbl.get_width())  // 2,
                    rect.y + (rect.height - lbl.get_height()) // 2))

def draw_message(surf, message, msg_color):
    if not message:
        return
    words, lines, cur = message.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if SMALL.size(test)[0] < 260:
            cur = test
        else:
            lines.append(cur); cur = w
    lines.append(cur)

    x, y0 = 700, 270
    for i, line in enumerate(lines):
        surf.blit(SMALL.render(line, True, msg_color),
                  (x, y0 + i*30))

# ========================================================
#                 ELEMENTOS DO MENU INICIAL
# ========================================================
MENU_RANDOM_RECT = pg.Rect(300, 200, 400, 80)
MENU_CUSTOM_RECT = pg.Rect(300, 300, 400, 80)

SIZE_LEFT_RECT   = pg.Rect(220, 420, 80, 80)
SIZE_RIGHT_RECT  = pg.Rect(700, 420, 80, 80)
SIZE_DISPLAY_RECT= pg.Rect(320, 420, 360, 80)

def draw_menu(surf, size_selected):
    surf.fill(WHITE)
    title = BIG.render("Escolha o modo", True, BLACK)
    surf.blit(title, ((WINDOW_SIZE[0]-title.get_width())//2, 80))

    draw_button(surf, MENU_RANDOM_RECT, "Puzzle Aleatório")
    draw_button(surf, MENU_CUSTOM_RECT, "Montar Manualmente")

    draw_button(surf, SIZE_LEFT_RECT,  "<")
    draw_button(surf, SIZE_RIGHT_RECT, ">")
    pg.draw.rect(surf, DARKGRAY, SIZE_DISPLAY_RECT, border_radius=12)
    label = SMALL.render(f"Tamanho: {size_selected}×{size_selected}", True, WHITE)
    surf.blit(label, (SIZE_DISPLAY_RECT.x + (SIZE_DISPLAY_RECT.width - label.get_width()) // 2,
                      SIZE_DISPLAY_RECT.y + (SIZE_DISPLAY_RECT.height - label.get_height()) // 2))

# ========================================================
#                   PYGAME – ESTADO GLOBAL
# ========================================================
window = pg.display.set_mode(WINDOW_SIZE)
pg.display.set_caption("Sudoku – Tamanho Dinâmico")
clock = pg.time.Clock()

board        = new_board()
input_locked = False
message      = ""
msg_color    = GREEN
selected     = (-1, -1)
game_phase   = "menu"

# ========================================================
#                        GAME LOOP
# ========================================================
running = True
while running:
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            running = False

        # ---------------- MENU ----------------
        if game_phase == "menu":
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                if SIZE_LEFT_RECT.collidepoint(ev.pos):
                    size_idx = (size_idx - 1) % len(SIZE_OPTIONS)
                    configure(SIZE_OPTIONS[size_idx])
                    board = new_board()
                elif SIZE_RIGHT_RECT.collidepoint(ev.pos):
                    size_idx = (size_idx + 1) % len(SIZE_OPTIONS)
                    configure(SIZE_OPTIONS[size_idx])
                    board = new_board()
                elif MENU_RANDOM_RECT.collidepoint(ev.pos):
                    solve_attempts = 0
                    board = generate_puzzle()
                    message, input_locked = "", False
                    game_phase = "play"
                elif MENU_CUSTOM_RECT.collidepoint(ev.pos):
                    board = new_board()
                    message, msg_color = "Insira suas pistas e clique Solve", BLACK
                    input_locked = False
                    game_phase   = "play"
            continue  # evita processar eventos de play

        # ---------------- PLAY ----------------
        if game_phase == "play":
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my   = ev.pos
                bx, by   = BOARD_TOPLEFT
                inside   = (bx <= mx <= bx+GRID_SIZE and
                            by <= my <= by+GRID_SIZE)

                if inside and not input_locked:
                    selected = ((mx - bx) // CELL_SIZE,
                                (my - by) // CELL_SIZE)
                else:
                    selected = (-1, -1)

                if pg.Rect(700, 50, 250, 80).collidepoint(ev.pos):
                    if is_board_consistent(board):
                        temp = copy.deepcopy(board)
                        solve_attempts = 0
                        start = time.time()
                        if solve_backtracking(temp):
                            board[:]   = temp
                            elapsed    = time.time() - start
                            message    = f"Resolvido em {elapsed:.3f}s "\
                                         f"({solve_attempts} tent.)"
                            msg_color  = GREEN
                            input_locked = True
                        else:
                            message, msg_color = "Sem solução.", RED
                    else:
                        message, msg_color = "Conflitos nas pistas!", RED

                if pg.Rect(700, 150, 250, 80).collidepoint(ev.pos):
                    board = new_board()
                    message, input_locked = "", False

            if (ev.type == pg.KEYDOWN and
                    selected != (-1, -1) and
                    not input_locked):
                key = pg.key.name(ev.key)
                sx, sy = selected
                if key.isdigit() and key != "0":
                    n = int(key)
                    if 1 <= n <= SIZE:
                        board[sy][sx] = n
                elif ev.key in (pg.K_BACKSPACE, pg.K_SPACE):
                    board[sy][sx] = EMPTY

    # ---------------- RENDER ----------------
    if game_phase == "menu":
        draw_menu(window, SIZE)
    else:
        draw_board(window)
        mx, my = pg.mouse.get_pos()
        bx, by = BOARD_TOPLEFT

        if bx <= mx <= bx+GRID_SIZE and by <= my <= by+GRID_SIZE:
            hx, hy = (mx - bx) // CELL_SIZE, (my - by) // CELL_SIZE
            highlight_cell(window, hx, hy, SKY)
        if selected != (-1, -1):
            highlight_cell(window, *selected, BLUE)

        draw_numbers(window, board)
        draw_button(window, pg.Rect(700, 50, 250, 80),  "Solve / Check")
        draw_button(window, pg.Rect(700, 150, 250, 80), "Clear Board")
        draw_message(window, message, msg_color)

    pg.display.flip()
    clock.tick(FPS)

pg.quit()