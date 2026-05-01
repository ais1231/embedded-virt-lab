"""Simulated OLED display (SSD1306 compatible, 128x64)."""


class OLEDDisplay:
    """Simulated OLED display with 5x7 font rendering."""

    WIDTH = 128
    HEIGHT = 64

    def __init__(self, name: str = "OLED"):
        self.name = name
        self._framebuffer = bytearray(self.WIDTH * self.HEIGHT // 8)
        self._power_on: bool = False
        self._contrast: int = 0x7F
        self._inverted: bool = False
        self._font_5x7 = {
            ord(c): bits for c, bits in [
                ('0', [0x3E, 0x51, 0x49, 0x45, 0x3E]),
                ('1', [0x00, 0x42, 0x7F, 0x40, 0x00]),
                ('2', [0x42, 0x61, 0x51, 0x49, 0x46]),
                ('3', [0x21, 0x41, 0x45, 0x4B, 0x31]),
                ('4', [0x18, 0x14, 0x12, 0x7F, 0x10]),
                ('5', [0x27, 0x45, 0x45, 0x45, 0x39]),
                ('6', [0x3C, 0x4A, 0x49, 0x49, 0x30]),
                ('7', [0x01, 0x71, 0x09, 0x05, 0x03]),
                ('8', [0x36, 0x49, 0x49, 0x49, 0x36]),
                ('9', [0x06, 0x49, 0x49, 0x29, 0x1E]),
                ('A', [0x7E, 0x11, 0x11, 0x11, 0x7E]),
                ('B', [0x7F, 0x49, 0x49, 0x49, 0x36]),
                ('C', [0x3E, 0x41, 0x41, 0x41, 0x22]),
                ('D', [0x7F, 0x41, 0x41, 0x22, 0x1C]),
                ('E', [0x7F, 0x49, 0x49, 0x49, 0x41]),
                ('F', [0x7F, 0x09, 0x09, 0x09, 0x01]),
                ('G', [0x3E, 0x41, 0x49, 0x49, 0x7A]),
                ('H', [0x7F, 0x08, 0x08, 0x08, 0x7F]),
                ('I', [0x00, 0x41, 0x7F, 0x41, 0x00]),
                ('J', [0x20, 0x40, 0x41, 0x3F, 0x01]),
                ('K', [0x7F, 0x08, 0x14, 0x22, 0x41]),
                ('L', [0x7F, 0x40, 0x40, 0x40, 0x40]),
                ('M', [0x7F, 0x02, 0x0C, 0x02, 0x7F]),
                ('N', [0x7F, 0x04, 0x08, 0x10, 0x7F]),
                ('O', [0x3E, 0x41, 0x41, 0x41, 0x3E]),
                ('P', [0x7F, 0x09, 0x09, 0x09, 0x06]),
                ('Q', [0x3E, 0x41, 0x51, 0x21, 0x5E]),
                ('R', [0x7F, 0x09, 0x19, 0x29, 0x46]),
                ('S', [0x46, 0x49, 0x49, 0x49, 0x31]),
                ('T', [0x01, 0x01, 0x7F, 0x01, 0x01]),
                ('U', [0x3F, 0x40, 0x40, 0x40, 0x3F]),
                ('V', [0x1F, 0x20, 0x40, 0x20, 0x1F]),
                ('W', [0x3F, 0x40, 0x38, 0x40, 0x3F]),
                ('X', [0x63, 0x14, 0x08, 0x14, 0x63]),
                ('Y', [0x07, 0x08, 0x70, 0x08, 0x07]),
                ('Z', [0x61, 0x51, 0x49, 0x45, 0x43]),
                (' ', [0x00, 0x00, 0x00, 0x00, 0x00]),
                ('-', [0x08, 0x08, 0x08, 0x08, 0x08]),
                ('.', [0x00, 0x60, 0x60, 0x00, 0x00]),
                (':', [0x00, 0x36, 0x36, 0x00, 0x00]),
                ('/', [0x40, 0x30, 0x0C, 0x03, 0x00]),
                ('%', [0x43, 0x33, 0x08, 0x66, 0x61]),
            ]
        }

    def power_on(self):
        self._power_on = True

    def power_off(self):
        self._power_on = False

    def set_contrast(self, contrast: int):
        self._contrast = contrast & 0xFF

    def clear(self):
        for i in range(len(self._framebuffer)):
            self._framebuffer[i] = 0x00

    def draw_text(self, x: int, y: int, text: str):
        """Render text using a 5x7 bitmap font into the framebuffer."""
        page = y // 8
        for char in text:
            glyph = self._font_5x7.get(ord(char), [0x00] * 5)
            for col, bits in enumerate(glyph):
                px = x + col
                if 0 <= px < self.WIDTH:
                    idx = page * self.WIDTH + px
                    self._framebuffer[idx] |= bits
            x += 6
            if x >= self.WIDTH:
                break

    def render_ascii(self) -> str:
        """Render OLED framebuffer as Unicode block-based ASCII art."""
        lines = []
        for page in range(self.HEIGHT // 8):
            line = ''
            for x in range(self.WIDTH):
                byte_val = self._framebuffer[page * self.WIDTH + x]
                bits = bin(byte_val).count('1')
                if bits <= 1:
                    line += ' '
                elif bits <= 3:
                    line += '\u2591'
                elif bits <= 5:
                    line += '\u2592'
                else:
                    line += '\u2588'
            lines.append(line)
        return '\n'.join(lines)

    def summary(self) -> str:
        return f"[{self.name}] {self.WIDTH}x{self.HEIGHT} {'ON' if self._power_on else 'OFF'}"
