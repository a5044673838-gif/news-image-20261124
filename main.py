# World news of Tuesday 24 November 2026, drawn as one infographic image.
# Pure Python standard library: zlib + struct write a real PNG, no PIL,
# no network at runtime, fully deterministic (same bytes on every run).
# Writes /output/entry.png (MAKEFUN_OUTPUT_DIR overrides, ./output fallback).
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ------------------------------------------------------------
PAPER = (247, 245, 239)
INK = (16, 36, 62)
NAVY = (15, 42, 67)
GOLD = (232, 179, 60)
GREY = (90, 98, 110)
LINE = (214, 210, 200)
WHITE = (255, 255, 255)

# ---- 5x7 pixel font (uppercase poster style; '#' = on) -----------------
F = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ':': ("00000", "00100", "00000", "00000", "00000", "00100", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
}

# ---- the day's news, verified from at least two news sources each ------
# 1 Gaza: Reuters / Just Security. 2 NATO satellite: SCMP / BBC / The Statesman.
# 3 Grok lawsuits: SCMP / Manila Times. 4 Nvidia/Huang: The Statesman / SCMP.
# 5 Nepal quake: Tribune India / Times of India / USGS. 6 Myanmar: SCMP / Saudi Gazette.
STORIES = [
    ("GAZA", (180, 35, 24),
     "ISRAELI STRIKES KILL AT LEAST SIX IN GAZA",
     "DEAD INCLUDE TWO POLICE OFFICERS, MEDICS SAY"),
    ("SPACE", (29, 78, 137),
     "NATO WARNS RUSSIA OVER REPORTED NUCLEAR SATELLITE",
     "ALLIANCE VOWS TO DEFEND AGAINST SPACE THREATS"),
    ("TECH", (107, 63, 160),
     "US STATES SUE MUSK COMPANIES OVER GROK IMAGES",
     "VIRGINIA AND OREGON SUE OVER AI-MADE SEXUALISED IMAGES"),
    ("BUSINESS", (14, 124, 107),
     "NVIDIA REINSTATES HUANG AS CHIEF EXECUTIVE",
     "JENSEN HUANG RETURNS AFTER TRUMP INTERVENTION"),
    ("NEPAL", (180, 83, 9),
     "5.4 QUAKE SHAKES NEPAL AND NEIGHBOURS",
     "TREMORS FELT IN INDIA, BHUTAN, BANGLADESH AND CHINA"),
    ("MYANMAR", (47, 107, 47),
     "UK SANCTIONS MYANMAR LEADERS AFTER GENOCIDE RULING",
     "MOVE FOLLOWS UN COURT FINDING ON THE ROHINGYA"),
]


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * w * h)

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = yy * self.w * 3
            for xx in range(x0, x1):
                o = base + xx * 3
                self.px[o:o + 3] = bytes(color)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            g = F.get(ch, F[' '])
            for r in range(7):
                row = g[r]
                for c in range(5):
                    if row[c] == '1':
                        self.rect(cx + c * scale, y + r * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s.upper()) * 6 * scale - scale

    def wrap(self, s, scale, max_w):
        words, lines, cur = s.split(' '), [], ''
        for wd in words:
            trial = (cur + ' ' + wd).strip()
            if self.text_w(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def draw():
    cv = Canvas(W, H, PAPER)
    # banner
    cv.rect(0, 0, W, 148, NAVY)
    cv.rect(0, 148, W, 6, GOLD)
    cv.text(48, 26, "WORLD NEWS", 8, WHITE)
    cv.text(48, 96, "TUESDAY 24 NOVEMBER 2026", 4, GOLD)
    # stories
    y = 154
    row_h = 134
    for i, (tag, color, head, sub) in enumerate(STORIES):
        top = y + i * row_h
        # number chip
        cv.rect(48, top + 14, 84, 84, color)
        num = "%02d" % (i + 1)
        nx = 48 + (84 - cv.text_w(num, 5)) // 2
        cv.text(nx, top + 36, num, 5, WHITE)
        tx = 156
        cv.text(tx, top + 12, tag, 2, color)
        lines = cv.wrap(head, 4, W - tx - 48)
        ly = top + 34
        for ln in lines[:2]:
            cv.text(tx, ly, ln, 4, INK)
            ly += 34
        sub_lines = cv.wrap(sub, 2, W - tx - 48)
        cv.text(tx, ly + 4, sub_lines[0], 2, GREY)
        if i < len(STORIES) - 1:
            cv.rect(48, top + row_h - 1, W - 96, 1, LINE)
    # footer
    fy = 154 + 6 * row_h + 6
    cv.rect(0, fy, W, 2, GOLD)
    foot = "THE DAY IN WORLD NEWS - SOURCES: REUTERS, SCMP, BBC, USGS, AP"
    fx = (W - cv.text_w(foot, 2)) // 2
    cv.text(fx, fy + 16, foot, 2, GREY)
    return cv


def write_png(cv, path):
    raw = b''.join(b'\x00' + bytes(cv.px[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))

    def chunk(typ, data):
        c = struct.pack('>I', len(data)) + typ + data
        return c + struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(raw, 9))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "entry.png")
        with open(path, 'wb') as f:
            pass
    except OSError:
        out_dir = "output"
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "entry.png")
    size = write_png(draw(), path)
    print("wrote %s (%dx%d, %d bytes)" % (path, W, H, size))


if __name__ == "__main__":
    main()
