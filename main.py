#!/usr/bin/env python3
"""THE WORLD TODAY - Wednesday 25 November 2026.

A one-page newspaper front page summing up the world's news of
Wednesday 25 November 2026: 32 stories, 5 regions. Written from
scratch in this session with the Python standard library only: a
Canvas class that owns the pixels, a hand-drawn 5x7 bitmap font,
and a small PNG writer. No network, no clock, no randomness, so
every run writes the same bytes. Writes a 1024x1024 PNG.
"""

import binascii
import os
import struct
import sys
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (20, 20, 20)
RED = (163, 22, 33)
BLUE = (29, 78, 137)
GREY = (96, 92, 82)
PALE = (233, 228, 214)
SEA = (214, 226, 232)
LAND = (198, 206, 178)
COAST = (110, 118, 92)


class Canvas:
    """A flat RGB pixel buffer with newspaper drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.paint(0, 0, w, h, bg)

    def px(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = col[0]
            self.buf[i + 1] = col[1]
            self.buf[i + 2] = col[2]

    def paint(self, x, y, w, h, col):
        x0 = max(x, 0)
        x1 = min(x + w, self.w)
        for yy in range(max(y, 0), min(y + h, self.h)):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.buf[base] = col[0]
                self.buf[base + 1] = col[1]
                self.buf[base + 2] = col[2]
                base += 3

    def hbar(self, x, y, w, col, t=1):
        self.paint(x, y, w, t, col)

    def vbar(self, x, y, h, col, t=1):
        self.paint(x, y, t, h, col)

    def frame(self, x, y, w, h, col, t=1):
        self.hbar(x, y, w, col, t)
        self.hbar(x, y + h - t, w, col, t)
        self.vbar(x, y, h, col, t)
        self.vbar(x + w - t, y, h, col, t)

    def seg(self, x0, y0, x1, y1, col):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.px(x, y, col)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def dot(self, cx, cy, r, col):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.px(xx, yy, col)

    def fill_poly(self, pts, col):
        if len(pts) < 3:
            return
        top = min(p[1] for p in pts)
        bot = max(p[1] for p in pts)
        n = len(pts)
        for y in range(top, bot + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for xx in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.px(xx, y, col)

    def poly(self, pts, col):
        n = len(pts)
        for i in range(n):
            self.seg(pts[i][0], pts[i][1],
                     pts[(i + 1) % n][0], pts[(i + 1) % n][1], col)


# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, drawn by hand. '#' is ink, '.' is empty.
# All page text is set in capitals, newspaper style.

GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#..##", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", "..##.", "..##."),
    ",": (".....", ".....", ".....", ".....", "..##.", "..#..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    ";": (".....", "..##.", "..##.", ".....", "..##.", "..#..", ".#..."),
    ":": (".....", "..##.", "..##.", ".....", "..##.", "..##.", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "<": ("....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"),
    ">": ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
    "$": ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
}

# ------------------------------------------------------------ text out

def put_char(cv, x, y, ch, scale, col):
    rows = GLYPHS.get(ch, GLYPHS["A"])
    for r in range(7):
        row = rows[r]
        for c in range(5):
            if row[c] == "#":
                cv.paint(x + c * scale, y + r * scale, scale, scale, col)


def str_w(s, scale):
    return len(s) * 6 * scale


def put_text(cv, x, y, s, scale, col, bold=False):
    s = s.upper()
    cx = x
    for ch in s:
        put_char(cv, cx, y, ch, scale, col)
        if bold:
            put_char(cv, cx + max(1, scale // 2), y, ch, scale, col)
        cx += 6 * scale
    return cx


def put_center(cv, cx, y, s, scale, col, bold=False):
    put_text(cv, cx - str_w(s, scale) // 2, y, s, scale, col, bold)


def put_right(cv, rx, y, s, scale, col, bold=False):
    put_text(cv, rx - str_w(s, scale), y, s, scale, col, bold)


def split_lines(s, scale, maxw):
    words = s.upper().split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if str_w(trial, scale) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def put_block(cv, x, y, s, scale, maxw, col, max_lines=None, leading=None):
    if leading is None:
        leading = 7 * scale + 3
    lines = split_lines(s, scale, maxw)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        put_text(cv, x, y + i * leading, ln, scale, col)
    return y + len(lines) * leading


def put_block_center(cv, cx, y, s, scale, maxw, col, max_lines=None):
    lines = split_lines(s, scale, maxw)
    if max_lines is not None:
        lines = lines[:max_lines]
    leading = 7 * scale + 3
    for i, ln in enumerate(lines):
        put_center(cv, cx, y + i * leading, ln, scale, col)
    return y + len(lines) * leading


# ------------------------------------------------------------ png out

def _chunk(kind, data):
    crc = binascii.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3])
    comp = zlib.compress(bytes(raw), 9)
    head = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    out = b"\x89PNG\r\n\x1a\n"
    out += _chunk(b"IHDR", head)
    out += _chunk(b"IDAT", comp)
    out += _chunk(b"IEND", b"")
    return out


def write_png(cv, path):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "wb") as f:
        f.write(encode_png(cv))


# ------------------------------------------------------------ the news
# All 32 stories first reported Wednesday 25 November 2026 (see
# SOURCES.md). Three leads, sixteen briefs, thirteen also. Five
# regions: Europe 8, Middle East 9, Americas 8, Asia-Pacific 4,
# Africa 3.

LEADS = [
    (
        "UNITED STATES - TARIFFS",
        "US PROPOSES TARIFFS ON 14 ECONOMIES",
        "AFTER THE SUPREME COURT STRUCK DOWN EARLIER DUTIES, "
        "WASHINGTON PROPOSES NEW TARIFFS OF UP TO 20% ON 14 "
        "ECONOMIES, INCLUDING CHINA AND THE EU.",
    ),
    (
        "SAUDI ARABIA - REFINERY",
        "HOUTHIS CLAIM ATTACK ON RAS TANURA REFINERY",
        "YEMEN'S HOUTHIS CLAIM A STRIKE ON SAUDI ARABIA'S LARGEST "
        "REFINERY. SATELLITE IMAGES SHOW THICK BLACK SMOKE AROUND "
        "THE SITE.",
    ),
    (
        "ISRAEL - NETANYAHU TRIAL",
        "JUDGES: DROP NETANYAHU BRIBERY CASE",
        "ISRAELI JUDGES RECOMMEND PROSECUTORS DROP THE BRIBERY "
        "CASE AGAINST PM NETANYAHU AND RECONSIDER A SECOND CASE.",
    ),
]

NUMBERS = [
    ("30", "KILLED IN THE CAIRO RING-ROAD FUEL FIRE"),
    ("19", "KILLED IN RSF DRONE ATTACKS IN SUDAN"),
    ("490,334", "RUSSIAN SOLDIERS DEAD SINCE 2022 - LEAKED DATA"),
    ("14", "ECONOMIES FACE PROPOSED US TARIFFS"),
    ("115BN", "EUROS: UKRAINE'S FINANCING NEED FOR 2027"),
    ("+36%", "BANGLADESH GARMENT WAGE RISE"),
]

BRIEFS = [
    ("POLAND NO-FLY ZONE",
     "POLAND WILL SOON CREATE A NO-FLY ZONE NEAR ITS UKRAINIAN "
     "BORDER AFTER INCURSIONS IT BLAMES ON RUSSIA."),
    ("CAIRO FUEL FIRE",
     "A PETROLEUM VEHICLE OVERTURNS AND BURNS ON A RING ROAD; "
     "27 VEHICLES DESTROYED, 25 INJURED."),
    ("RSF DRONES KILL 19",
     "DRONE ATTACKS ON DAMAZIN AND ROSEIRES HIT HOMES, POWER "
     "FACILITIES AND A DAM IN BLUE NILE STATE."),
    ("HAMAS OFFICIAL KILLED",
     "ISRAELI STRIKE KILLS MUHAMMAD MAJID ABU AL-AWF, NORTHERN "
     "GAZA SECURITY CHIEF, WITH HIS FAMILY."),
    ("US: LEAVE IRAN NOW",
     "WASHINGTON TELLS US CITIZENS TO LEAVE IRAN AFTER ATTACKS "
     "ON US ASSETS IN BAHRAIN AND KUWAIT."),
    ("INDONESIA MINE FLOOD",
     "RESCUERS SEARCH FOR 26 TO 29 WORKERS TRAPPED IN A FLOODED "
     "GOLD MINE 100 METRES DEEP IN WEST JAVA."),
    ("CARTAGENA RESCUE",
     "COLOMBIAN FORCES STORM A SUPERMARKET, RESCUING ALL "
     "REMAINING HOSTAGES AND KILLING ONE CAPTOR."),
    ("BANGLADESH WAGE +36%",
     "GARMENT MINIMUM WAGE RISES TO 17,000 TAKAS AFTER WEEKS OF "
     "VIOLENT PROTESTS."),
    ("N. KOREA EXPELS SWISS",
     "PYONGYANG ORDERS SWITZERLAND TO SHUT ITS NEW OFFICE AND "
     "GIVES ITS HEAD 48 HOURS TO LEAVE."),
    ("UK WARNS OF SABOTAGE",
     "MI5 AND THE DEFENCE MINISTRY WARN FIRMS BACKING UKRAINE "
     "THEY MAY FACE RUSSIAN SABOTAGE."),
    ("2 LIBYANS DIE IN BENGHAZI",
     "TWO NAVAL OFFICERS DIE FROM WOUNDS AFTER A UKRAINIAN DRONE "
     "STRIKE ON A RUSSIAN WARSHIP."),
    ("COALITION HITS HODEIDAH",
     "SAUDI-LED COALITION SAYS IT STRUCK YEMEN'S HODEIDAH PORT "
     "AND TARGETS IN SAADA AND AMRAN."),
    ("6 DEAD IN PLANE CRASH",
     "A CESSNA 210 CRASHES INTO THE GULF OFF MISSISSIPPI; TWO "
     "BOYS AGED 8 AND 10 AMONG THE DEAD."),
    ("ARMY BLASTS LEAD AZIDE",
     "THE US ARMY DETONATES 4,400 KG OF LEAD AZIDE IN IOWA; "
     "RESIDENTS WITHIN 20 MILES SHELTER INDOORS."),
    ("CHINA PROBES CHEN JINING",
     "SHANGHAI PARTY CHIEF AND POLITBURO MEMBER INVESTIGATED; "
     "FOURTH TOP LEADER PROBED SINCE 2025."),
    ("UKRAINE NEEDS 115BN EUROS",
     "KYIV SAYS IT NEEDS 115 BILLION EUROS IN 2027; ABOUT 90 "
     "BILLION SECURED FROM THE EU."),
]

ALSO = [
    "20. LEAKED DATA: 490,334 RUSSIAN SOLDIERS DEAD SINCE 2022",
    "21. SAUDI ARABIA SHOOTS DOWN 7 HOUTHI DRONES",
    "22. HOUTHIS ADVANCE ON ADEN; RESIDENTS PREPARE TO FLEE",
    "23. IRAQ COURT: BAGHDAD CAN SEND TROOPS TO KURDISH BORDERS",
    "24. UN WARNS OF ATROCITY RISK BY ISRAEL IN PALESTINE",
    "25. UKRAINE STRIKES 2 RUSSIAN OIL REFINERIES",
    "26. RUSSIAN ATTACKS KILL 2 IN ODESA, INCLUDING TEENAGER",
    "27. UK RAF MOVES JETS TO HANGARS OVER DRONE THREAT",
    "28. US TO CAP INDIA TARIFF AT 17% IF DEAL IS REACHED",
    "29. US SHELVES RUSSIA BUSINESS DEALS TO END WAR",
    "30. FAA PROBE FINDS CULPRIT OF NATIONWIDE GROUND STOP",
    "31. SECOND JUDGE BLOCKS TRUMP BIRTHRIGHT ORDER",
    "32. EU 'STRONGLY' REJECTS PREMISE OF NEW US TARIFFS",
]

# Schematic continents inside the map box, rough polygons.
CONTINENTS = [
    [(60, 368), (150, 358), (240, 364), (255, 388), (210, 412),
     (170, 425), (120, 418), (75, 400)],
    [(230, 430), (275, 425), (295, 448), (272, 482), (248, 476),
     (230, 452)],
    [(258, 356), (280, 352), (288, 366), (268, 374)],
    [(478, 362), (540, 356), (560, 372), (540, 388), (500, 390),
     (480, 378)],
    [(560, 356), (700, 348), (780, 364), (762, 396), (700, 416),
     (640, 410), (585, 396), (555, 378)],
    [(700, 424), (728, 420), (732, 434), (706, 438)],
    [(735, 438), (756, 436), (758, 446), (738, 448)],
    [(700, 452), (752, 448), (766, 466), (730, 480), (700, 470)],
]

# (x, y, label, label dx, label dy) - places in the day's news.
DOTS = [
    (505, 360, "WARSAW", -30, -14),
    (478, 372, "LONDON", -56, -3),
    (545, 360, "KYIV", 8, -3),
    (545, 385, "ODESA", 8, -3),
    (548, 415, "CAIRO", -44, -3),
    (600, 405, "RIYADH", 8, -3),
    (605, 430, "ADEN", 8, -3),
    (560, 398, "GAZA", -40, -3),
    (585, 385, "BAGHDAD", -20, -14),
    (530, 448, "DAMAZIN", 8, -3),
    (700, 415, "JAKARTA", 8, -3),
    (670, 390, "DHAKA", 8, -3),
]

# ------------------------------------------------------------ layout
MARGIN = 28
RIGHT = 996


def section_head(cv, y, text, note=None):
    put_text(cv, MARGIN, y, text, 2, RED, bold=True)
    if note:
        put_right(cv, RIGHT, y + 3, note, 1, GREY)
    cv.hbar(MARGIN, y + 20, RIGHT - MARGIN, INK, 2)


def draw_masthead(cv):
    cv.paint(0, 0, W, 6, INK)
    put_center(cv, W // 2, 16, "THE WORLD TODAY", 7, INK)
    put_text(cv, MARGIN, 38, "VOL. II", 1, GREY)
    put_right(cv, RIGHT, 38, "WEDNESDAY EDITION", 1, GREY)
    cv.hbar(MARGIN, 74, RIGHT - MARGIN, INK, 3)
    cv.hbar(MARGIN, 79, RIGHT - MARGIN, RED, 1)
    put_text(cv, MARGIN, 88, "WEDNESDAY 25 NOVEMBER 2026", 2, INK, bold=True)
    put_right(cv, RIGHT, 88, "32 STORIES - 5 REGIONS", 2, INK, bold=True)
    cv.hbar(MARGIN, 108, RIGHT - MARGIN, INK, 1)


def draw_numbers(cv):
    y = 116
    box_w = 156
    gap = 6
    for i, (big, label) in enumerate(NUMBERS):
        x = MARGIN + i * (box_w + gap)
        cv.frame(x, y, box_w, 54, GREY, 1)
        put_center(cv, x + box_w // 2, y + 6, big, 2, RED, bold=True)
        put_block_center(cv, x + box_w // 2, y + 27, label, 1,
                         box_w - 10, GREY, max_lines=2)


def draw_leads(cv):
    section_head(cv, 178, "THE LEADS")
    xs = [28, 357, 686]
    for col, (kicker, head, body) in enumerate(LEADS):
        x = xs[col]
        put_text(cv, x, 206, kicker, 1, RED, bold=True)
        put_block(cv, x, 218, head, 2, 310, INK, max_lines=2, leading=17)
        put_block(cv, x, 256, body, 1, 310, INK, max_lines=5, leading=10)
    cv.vbar(347, 206, 100, PALE, 1)
    cv.vbar(676, 206, 100, PALE, 1)


def draw_map(cv):
    section_head(cv, 322, "WHERE IT HAPPENED", "SCHEMATIC MAP - NOT TO SCALE")
    cv.frame(MARGIN, 342, RIGHT - MARGIN, 146, INK, 1)
    cv.paint(MARGIN + 1, 343, RIGHT - MARGIN - 2, 144, SEA)
    for poly in CONTINENTS:
        cv.fill_poly(poly, LAND)
        cv.poly(poly, COAST)
    put_text(cv, 95, 392, "N. AMERICA", 1, GREY)
    put_text(cv, 228, 458, "S. AMERICA", 1, GREY)
    put_text(cv, 505, 435, "AFRICA", 1, GREY)
    put_text(cv, 640, 378, "ASIA", 1, GREY)
    put_text(cv, 700, 478, "AUSTRALIA", 1, GREY)
    for (dx, dy, label, lx, ly) in DOTS:
        cv.dot(dx, dy, 5, INK)
        cv.dot(dx, dy, 3, RED)
        put_text(cv, dx + lx, dy + ly, label, 1, INK, bold=True)


def draw_briefs(cv):
    section_head(cv, 496, "THE DAY IN BRIEF - 16 STORIES")
    xs = [28, 273, 518, 763]
    ys = [522, 592, 662, 732]
    for i, (head, body) in enumerate(BRIEFS):
        col = i % 4
        row = i // 4
        x = xs[col]
        y = ys[row]
        put_text(cv, x, y, "%02d" % (i + 4), 1, RED, bold=True)
        put_block(cv, x + 20, y, head, 1, 213, INK, max_lines=2, leading=10)
        put_block(cv, x, y + 22, body, 1, 233, INK, max_lines=3, leading=10)
    for vx in (261, 506, 751):
        cv.vbar(vx, 522, 276, PALE, 1)
    for hy in (588, 658, 728):
        cv.hbar(MARGIN, hy, RIGHT - MARGIN, PALE, 1)


def draw_also(cv):
    section_head(cv, 806, "ALSO ON WEDNESDAY 25 NOVEMBER")
    for i, item in enumerate(ALSO):
        col = i // 7
        row = i % 7
        x = MARGIN if col == 0 else 524
        put_text(cv, x, 832 + row * 19, item, 1, INK)


def draw_footer(cv):
    cv.hbar(MARGIN, 972, RIGHT - MARGIN, INK, 2)
    put_block(cv, MARGIN, 980,
              "DATE CHECK: THE BENGHAZI STRIKE WAS ON 24 NOVEMBER; "
              "THE TWO LIBYAN SOLDIERS' DEATHS WERE REPORTED ON "
              "25 NOVEMBER. THE HOUTHI ADVANCE ON ADEN WAS FIRST "
              "REPORTED AT 00:00 UTC ON 25 NOVEMBER.",
              1, RIGHT - MARGIN, INK, max_lines=2, leading=10)
    put_text(cv, MARGIN, 1002,
             "SOURCES: DAILY SUMMARY OF, REUTERS, CNN, BBC, "
             "THE GLOBAL EYE, THE KYIV INDEPENDENT - SEE SOURCES.MD",
             1, GREY)


def render():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_numbers(cv)
    draw_leads(cv)
    draw_map(cv)
    draw_briefs(cv)
    draw_also(cv)
    draw_footer(cv)
    return cv


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    write_png(render(), out)


if __name__ == "__main__":
    main()
