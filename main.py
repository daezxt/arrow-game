import pygame
import sys
import random
from levels import LEVELS

# ==================== 初始化 ====================
pygame.init()

CELL_SIZE = 80
GRID_W, GRID_H = 5, 5
BOARD_LEFT = 100
BOARD_TOP = 180
SCREEN_W = BOARD_LEFT * 2 + CELL_SIZE * GRID_W
SCREEN_H = BOARD_TOP + CELL_SIZE * GRID_H + 150

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (70, 130, 180)
RED = (220, 60, 60)
GREEN = (60, 180, 90)
YELLOW = (240, 200, 60)

BG_TOP = (245, 250, 255)
BG_BOTTOM = (215, 230, 245)
BOARD_BG = (255, 255, 255)
GRID_LINE = (210, 220, 230)
CARD_BG = (255, 255, 255)
TITLE_COLOR = (40, 90, 150)
TEXT_COLOR = (50, 60, 70)
BTN_BLUE = (70, 130, 180)
BTN_BLUE_HOVER = (90, 150, 200)
BTN_GREEN = (60, 170, 100)
BTN_GREEN_HOVER = (80, 190, 120)
SHADOW = (180, 195, 210)

FONT_PATH = "C:/Windows/Fonts/simhei.ttf"
FONT = pygame.font.Font(FONT_PATH, 28)
FONT_SMALL = pygame.font.Font(FONT_PATH, 22)
FONT_BIG = pygame.font.Font(FONT_PATH, 48)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("一箭又一箭")
clock = pygame.time.Clock()


# ==================== 游戏逻辑类 ====================
class Game:
    def __init__(self, level_index=0):
        self.level_index = level_index
        self.load_level(level_index)
        self.state = "playing"
        self.animations = []

    def load_level(self, index):
        raw = LEVELS[index]
        self.board = [row[:] for row in raw]
        self.rows = len(self.board)
        self.cols = len(self.board[0])
        self.mistakes_left = 3
        self.remaining = sum(1 for row in self.board for cell in row if cell)

        palette = [
            (230, 80, 80), (80, 160, 230), (80, 200, 120), (240, 180, 60),
            (180, 100, 220), (240, 130, 180), (100, 200, 220), (200, 200, 80),
        ]
        self.colors = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] is not None:
                    self.colors[(r, c)] = random.choice(palette)

    def restart(self):
        self.load_level(self.level_index)
        self.state = "playing"
        self.animations = []

    def next_level(self):
        if self.level_index + 1 < len(LEVELS):
            self.level_index += 1
            self.restart()
        else:
            self.state = "all_win"

    def can_fly(self, r, c):
        arrow = self.board[r][c]
        if arrow is None:
            return False

        if arrow == 'U':
            for i in range(r - 1, -1, -1):
                if self.board[i][c] is not None:
                    return False
        elif arrow == 'D':
            for i in range(r + 1, self.rows):
                if self.board[i][c] is not None:
                    return False
        elif arrow == 'L':
            for j in range(c - 1, -1, -1):
                if self.board[r][j] is not None:
                    return False
        elif arrow == 'R':
            for j in range(c + 1, self.cols):
                if self.board[r][j] is not None:
                    return False
        return True

    def click(self, r, c):
        if self.state != "playing":
            return
        if self.board[r][c] is None:
            return

        if self.can_fly(r, c):
            arrow = self.board[r][c]
            self.board[r][c] = None
            self.remaining -= 1
            self.animations.append({
                "r": r, "c": c, "dir": arrow, "t": 0
            })
            if self.remaining == 0:
                self.state = "win"
        else:
            self.mistakes_left -= 1
            self.animations.append({
                "r": r, "c": c, "dir": self.board[r][c], "t": 0, "shake": True
            })
            if self.mistakes_left <= 0:
                self.state = "lose"


# ==================== 绘制函数 ====================
def draw_gradient_background(surface):
    for y in range(SCREEN_H):
        t = y / SCREEN_H
        r = int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_W, y))


def make_rocket_surface(color):
    """生成一个朝上的火箭 Surface，带描边和细节"""
    size = CELL_SIZE
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    cx = size // 2
    cy = size // 2
    s = CELL_SIZE // 3

    outline = (max(0, color[0] - 80), max(0, color[1] - 80), max(0, color[2] - 80))
    light = (min(255, color[0] + 60), min(255, color[1] + 60), min(255, color[2] + 60))

    # 坐标都按“朝上”设计
    nose = (cx, cy - s)
    left = (cx - s * 0.6, cy + s * 0.2)
    right = (cx + s * 0.6, cy + s * 0.2)
    body_rect = pygame.Rect(cx - s * 0.4, cy, s * 0.8, s * 0.8)
    flame = [(cx - s * 0.3, cy + s * 0.8),
             (cx + s * 0.3, cy + s * 0.8),
             (cx, cy + s * 1.3)]
    fin_left = [(cx - s * 0.6, cy + s * 0.6),
                (cx - s * 0.4, cy + s * 0.2),
                (cx - s * 0.4, cy + s * 0.9)]
    fin_right = [(cx + s * 0.6, cy + s * 0.6),
                 (cx + s * 0.4, cy + s * 0.2),
                 (cx + s * 0.4, cy + s * 0.9)]
    window_pos = (cx, cy + s * 0.3)

    # 尾焰
    pygame.draw.polygon(surf, (255, 220, 80), flame)
    inner_flame = []
    for i, (fx, fy) in enumerate(flame):
        if i == 2:
            inner_flame.append((fx, fy))
        else:
            inner_flame.append(((fx + cx) / 2, (fy + cy) / 2))
    pygame.draw.polygon(surf, (255, 140, 40), inner_flame)

    # 尾翼
    for fin in (fin_left, fin_right):
        pygame.draw.polygon(surf, outline, fin)
        pygame.draw.polygon(surf, color, fin, 1)

    # 机身
    pygame.draw.rect(surf, color, body_rect)
    pygame.draw.rect(surf, outline, body_rect, 2)
    hl_rect = pygame.Rect(body_rect.x + 3, body_rect.y + 3,
                          max(2, body_rect.width // 4), max(2, body_rect.height - 6))
    pygame.draw.rect(surf, light, hl_rect)

    # 机头
    pygame.draw.polygon(surf, color, [nose, left, right])
    pygame.draw.polygon(surf, outline, [nose, left, right], 2)
    nose_hl = [nose,
               ((nose[0] + left[0]) / 2, (nose[1] + left[1]) / 2),
               ((nose[0] + right[0]) / 2, (nose[1] + right[1]) / 2)]
    pygame.draw.polygon(surf, light, nose_hl)

    # 舷窗
    wr = max(3, int(s * 0.22))
    wx, wy = int(window_pos[0]), int(window_pos[1])
    pygame.draw.circle(surf, outline, (wx, wy), wr + 1)
    pygame.draw.circle(surf, (180, 230, 255), (wx, wy), wr)
    pygame.draw.circle(surf, WHITE, (wx - wr // 3, wy - wr // 3), max(1, wr // 3))

    return surf


# 缓存：同一颜色只生成一次
_rocket_cache = {}


def draw_arrow(surface, cx, cy, direction, color=BLACK):
    """根据方向旋转同一个朝上的火箭，保证四个方向形状一致"""
    if color not in _rocket_cache:
        _rocket_cache[color] = make_rocket_surface(color)
    base = _rocket_cache[color]

    if direction == 'U':
        rotated = base
    elif direction == 'R':
        rotated = pygame.transform.rotate(base, -90)
    elif direction == 'D':
        rotated = pygame.transform.rotate(base, 180)
    elif direction == 'L':
        rotated = pygame.transform.rotate(base, 90)
    else:
        return

    rect = rotated.get_rect(center=(int(cx), int(cy)))
    surface.blit(rotated, rect)

def update_animations(game, dt):
    for anim in game.animations[:]:
        anim["t"] += dt
        if anim.get("shake"):
            if anim["t"] > 0.4:
                game.animations.remove(anim)
        else:
            if anim["t"] > 1.5:
                game.animations.remove(anim)


def draw_board(screen, game):
    board_rect = pygame.Rect(
        BOARD_LEFT - 10, BOARD_TOP - 10,
        game.cols * CELL_SIZE + 20, game.rows * CELL_SIZE + 20
    )
    pygame.draw.rect(screen, SHADOW, board_rect.move(4, 4), border_radius=14)
    pygame.draw.rect(screen, BOARD_BG, board_rect, border_radius=14)
    pygame.draw.rect(screen, GRID_LINE, board_rect, 2, border_radius=14)

    anim_cells = {(a["r"], a["c"]) for a in game.animations}

    # 画棋盘上静止的火箭
    for r in range(game.rows):
        for c in range(game.cols):
            x = BOARD_LEFT + c * CELL_SIZE
            y = BOARD_TOP + r * CELL_SIZE
            cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRID_LINE, cell_rect, 1)

            arrow = game.board[r][c]
            if arrow and (r, c) not in anim_cells:
                cx = x + CELL_SIZE // 2
                cy = y + CELL_SIZE // 2
                color = game.colors.get((r, c), BLACK)
                draw_arrow(screen, cx, cy, arrow, color)

    # 画动画中的火箭
    for anim in game.animations:
        r, c = anim["r"], anim["c"]
        x = BOARD_LEFT + c * CELL_SIZE
        y = BOARD_TOP + r * CELL_SIZE
        cx = x + CELL_SIZE // 2
        cy = y + CELL_SIZE // 2

        if anim.get("shake"):
            arrow = game.board[r][c]
            if arrow is None:
                continue
            offset = int(6 * (1 if int(anim["t"] * 20) % 2 == 0 else -1))
            cx += offset
        else:
            arrow = anim["dir"]
            speed = 1200
            dist = speed * anim["t"]
            if arrow == 'U':
                cy -= dist
            elif arrow == 'D':
                cy += dist
            elif arrow == 'L':
                cx -= dist
            elif arrow == 'R':
                cx += dist

        color = game.colors.get((r, c), BLACK)
        draw_arrow(screen, cx, cy, arrow, color)

    # 右下角“重新开始”按钮
    btn_rect = pygame.Rect(
        board_rect.right - 150, board_rect.bottom + 20, 140, 50
    )
    mouse_pos = pygame.mouse.get_pos()
    hover = btn_rect.collidepoint(mouse_pos)
    color = BTN_BLUE_HOVER if hover else BTN_BLUE
    pygame.draw.rect(screen, SHADOW, btn_rect.move(2, 2), border_radius=10)
    pygame.draw.rect(screen, color, btn_rect, border_radius=10)
    text = FONT_SMALL.render("重新开始", True, WHITE)
    screen.blit(text, (btn_rect.x + 25, btn_rect.y + 12))

    return btn_rect


def draw_hud(screen, game):
    card = pygame.Rect(BOARD_LEFT - 10, 10, SCREEN_W - 2 * (BOARD_LEFT - 10), 130)
    pygame.draw.rect(screen, SHADOW, card.move(3, 3), border_radius=12)
    pygame.draw.rect(screen, CARD_BG, card, border_radius=12)
    pygame.draw.rect(screen, GRID_LINE, card, 2, border_radius=12)

    text = FONT.render(f"关卡：{game.level_index + 1}", True, TITLE_COLOR)
    screen.blit(text, (BOARD_LEFT + 10, 30))
    text = FONT.render(f"剩余箭头：{game.remaining}", True, TEXT_COLOR)
    screen.blit(text, (BOARD_LEFT + 10, 80))
    text = FONT.render(f"剩余失误：{game.mistakes_left}", True, RED)
    screen.blit(text, (BOARD_LEFT + 280, 80))


def draw_start_screen(screen):
    draw_gradient_background(screen)
    card = pygame.Rect(SCREEN_W // 2 - 220, 150, 440, 320)
    pygame.draw.rect(screen, SHADOW, card.move(5, 5), border_radius=20)
    pygame.draw.rect(screen, CARD_BG, card, border_radius=20)
    pygame.draw.rect(screen, GRID_LINE, card, 2, border_radius=20)

    title = FONT_BIG.render("一箭又一箭", True, TITLE_COLOR)
    screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 190))
    tip = FONT.render("点击火箭，让它飞出棋盘", True, TEXT_COLOR)
    screen.blit(tip, (SCREEN_W // 2 - tip.get_width() // 2, 270))
    tip2 = FONT_SMALL.render("失误 3 次即失败，清空全部火箭通关", True, (120, 130, 140))
    screen.blit(tip2, (SCREEN_W // 2 - tip2.get_width() // 2, 310))

    btn = pygame.Rect(SCREEN_W // 2 - 100, 380, 200, 60)
    mouse_pos = pygame.mouse.get_pos()
    hover = btn.collidepoint(mouse_pos)
    color = BTN_GREEN_HOVER if hover else BTN_GREEN
    pygame.draw.rect(screen, SHADOW, btn.move(3, 3), border_radius=14)
    pygame.draw.rect(screen, color, btn, border_radius=14)
    text = FONT.render("开始游戏", True, WHITE)
    screen.blit(text, (btn.x + 50, btn.y + 15))
    return btn


def draw_result_screen(screen, game, win=True):
    draw_gradient_background(screen)
    card = pygame.Rect(SCREEN_W // 2 - 220, 150, 440, 320)
    pygame.draw.rect(screen, SHADOW, card.move(5, 5), border_radius=20)
    pygame.draw.rect(screen, CARD_BG, card, border_radius=20)
    pygame.draw.rect(screen, GRID_LINE, card, 2, border_radius=20)

    if win:
        msg, color, sub = "恭喜通关！", BTN_GREEN, f"第 {game.level_index + 1} 关完成"
    else:
        msg, color, sub = "失败！", RED, "失误次数已用完"

    text = FONT_BIG.render(msg, True, color)
    screen.blit(text, (SCREEN_W // 2 - text.get_width() // 2, 190))
    sub_text = FONT.render(sub, True, TEXT_COLOR)
    screen.blit(sub_text, (SCREEN_W // 2 - sub_text.get_width() // 2, 270))

    btn = pygame.Rect(SCREEN_W // 2 - 100, 360, 200, 60)
    mouse_pos = pygame.mouse.get_pos()
    hover = btn.collidepoint(mouse_pos)
    base = BTN_BLUE if win else RED
    hover_color = BTN_BLUE_HOVER if win else (240, 90, 90)
    color = hover_color if hover else base
    pygame.draw.rect(screen, SHADOW, btn.move(3, 3), border_radius=14)
    pygame.draw.rect(screen, color, btn, border_radius=14)
    label = FONT.render("下一关" if win else "重新开始", True, WHITE)
    screen.blit(label, (btn.x + 50, btn.y + 15))
    return btn


# ==================== 主循环 ====================
def main():
    game = None
    scene = "start"
    start_btn = None
    result_btn = None
    restart_btn = None
    result_win = True

    running = True
    while running:
        dt = clock.get_time() / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if scene == "start":
                    if start_btn and start_btn.collidepoint(mx, my):
                        game = Game(0)
                        scene = "playing"

                elif scene == "playing":
                    # 右下角重新开始按钮
                    if restart_btn and restart_btn.collidepoint(mx, my):
                        game.restart()
                        continue

                    if BOARD_LEFT <= mx < BOARD_LEFT + game.cols * CELL_SIZE and \
                       BOARD_TOP <= my < BOARD_TOP + game.rows * CELL_SIZE:
                        c = (mx - BOARD_LEFT) // CELL_SIZE
                        r = (my - BOARD_TOP) // CELL_SIZE
                        game.click(r, c)

                    if game.state == "win":
                        scene = "result"
                        result_win = True
                    elif game.state == "lose":
                        scene = "result"
                        result_win = False

                elif scene == "result":
                    if result_btn and result_btn.collidepoint(mx, my):
                        if result_win:
                            game.next_level()
                            if game.state == "all_win":
                                scene = "start"
                            else:
                                scene = "playing"
                        else:
                            game.restart()
                            scene = "playing"

        if scene == "start":
            start_btn = draw_start_screen(screen)
        elif scene == "playing":
            draw_gradient_background(screen)
            update_animations(game, dt)
            draw_hud(screen, game)
            restart_btn = draw_board(screen, game)
        elif scene == "result":
            result_btn = draw_result_screen(screen, game, result_win)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()