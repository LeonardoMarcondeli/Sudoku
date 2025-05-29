import pygame as pg
import random, copy, time as time   # random → embaralhar; copy → clone profundo; time → medir solução

# =============================================================
#                    CONFIGURAÇÕES INICIAIS
# =============================================================
WINDOW_SIZE = (1000, 700)           # largura, altura da janela
FPS         = 60                    # quadros por segundo

# Paleta de cores (RGB)
WHITE = (245, 245, 245); BLACK = (30, 30, 30)
GRAY  = (200, 200, 200); DARKGRAY = (100, 100, 100)
GREEN = (0, 160, 100);  L_GREEN  = (0, 200, 130)
SKY   = (220, 230, 250); BLUE    = (80, 130, 255)
RED   = (200,  60,  60)

EMPTY = "n"                          # sentinela para célula vazia

# -------------------------------------------------------------
#  TAMANHO DINÂMICO DO TABULEIRO
# -------------------------------------------------------------
SIZE_OPTIONS = [3, 6, 9, 12, 15, 18] # múltiplos de 3
size_idx     = 0                     # posição inicial na lista

def configure(sz: int):
    """
    Ajusta variáveis globais conforme o tamanho (SZ × SZ).
    Tudo que depende de SIZE – fonte, tamanho das células, posição do tabuleiro – é recalculado aqui.
    """
    global SIZE, BOX_ROWS, BOX_COLS
    global CELL_SIZE, GRID_SIZE, BOARD_TOPLEFT
    global BIG, SMALL

    SIZE       = sz
    BOX_ROWS   = 3                   # fixo: 3 linhas por bloco
    BOX_COLS   = SIZE // BOX_ROWS    # colunas variam (ex.: 4, 5, 6…)

    # calcula tamanho da célula para caber na janela, com margem lateral para botões
    CELL_SIZE  = min((WINDOW_SIZE[0] - 300) // SIZE,
                     (WINDOW_SIZE[1] - 100) // SIZE)
    GRID_SIZE  = CELL_SIZE * SIZE
    BOARD_TOPLEFT = (50, 50)         # canto superior-esquerdo da grade

    # fontes proporcional ao CELL_SIZE
    BIG   = pg.font.SysFont("Segoe UI", max(18, int(CELL_SIZE * 0.8)), bold=True)
    SMALL = pg.font.SysFont("Segoe UI", 28)

# -------------------------------------------------------------
#  PYGAME E FONTES FIXAS
# -------------------------------------------------------------
pg.init(); pg.font.init()
TITLE_FONT     = pg.font.SysFont("Segoe UI", 48, bold=True)  # usada no menu
configure(SIZE_OPTIONS[size_idx])                            # gera fontes BIG/SMALL vinculadas ao CELL_SIZE

solve_attempts = 0        # contador global de tentativas do backtracking

# =============================================================
#                     FUNÇÕES DE LÓGICA
# =============================================================
def new_board():
    """Cria tabuleiro vazio SIZE × SIZE."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

# Acessos rápidos
def row(b, y): return b[y]
def col(b, x): return [b[i][x] for i in range(SIZE)]

def block(b, x, y):
    """Retorna todas as células do bloco onde (x, y) está."""
    bx = (x // BOX_COLS) * BOX_COLS
    by = (y // BOX_ROWS) * BOX_ROWS
    return [b[j][i] for j in range(by, by + BOX_ROWS)
                       for i in range(bx, bx + BOX_COLS)]

def valid_number(b, x, y, n):
    """Checa se n é válido na posição (x, y)."""
    return n not in row(b, y) and n not in col(b, x) and n not in block(b, x, y)

def is_board_consistent(b):
    """Verifica se não há repetições – usado para entrada manual."""
    # linhas
    for y in range(SIZE):
        vals = [v for v in b[y] if v != EMPTY]
        if len(vals) != len(set(vals)): return False
    # colunas
    for x in range(SIZE):
        vals = [b[y][x] for y in range(SIZE) if b[y][x] != EMPTY]
        if len(vals) != len(set(vals)): return False
    # blocos
    for by in range(0, SIZE, BOX_ROWS):
        for bx in range(0, SIZE, BOX_COLS):
            vals = [b[yy][xx] for yy in range(by, by + BOX_ROWS)
                               for xx in range(bx, bx + BOX_COLS)
                               if b[yy][xx] != EMPTY]
            if len(vals) != len(set(vals)): return False
    return True

def solve_backtracking(b, randomize=False):
    """
    Resolve recursivamente com backtracking.
    Se randomize=True, embaralha a ordem de tentativas (útil para gerar puzzles).
    """
    global solve_attempts
    for y in range(SIZE):
        for x in range(SIZE):
            if b[y][x] == EMPTY:
                nums = list(range(1, SIZE + 1))
                if randomize: random.shuffle(nums)
                for n in nums:
                    if valid_number(b, x, y, n):
                        solve_attempts += 1
                        b[y][x] = n
                        if solve_backtracking(b, randomize): return True
                        b[y][x] = EMPTY
                return False
    return True  # tabuleiro completo

def generate_puzzle(clue_ratio=0.45):
    """
    1) Gera tabuleiro completamente preenchido
    2) Remove células até restar clue_ratio de pistas
    """
    global solve_attempts
    solve_attempts = 0            # zera contador para estatísticas
    full = new_board()
    solve_backtracking(full, randomize=True)

    puzzle = copy.deepcopy(full)
    total    = SIZE * SIZE
    clues    = int(total * clue_ratio)
    to_blank = total - clues

    cells = list(range(total)); random.shuffle(cells)
    for _ in range(to_blank):
        y, x = divmod(cells.pop(), SIZE)
        puzzle[y][x] = EMPTY
    return puzzle

# =============================================================
#                        FUNÇÕES DE UI
# =============================================================
def draw_board(surf):
    """Desenha grade e linhas grossas/finas."""
    bx, by = BOARD_TOPLEFT
    surf.fill(WHITE)
    pg.draw.rect(surf, DARKGRAY, (bx, by, GRID_SIZE, GRID_SIZE), 4)

    for i in range(1, SIZE):
        # horizontais
        y = by + i * CELL_SIZE
        pg.draw.line(surf,
                     DARKGRAY if i % BOX_ROWS == 0 else GRAY,
                     (bx, y), (bx + GRID_SIZE, y),
                     4 if i % BOX_ROWS == 0 else 1)
        # verticais
        x = bx + i * CELL_SIZE
        pg.draw.line(surf,
                     DARKGRAY if i % BOX_COLS == 0 else GRAY,
                     (x, by), (x, by + GRID_SIZE),
                     4 if i % BOX_COLS == 0 else 1)

def draw_numbers(surf, b):
    """Renderiza todos os números já presentes no tabuleiro."""
    bx, by = BOARD_TOPLEFT
    for y in range(SIZE):
        for x in range(SIZE):
            v = b[y][x]
            if v != EMPTY:
                img = BIG.render(str(v), True, BLACK)
                surf.blit(img, img.get_rect(center=(bx + x * CELL_SIZE + CELL_SIZE // 2,
                                                    by + y * CELL_SIZE + CELL_SIZE // 2)))

def highlight_cell(surf, x, y, color):
    """Destaca uma célula (hover ou seleção)."""
    bx, by = BOARD_TOPLEFT
    pg.draw.rect(surf, color,
                 (bx + x * CELL_SIZE, by + y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                 border_radius=4)

# ------ elementos genéricos ------
def draw_button(surf, rect, text):
    hovered = rect.collidepoint(pg.mouse.get_pos())
    pg.draw.rect(surf, L_GREEN if hovered else GREEN, rect, border_radius=12)
    lbl = SMALL.render(text, True, WHITE)
    surf.blit(lbl, (rect.x + (rect.width  - lbl.get_width())  // 2,
                    rect.y + (rect.height - lbl.get_height()) // 2))

def draw_message(surf, message, color):
    """Mostra mensagem (resolvido, erro, etc.) quebrando linhas se necessário."""
    if not message: return
    words, lines, cur = message.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if SMALL.size(test)[0] < 260: cur = test
        else: lines.append(cur); cur = w
    lines.append(cur)

    x, y0 = 700, 340  # início mais abaixo para não colidir com botões
    for i, line in enumerate(lines):
        surf.blit(SMALL.render(line, True, color), (x, y0 + i * 30))

# ------------------------ BOTÕES / RETÂNGULOS -------------------------
MENU_RANDOM_RECT  = pg.Rect(300, 200, 400, 80)
MENU_CUSTOM_RECT  = pg.Rect(300, 300, 400, 80)
SIZE_LEFT_RECT    = pg.Rect(220, 420, 80, 80)
SIZE_RIGHT_RECT   = pg.Rect(700, 420, 80, 80)
SIZE_DISPLAY_RECT = pg.Rect(320, 420, 360, 80)
BACK_RECT         = pg.Rect(700, 250, 250, 80)   # botão voltar

def draw_menu(surf, size_selected):
    """Tela de menu principal."""
    surf.fill(WHITE)
    t = TITLE_FONT.render("Escolha o modo", True, BLACK)
    surf.blit(t, ((WINDOW_SIZE[0]-t.get_width()) // 2, 80))

    # botões de modo
    draw_button(surf, MENU_RANDOM_RECT, "Puzzle Aleatório")
    draw_button(surf, MENU_CUSTOM_RECT, "Montar Manualmente")

    # seletor de tamanho
    draw_button(surf, SIZE_LEFT_RECT,  "<")
    draw_button(surf, SIZE_RIGHT_RECT, ">")
    pg.draw.rect(surf, DARKGRAY, SIZE_DISPLAY_RECT, border_radius=12)
    lbl = SMALL.render(f"Tamanho: {size_selected}×{size_selected}", True, WHITE)
    surf.blit(lbl, (SIZE_DISPLAY_RECT.x + (SIZE_DISPLAY_RECT.width - lbl.get_width()) // 2,
                    SIZE_DISPLAY_RECT.y + (SIZE_DISPLAY_RECT.height - lbl.get_height()) // 2))

# =============================================================
#                        LOOP PRINCIPAL
# =============================================================
window = pg.display.set_mode(WINDOW_SIZE)
pg.display.set_caption("Sudoku – Tamanho Dinâmico")
clock = pg.time.Clock()

board        = new_board()
input_locked = False   # bloqueia edição após resolver
message      = ""
msg_color    = GREEN
selected     = (-1, -1)
game_phase   = "menu"  # menu ▸ play

running = True
while running:
    # -------------------- EVENTOS --------------------
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            running = False

        # -------- EVENTOS NO MENU --------
        if game_phase == "menu":
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                if SIZE_LEFT_RECT.collidepoint(ev.pos):   # tamanho --
                    size_idx = (size_idx - 1) % len(SIZE_OPTIONS)
                    configure(SIZE_OPTIONS[size_idx]); board = new_board()
                elif SIZE_RIGHT_RECT.collidepoint(ev.pos):# tamanho ++
                    size_idx = (size_idx + 1) % len(SIZE_OPTIONS)
                    configure(SIZE_OPTIONS[size_idx]); board = new_board()
                elif MENU_RANDOM_RECT.collidepoint(ev.pos):
                    board = generate_puzzle(); message = ""; input_locked = False
                    game_phase = "play"
                elif MENU_CUSTOM_RECT.collidepoint(ev.pos):
                    board = new_board(); message = "Insira pistas e clique Solve"
                    msg_color = BLACK; input_locked = False; game_phase = "play"
            continue  # volta para renderização

        # -------- EVENTOS NO PLAY --------
        if game_phase == "play":
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                bx, by = BOARD_TOPLEFT
                inside = (bx <= mx <= bx + GRID_SIZE and by <= my <= by + GRID_SIZE)

                # selecionar célula
                if inside and not input_locked:
                    selected = ((mx - bx) // CELL_SIZE, (my - by) // CELL_SIZE)
                else:
                    selected = (-1, -1)

                # Solve / Check
                if pg.Rect(700, 50, 250, 80).collidepoint(ev.pos):
                    if is_board_consistent(board):
                        temp = copy.deepcopy(board); solve_attempts = 0
                        start = time.time()
                        if solve_backtracking(temp):
                            board[:] = temp
                            message  = f"Resolvido em {time.time()-start:.3f}s ({solve_attempts} tent.)"
                            msg_color, input_locked = GREEN, True
                        else:
                            message, msg_color = "Sem solução.", RED
                    else:
                        message, msg_color = "Conflitos nas pistas!", RED

                # Clear
                if pg.Rect(700, 150, 250, 80).collidepoint(ev.pos):
                    board = new_board(); message = ""; input_locked = False

                # Voltar ao menu
                if BACK_RECT.collidepoint(ev.pos):
                    game_phase = "menu"; selected = (-1, -1); message = ""; input_locked = False

            # entrada de números / backspace / espaço
            if ev.type == pg.KEYDOWN and selected != (-1, -1) and not input_locked:
                k = pg.key.name(ev.key); sx, sy = selected
                if k.isdigit() and k != "0":
                    n = int(k)
                    if 1 <= n <= SIZE: board[sy][sx] = n
                elif ev.key in (pg.K_BACKSPACE, pg.K_SPACE):
                    board[sy][sx] = EMPTY

    # -------------------- DRAW --------------------
    if game_phase == "menu":
        draw_menu(window, SIZE)
    else:
        draw_board(window)
        # hover + seleção
        mx, my = pg.mouse.get_pos()
        bx, by = BOARD_TOPLEFT
        if bx <= mx <= bx + GRID_SIZE and by <= my <= by + GRID_SIZE:
            highlight_cell(window, (mx - bx) // CELL_SIZE, (my - by) // CELL_SIZE, SKY)
        if selected != (-1, -1):
            highlight_cell(window, *selected, BLUE)

        draw_numbers(window, board)
        draw_button(window, pg.Rect(700, 50, 250, 80),  "Solve / Check")
        draw_button(window, pg.Rect(700, 150, 250, 80), "Clear Board")
        draw_button(window, BACK_RECT, "Voltar ao Menu")
        draw_message(window, message, msg_color)

    pg.display.flip()
    clock.tick(FPS)

pg.quit()