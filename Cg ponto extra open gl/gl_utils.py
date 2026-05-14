
import numpy as np
import pygame

from OpenGL.GL import (
    glGenTextures, glBindTexture, glTexImage2D, glTexParameteri,
    glDeleteTextures, glEnable, glDisable, glBegin, glEnd,
    glVertex2f, glTexCoord2f, glColor3f, glColor4f, glLineWidth,
    GL_TEXTURE_2D, GL_RGB, GL_RGBA, GL_UNSIGNED_BYTE,
    GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER,
    GL_LINEAR, GL_NEAREST, GL_QUADS, GL_LINES, GL_LINE_LOOP,
)


#  ESSE CARREGA TEXTURAS


def make_texture(arr: np.ndarray) -> int:
    

    arr_flip = np.flipud(arr)
    tid = int(glGenTextures(1))
    glBindTexture(GL_TEXTURE_2D, tid)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGB,
        arr.shape[1], arr.shape[0], 0,
        GL_RGB, GL_UNSIGNED_BYTE, arr_flip.tobytes(),
    )
    return tid


def update_texture(tid: int, arr: np.ndarray) -> None:
    """dados de uma textura existente sem recriar o ID."""
    arr_flip = np.flipud(arr)
    glBindTexture(GL_TEXTURE_2D, tid)
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGB,
        arr.shape[1], arr.shape[0], 0,
        GL_RGB, GL_UNSIGNED_BYTE, arr_flip.tobytes(),
    )



def draw_quad_textured(tid: int,
                       x: float, y: float,
                       w: float, h: float) -> None:

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tid)
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x,     y)
    glTexCoord2f(1, 0); glVertex2f(x + w, y)
    glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
    glTexCoord2f(0, 1); glVertex2f(x,     y + h)
    glEnd()
    glDisable(GL_TEXTURE_2D)


def fill_rect(x: float, y: float,
              w: float, h: float,
              r: float, g: float, b: float,
              a: float = 1.0) -> None:

    glColor4f(r, g, b, a)
    glBegin(GL_QUADS)
    glVertex2f(x,     y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x,     y + h)
    glEnd()


def stroke_rect(x: float, y: float,
                w: float, h: float,
                r: float, g: float, b: float,
                a: float = 1.0,
                lw: float = 1.0) -> None:

    glLineWidth(lw)
    glColor4f(r, g, b, a)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x,     y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x,     y + h)
    glEnd()
    glLineWidth(1.0)


def draw_hline(x1: float, x2: float, y: float,
               r: float, g: float, b: float,
               lw: float = 1.0) -> None:

    glLineWidth(lw)
    glColor3f(r, g, b)
    glBegin(GL_LINES)
    glVertex2f(x1, y)
    glVertex2f(x2, y)
    glEnd()
    glLineWidth(1.0)


def draw_vline(x: float, y1: float, y2: float,
               r: float, g: float, b: float,
               lw: float = 1.0) -> None:

    glLineWidth(lw)
    glColor3f(r, g, b)
    glBegin(GL_LINES)
    glVertex2f(x, y1)
    glVertex2f(x, y2)
    glEnd()
    glLineWidth(1.0)


# inserir textos dps

_font_cache: dict = {}


def _get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont("monospace", size, bold=bold)
    return _font_cache[key]


def draw_text(text: str,
              x: int, y: int,
              size: int = 14,
              color: tuple = (255, 255, 255),
              bold: bool = False) -> tuple[int, int]:
    """
    Renderiza texto na posição (x, y) em coordenadas OpenGL.

    Cria uma textura temporária por frame 
    Retorna (largura, altura) em pixels do texto renderizado.
    """
    font = _get_font(size, bold)
    surf = font.render(text, True, color)
    tw, th = surf.get_size()
    raw   = pygame.image.tostring(surf, "RGBA", True)

    tid = int(glGenTextures(1))
    glBindTexture(GL_TEXTURE_2D, tid)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tw, th, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, raw)

    glEnable(GL_TEXTURE_2D)
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x,      y)
    glTexCoord2f(1, 0); glVertex2f(x + tw, y)
    glTexCoord2f(1, 1); glVertex2f(x + tw, y + th)
    glTexCoord2f(0, 1); glVertex2f(x,      y + th)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glDeleteTextures([tid])

    return tw, th


def measure_text(text: str, size: int = 14, bold: bool = False) -> tuple[int, int]:

    font = _get_font(size, bold)
    return font.size(text)