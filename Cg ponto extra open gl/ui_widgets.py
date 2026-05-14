
from gl_utils import fill_rect, stroke_rect, draw_text, measure_text

#  BOTÃO


class Button:
    def __init__(self,
                 x: int, y: int, w: int, h: int,
                 label: str,
                 bg: tuple = (0.12, 0.48, 0.90),
                 fg: tuple = (255, 255, 255)):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.label = label
        self.bg    = bg
        self.fg    = fg
        self.hover = False



    def draw(self) -> None:
        r, g, b = self.bg
        if self.hover:
            r, g, b = min(1, r + 0.12), min(1, g + 0.12), min(1, b + 0.12)

        fill_rect(self.x, self.y, self.w, self.h, r, g, b)
        stroke_rect(self.x, self.y, self.w, self.h,
                    1.0, 1.0, 1.0, a=0.25)

        tw, th = measure_text(self.label, size=13, bold=True)
        tx = self.x + (self.w - tw) // 2
        ty = self.y + (self.h - th) // 2
        draw_text(self.label, tx, ty, size=13,
                  color=self.fg, bold=True)

    def contains(self, mx: int, my: int) -> bool:
        return (self.x <= mx <= self.x + self.w and
                self.y <= my <= self.y + self.h)



#  SLIDER

class Slider:
    TRACK_H  = 6    
    KNOB_W   = 14   
    KNOB_H   = 20   

    def __init__(self,
                 x: int, y: int, w: int,
                 label: str,
                 vmin: float, vmax: float, default: float,
                 color: tuple = (0.3, 0.7, 1.0),
                 fmt: str = "{:.2f}"):
        self.x, self.y, self.w = x, y, w
        self.label   = label
        self.vmin    = vmin
        self.vmax    = vmax
        self.value   = default
        self.default = default
        self.color   = color
        self.fmt     = fmt

    @property
    def track_cy(self) -> int:
        return self.y + 22

    @property
    def knob_cx(self) -> int:
        t = (self.value - self.vmin) / (self.vmax - self.vmin)
        return self.x + int(t * self.w)

    def draw(self) -> None:
        cr, cg, cb = self.color
        ty = self.track_cy
        kx = self.knob_cx
        th = self.TRACK_H
        kw = self.KNOB_W
        kh = self.KNOB_H

        fill_rect(self.x, ty - th // 2, self.w, th, 0.15, 0.15, 0.22)

        fill_width = max(0, kx - self.x)
        fill_rect(self.x, ty - th // 2, fill_width, th, cr, cg, cb)

        fill_rect(kx - kw // 2, ty - kh // 2, kw, kh, cr, cg, cb)
        stroke_rect(kx - kw // 2, ty - kh // 2, kw, kh,
                    1.0, 1.0, 1.0, a=0.45)

        # formatação dos números visível para apresentação!
        val_str = self.fmt.format(self.value)
        draw_text(f"{self.label}:  {val_str}",
                  self.x, self.y + 4,
                  size=12, color=(195, 210, 230))

    def hit(self, mx: int, my: int) -> bool:
        ty = self.track_cy
        kh = self.KNOB_H
        return (self.x - 4 <= mx <= self.x + self.w + 4 and
                ty - kh <= my <= ty + kh)

    def set_from_mouse(self, mx: int) -> None:
        t = max(0.0, min(1.0, (mx - self.x) / self.w))
        self.value = self.vmin + t * (self.vmax - self.vmin)

    def reset(self) -> None:
        self.value = self.default