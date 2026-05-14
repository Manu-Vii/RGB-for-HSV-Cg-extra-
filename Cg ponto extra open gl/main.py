import sys
import os
import ctypes
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog

import glfw

from OpenGL.GL import (
    glClear, glClearColor, glEnable, glDisable,
    glMatrixMode, glLoadIdentity, glOrtho, glViewport,
    glBlendFunc, glDeleteTextures,
    GL_COLOR_BUFFER_BIT, GL_BLEND,
    GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,
    GL_DEPTH_TEST, GL_PROJECTION, GL_MODELVIEW,
)

import pygame
pygame.font.init()

from color_math import rgb_to_hsv, apply_hsv_adjustments, hsv_stats
from gl_utils   import (make_texture, update_texture,
                        draw_quad_textured, fill_rect, stroke_rect,
                        draw_hline, draw_text, measure_text)
from ui_widgets import Button, Slider


#  CONFIGURAÇÕES DE LAYOUOOOOOT E ESCALA


WIN_W   = 1280   
WIN_H   = 720    
TITLE_H = 46     
PANEL_H = 168    
IMG_PAD = 10     
LABEL_H = 24     

# Zoom da Interface 
UI_SCALE = 1.5   

class App:

    def __init__(self):
        if not glfw.init():
            raise RuntimeError("Falha ao inicializar o GLFW")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)

        self.window = glfw.create_window(
            WIN_W, WIN_H,
            "Conversor RGB for HSV  |  CG  / Aluna: Emanuele Lima",
            None,   
            None,   
        )
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Falha ao criar a janela GLFW")

        glfw.make_context_current(self.window)
        glfw.swap_interval(1)

        win_w, win_h = glfw.get_window_size(self.window)
        self._w = int(win_w / UI_SCALE)
        self._h = int(win_h / UI_SCALE)

        glClearColor(0.07, 0.07, 0.10, 1.0)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.img_rgb  = None   
        self.img_hsv  = None   
        self.img_adj  = None   
        self.tex_orig = None   
        self.tex_adj  = None   
        self.img_name = ""
        self._active_sl = None

        glfw.set_key_callback(self.window,              self._on_key)
        glfw.set_mouse_button_callback(self.window,     self._on_mouse_button)
        glfw.set_cursor_pos_callback(self.window,       self._on_cursor_pos)
        
        self._build_ui()

    def _build_ui(self) -> None:
        PAD  = 20
        BH   = 44    
        BTN1 = 200   
        BTN2 = 130   

        self.btn_open = Button(
            PAD, 14, BTN1, BH,
            "\u2b06  ENVIAR",
            bg=(0.10, 0.48, 0.90))

        self.btn_reset = Button(
            PAD + BTN1 + 10, 14, BTN2, BH,
            "\u21ba  ZERAR",
            bg=(0.20, 0.20, 0.26))

        SX = PAD + BTN1 + 10 + BTN2 + 22
        SW = self._w - SX - PAD   

        self.sl_h = Slider(
            SX, 10,       SW,
            "H  Matiz (Hue)", -180, 180, 0,
            color=(1.0, 0.55, 0.10), fmt="{:+.0f}\u00b0")

        self.sl_s = Slider(
            SX, 10 + 56,  SW,
            "S  Saturacao",  -1.0, 1.0, 0,
            color=(0.20, 0.85, 0.40), fmt="{:+.2f}")

        self.sl_v = Slider(
            SX, 10 + 112, SW,
            "V  Luminancia", -1.0, 1.0, 0,
            color=(0.95, 0.88, 0.20), fmt="{:+.2f}")

        self.sliders = [self.sl_h, self.sl_s, self.sl_v]

    def _flip_y(self, y_glfw: float) -> int:
        return self._h - int(y_glfw / UI_SCALE) - 1

    def _on_key(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_O:
            self.open_image()
        elif key == glfw.KEY_R:
            for sl in self.sliders:
                sl.reset()
            self._refresh()

    def _on_mouse_button(self, window, button, action, mods):
        if button != glfw.MOUSE_BUTTON_LEFT:
            return

        xpos, ypos = glfw.get_cursor_pos(window)
        mx = int(xpos / UI_SCALE)
        my = self._flip_y(ypos)

        if action == glfw.PRESS:
            if self.btn_open.contains(mx, my):
                self.open_image()
            elif self.btn_reset.contains(mx, my):
                for sl in self.sliders:
                    sl.reset()
                self._refresh()
            else:
                for sl in self.sliders:
                    if sl.hit(mx, my):
                        sl.set_from_mouse(mx)
                        self._active_sl = sl
                        self._refresh()
                        break

        elif action == glfw.RELEASE:
            self._active_sl = None

    def _on_cursor_pos(self, window, xpos, ypos):
        mx = int(xpos / UI_SCALE)
        my = self._flip_y(ypos)

        self.btn_open.hover  = self.btn_open.contains(mx, my)
        self.btn_reset.hover = self.btn_reset.contains(mx, my)

        if self._active_sl:
            self._active_sl.set_from_mouse(mx)
            self._refresh()
    
    #aqui abre a imagem desejada
    def open_image(self) -> None:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(
            title="Selecionar imagem",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp *.webp *.tiff"),
                ("Todos",   "*.*"),
            ])
        root.destroy()
        if not path:
            return
            
            #manda pra conversão
        img = Image.open(path).convert("RGB")
        MAX = 1080 
        if img.width > MAX or img.height > MAX:
            img.thumbnail((MAX, MAX), Image.LANCZOS)

        self.img_rgb  = np.array(img, dtype=np.uint8)

        #pixel por pixel
        self.img_hsv  = rgb_to_hsv(self.img_rgb)
        self.img_adj  = self.img_rgb.copy()
        self.img_name = os.path.basename(path)

        for sl in self.sliders:
            sl.reset()

        if self.tex_orig:
            glDeleteTextures([self.tex_orig])
        if self.tex_adj:
            glDeleteTextures([self.tex_adj])

        self.tex_orig = make_texture(self.img_rgb)
        self.tex_adj  = make_texture(self.img_adj)

        ih, iw = self.img_rgb.shape[:2]
        stats  = hsv_stats(self.img_hsv)
        print(f"\n[Carregada] {self.img_name}  {iw}x{ih}px")

    def _refresh(self) -> None:
        if self.img_hsv is None:
            return
        self.img_adj = apply_hsv_adjustments(
            self.img_hsv,
            self.sl_h.value,
            self.sl_s.value,
            self.sl_v.value,
        )
        update_texture(self.tex_adj, self.img_adj)

    def _set_ortho(self) -> None:
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self._w, 0, self._h, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def _draw_title_bar(self) -> None:
        y = self._h - TITLE_H
        fill_rect(0, y, self._w, TITLE_H, 0.09, 0.09, 0.13)
        draw_hline(0, self._w, y, 0.15, 0.50, 1.0, lw=2.0)
        draw_text("CONVERSOR RGB for HSV",
                  20, y + 11, size=20,
                  color=(235, 242, 255), bold=True)
        draw_text(
            "Computacao Grafica  \u2502  Aluna: Emanuele Lima",
            400, y + 15, size=12, color=(110, 145, 200))

    def _draw_control_panel(self) -> None:
        fill_rect(0, 0, self._w, PANEL_H, 0.09, 0.09, 0.13)
        draw_hline(0, self._w, PANEL_H, 0.17, 0.17, 0.24, lw=2.0)

        self.btn_open.draw()
        self.btn_reset.draw()
        for sl in self.sliders:
            sl.draw()

    def _draw_image_area(self) -> None:
        IMG_BOT = PANEL_H + 4
        IMG_TOP = self._h - TITLE_H - 4
        area_h  = IMG_TOP - IMG_BOT
        half_w  = self._w // 2

        fill_rect(0,      IMG_BOT, half_w, area_h, 0.08, 0.08, 0.11)
        fill_rect(half_w, IMG_BOT, half_w, area_h, 0.08, 0.08, 0.11)
        fill_rect(half_w - 1, IMG_BOT, 2, area_h, 0.18, 0.18, 0.26)

        if self.tex_orig is None or self.img_rgb is None:
            return

        ih, iw = self.img_rgb.shape[:2]
        aw = half_w - 2 * IMG_PAD
        ah = area_h - 2 * IMG_PAD - LABEL_H

        scale = min(aw / iw, ah / ih)
        dw    = int(iw * scale)
        dh    = int(ih * scale)

        # inagem original 
        ox = IMG_PAD + (aw - dw) // 2
        oy = IMG_BOT + IMG_PAD + (ah - dh) // 2
        draw_quad_textured(self.tex_orig, ox, oy, dw, dh)
        stroke_rect(ox - 1, oy - 1, dw + 2, dh + 2,
                    0.25, 0.50, 1.0, lw=1.5)
        draw_text(f"ORIGINAL  (RGB)",
                  IMG_PAD, IMG_BOT + area_h - LABEL_H - 2,
                  size=12, color=(120, 175, 255), bold=True)

        # imagem ajustada
        ax = half_w + IMG_PAD + (aw - dw) // 2
        draw_quad_textured(self.tex_adj, ax, oy, dw, dh)
        stroke_rect(ax - 1, oy - 1, dw + 2, dh + 2,
                    0.10, 0.75, 0.42, lw=1.5)

        # rótulo de resultado 
        lbl = "RESULTADO"

        draw_text(lbl,
                  half_w + IMG_PAD,
                  IMG_BOT + area_h - LABEL_H - 2,
                  size=12, color=(70, 215, 135), bold=True)

    def _draw(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT)
        self._set_ortho()
        self._draw_title_bar()
        self._draw_control_panel()
        self._draw_image_area()

    def run(self) -> None:
        print("=" * 56)
        print("  CONVERSOR RGB -> HSV  |  OpenGL ")
        print("  Aluna: Emanuele Lima")
        print("=" * 56)

        while not glfw.window_should_close(self.window):
            glfw.poll_events()
              
            if glfw.window_should_close(self.window):
                break

            win_w, win_h = glfw.get_window_size(self.window)
            fb_w, fb_h = glfw.get_framebuffer_size(self.window)

            if fb_w == 0 or fb_h == 0:
                continue

            glViewport(0, 0, fb_w, fb_h)

            logical_w = int(win_w / UI_SCALE)
            logical_h = int(win_h / UI_SCALE)

            if logical_w > 0 and logical_h > 0:
                if logical_w != self._w or logical_h != self._h:
                    self._w = logical_w
                    self._h = logical_h
                    self._build_ui()

            self._draw()
            glfw.swap_buffers(self.window)

        glfw.destroy_window(self.window)
        glfw.terminate()
        sys.exit()

if __name__ == "__main__":
    App().run()
