'''
credited to GOOGLE GEMINI, provided by SIMON GAUVREAU
used for study and occasional inspiration only.
'''

 
import time
import board
import displayio
import terminalio
import gc
import array
import struct
import math
 
# Gestion sécurisée des imports matériels
try:
    import microcontroller
except ImportError:
    microcontroller = None
 
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire
 
from adafruit_gc9a01a import GC9A01A
from adafruit_display_text.bitmap_label import Label
 
# =========================================
#   CONFIG SYSTEME & SECURITE
# =========================================
PARAM_ROTATION_ECRAN = 0
PARAM_CORRECTION_MIROIR = True
OFFSET_X_HARDWARE = 0
OFFSET_Y_HARDWARE = 0
 
# --- PROTECTION THERMIQUE ---
PARAM_PROTECTION_THERMIQUE = True
TEMP_SEUIL_DANGER = 65.0
FREQ_TURBO = 200_000_000
FREQ_NORMAL = 125_000_000
 
# Centre de l'écran (240x240)
SCREEN_CX = 120
SCREEN_CY = 120
 
# =========================
# INIT MATERIEL
# =========================
displayio.release_displays()
spi = board.SPI()
 
# --- GESTION CPU ROBUSTE ---
current_freq = "Inconnue"
cpu_control_available = False
 
if microcontroller and hasattr(microcontroller, "cpu"):
    try:
        microcontroller.cpu.frequency = FREQ_TURBO
        current_freq = f"{microcontroller.cpu.frequency / 1_000_000} MHz"
        cpu_control_available = True
    except (AttributeError, ValueError, Exception) as e:
        print(f"Info: Controle CPU non supporte ({e})")
else:
    print("Info: Execution sur Linux/OS (Pas d'acces direct CPU)")

print(f"Init CPU: {current_freq}")
print("Init SPI & Ecran...")
 
bus_spi = FourWire(spi, command=board.D25, chip_select=board.CE0, reset=board.D27, baudrate=62_500_000)
display = GC9A01A(bus_spi, width=240, height=240)
display.root_group = displayio.Group()
display.auto_refresh = False
 
# =========================
# GESTION THERMIQUE
# =========================
def lire_temperature():
    if cpu_control_available:
        try: return microcontroller.cpu.temperature
        except: pass
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return float(f.read()) / 1000.0
    except: pass
    return 25.0
 
def gerer_thermique(dernier_check_time):
    now = time.monotonic()
    if now - dernier_check_time < 2.0: return dernier_check_time
   
    temp = lire_temperature()
    if cpu_control_available:
        freq_actuelle = microcontroller.cpu.frequency
        if temp > TEMP_SEUIL_DANGER and freq_actuelle > FREQ_NORMAL:
            print(f"ALERTE SURCHAUFFE ({temp:.1f}C) -> Ralentissement CPU")
            try: microcontroller.cpu.frequency = FREQ_NORMAL
            except: pass
        elif temp < (TEMP_SEUIL_DANGER - 5.0) and freq_actuelle < FREQ_TURBO:
            print(f"Refroidissement OK ({temp:.1f}C) -> Retour Turbo")
            try: microcontroller.cpu.frequency = FREQ_TURBO
            except: pass
    else:
        if temp > TEMP_SEUIL_DANGER:
            print(f"ALERTE TEMP: {temp:.1f}C")
    return now
 
# =========================
# ROTATION MATERIELLE
# =========================
def force_hardware_rotation(angle):
    IS_BGR = 0x08
    madctl_val = 0xC0
    if angle == 0: madctl_val = 0xC0
    elif angle == 90: madctl_val = 0x60
    elif angle == 180: madctl_val = 0x00
    elif angle == 270: madctl_val = 0xA0
    if PARAM_CORRECTION_MIROIR: madctl_val ^= 0x40
    bus_spi.send(0x36, struct.pack("B", madctl_val | IS_BGR))
 
force_hardware_rotation(PARAM_ROTATION_ECRAN)
 
# =========================
# MOTEUR GRAPHIQUE
# =========================
def color_to_bytes(color_hex):
    r, g, b = (color_hex >> 16) & 0xFF, (color_hex >> 8) & 0xFF, color_hex & 0xFF
    val = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return struct.pack(">H", val)
 
COL_NOIR_BYTES = color_to_bytes(0x000000)
FILL_BUFFER_SIZE = 240 * 40 * 2
fill_buffer = bytearray(FILL_BUFFER_SIZE)
 
def blit_buffer(x, y, w, h, buffer_data):
    draw_x = x + OFFSET_X_HARDWARE
    draw_y = y + OFFSET_Y_HARDWARE
    if draw_x < 0: draw_x = 0
    if draw_y < 0: draw_y = 0
    x_end = draw_x + w - 1
    y_end = draw_y + h - 1
    bus_spi.send(0x2A, struct.pack(">HH", draw_x, x_end))
    bus_spi.send(0x2B, struct.pack(">HH", draw_y, y_end))
    bus_spi.send(0x2C, buffer_data)
 
def blit_solid_rect(x, y, w, h, color_bytes):
    if w <= 0 or h <= 0: return
    draw_x = x + OFFSET_X_HARDWARE
    draw_y = y + OFFSET_Y_HARDWARE
    needed_size = w * h * 2
    if needed_size > FILL_BUFFER_SIZE: needed_size = FILL_BUFFER_SIZE
    if fill_buffer[0] != color_bytes[0] or fill_buffer[1] != color_bytes[1]:
        fill_buffer[0:2] = color_bytes
        curr = 2
        while curr < needed_size:
            rem = needed_size - curr
            to_copy = curr if rem > curr else rem
            fill_buffer[curr:curr+to_copy] = fill_buffer[0:to_copy]
            curr += to_copy
    x_end = draw_x + w - 1
    y_end = draw_y + h - 1
    bus_spi.send(0x2A, struct.pack(">HH", draw_x, x_end))
    bus_spi.send(0x2B, struct.pack(">HH", draw_y, y_end))
    bus_spi.send(0x2C, fill_buffer[:needed_size])
 
def smart_update(obj, new_x_center, new_y_center):
    old_tl_x = obj.current_tl_x
    old_tl_y = obj.current_tl_y
    new_tl_x = int(SCREEN_CX + new_x_center - (obj.width // 2))
    new_tl_y = int(SCREEN_CY + new_y_center - (obj.height // 2))
   
    if old_tl_x == new_tl_x and old_tl_y == new_tl_y: return
 
    blit_buffer(new_tl_x, new_tl_y, obj.width, obj.height, obj.buffer)
   
    if new_tl_y > old_tl_y:
        blit_solid_rect(old_tl_x, old_tl_y, obj.width, new_tl_y - old_tl_y, COL_NOIR_BYTES)
    elif new_tl_y < old_tl_y:
        blit_solid_rect(old_tl_x, new_tl_y + obj.height, obj.width, old_tl_y - new_tl_y, COL_NOIR_BYTES)
    if new_tl_x > old_tl_x:
        blit_solid_rect(old_tl_x, old_tl_y, new_tl_x - old_tl_x, obj.height, COL_NOIR_BYTES)
    elif new_tl_x < old_tl_x:
        blit_solid_rect(new_tl_x + obj.width, old_tl_y, old_tl_x - new_tl_x, obj.height, COL_NOIR_BYTES)
 
    obj.current_tl_x = new_tl_x
    obj.current_tl_y = new_tl_y
    obj.x = new_x_center
    obj.y = new_y_center
 
def clear_screen():
    print("Reset Ecran...")
    bande = bytearray(240 * 20 * 2)
    for y in range(0, 240, 20): blit_buffer(0, y, 240, 20, bande)
    gc.collect()
 
# =========================
# CLASSES OBJETS & CACHE
# =========================
OBJETS_CACHE = {}
 
class ObjetGraphique:
    def __init__(self, x_center, y_center, width, height, buffer):
        self.width = width
        self.height = height
        self.buffer = buffer
        self.x = x_center
        self.y = y_center
        self.current_tl_x = int(SCREEN_CX + x_center - (width // 2))
        self.current_tl_y = int(SCREEN_CY + y_center - (height // 2))
 
# --- GENERATEURS AVEC CACHE ---
 
def DefinirTexte(nom, texte, scale, couleur_hex, x, y):
    # Si l'objet existe, on le déplace immédiatement à la position demandée
    if nom in OBJETS_CACHE:
        obj = OBJETS_CACHE[nom]
        smart_update(obj, x, y)
        return obj
   
    if "{temp}" in texte:
        t = lire_temperature()
        texte = texte.format(temp=f"{t:.0f}")
 
    lbl = Label(terminalio.FONT, text=texte, scale=scale)
    lbl.anchor_point = (0.5, 0.5)
    lbl.anchored_position = (0,0)
    w = lbl.bitmap.width * scale
    if w % 2 != 0: w += 1
    h = lbl.bitmap.height * scale
   
    buf = bytearray(w * h * 2)
    col_bytes = color_to_bytes(couleur_hex)
    ch, cl = col_bytes[0], col_bytes[1]
    bmp = lbl.bitmap
    for by in range(bmp.height):
        for bx in range(bmp.width):
            if bmp[bx, by]:
                tx, ty = bx*scale, by*scale
                for sy in range(scale):
                    for sx in range(scale):
                        if tx+sx < w:
                            i = ((ty+sy)*w + (tx+sx))*2
                            buf[i] = ch
                            buf[i+1] = cl
   
    obj = ObjetGraphique(x, y, w, h, buf)
    blit_buffer(obj.current_tl_x, obj.current_tl_y, w, h, buf) # Affichage init
    OBJETS_CACHE[nom] = obj
    del lbl
    gc.collect()
    return obj
 
def DefinirRect(nom, w, h, couleur_hex, x, y):
    if nom in OBJETS_CACHE:
        obj = OBJETS_CACHE[nom]
        smart_update(obj, x, y)
        return obj
 
    if w % 2 != 0: w += 1
    buf = bytearray(w * h * 2)
    chunk = color_to_bytes(couleur_hex) * w
    for i in range(h): buf[i*w*2 : (i+1)*w*2] = chunk
    obj = ObjetGraphique(x, y, w, h, buf)
    blit_buffer(obj.current_tl_x, obj.current_tl_y, w, h, buf)
    OBJETS_CACHE[nom] = obj
    return obj
 
def DefinirCercle(nom, rayon, couleur_hex, x, y):
    if nom in OBJETS_CACHE:
        obj = OBJETS_CACHE[nom]
        smart_update(obj, x, y)
        return obj
 
    diam = rayon * 2
    if diam % 2 != 0: diam += 1
    buf = bytearray(diam * diam * 2)
    col = color_to_bytes(couleur_hex)
    ch, cl = col[0], col[1]
    r_sq = rayon * rayon
    center_offset = diam / 2.0
    for py in range(diam):
        dy = (py + 0.5) - center_offset
        for px in range(diam):
            dx = (px + 0.5) - center_offset
            if (dx*dx + dy*dy) <= r_sq:
                i = (py * diam + px) * 2
                buf[i] = ch
                buf[i+1] = cl
    obj = ObjetGraphique(x, y, diam, diam, buf)
    blit_buffer(obj.current_tl_x, obj.current_tl_y, diam, diam, buf)
    OBJETS_CACHE[nom] = obj
    return obj
 
def DefinirTriangle(nom, base, hauteur, couleur_hex, x, y):
    if nom in OBJETS_CACHE:
        obj = OBJETS_CACHE[nom]
        smart_update(obj, x, y)
        return obj
 
    if base % 2 != 0: base += 1
    buf = bytearray(base * hauteur * 2)
    col = color_to_bytes(couleur_hex)
    ch, cl = col[0], col[1]
    half_base = base / 2.0
    slope = hauteur / half_base
    for py in range(hauteur):
        y_from_base = hauteur - py
        current_half_width = (y_from_base / slope)
        start_x = int(half_base - current_half_width)
        end_x = int(half_base + current_half_width)
        if start_x < 0: start_x = 0
        if end_x > base: end_x = base
        for px in range(start_x, end_x):
            i = (py * base + px) * 2
            buf[i] = ch
            buf[i+1] = cl
    obj = ObjetGraphique(x, y, base, hauteur, buf)
    blit_buffer(obj.current_tl_x, obj.current_tl_y, base, hauteur, buf)
    OBJETS_CACHE[nom] = obj
    return obj
 
# =========================
# MOTEUR D'ANIMATION
# =========================
def animer_objet(objet, cible_x, cible_y, duree_sec, lissage=1):
    start_x, start_y = objet.x, objet.y
    dist_x = cible_x - start_x
    dist_y = cible_y - start_y
    start_time = time.monotonic()
   
    if not hasattr(animer_objet, "last_check"): animer_objet.last_check = 0
   
    while True:
        now = time.monotonic()
        elapsed = now - start_time
        if PARAM_PROTECTION_THERMIQUE:
            animer_objet.last_check = gerer_thermique(animer_objet.last_check)
       
        if elapsed >= duree_sec: break
        p = elapsed / duree_sec
       
        if lissage == 1: p = -(math.cos(math.pi * p) - 1) / 2
        elif lissage == 2: p = p * p * (3 - 2 * p)
           
        smart_update(objet, int(start_x + dist_x * p), int(start_y + dist_y * p))
   
    smart_update(objet, cible_x, cible_y)
 
# =========================
# SCÉNARIO UTILISATEUR
# =========================
def run_scenario():
    clear_screen()
    print("Demarrage Scenario Simplifie...")
   
    while True:
        # === PHASE 1 ===
        # Syntaxe : animer_objet(DEFINITION, CIBLE_X, CIBLE_Y, TEMPS, LISSAGE)
        # Note: La "DEFINITION" ne crée l'objet que la première fois (Cache intelligent).
        # Les coordonnées X,Y dans la définition sont ignorées si l'objet existe déjà.
       
        animer_objet(DefinirCercle("mon_rond", 15, 0xFF00FF, 80, 50), 0, 10, 0.5, lissage=2)
        animer_objet(DefinirTriangle("mon_tri", 30, 30, 0xFFA500, 0, 50), 0, -20, 0.5, lissage=1)
        animer_objet(DefinirTexte("t_fps", "FPS", 3, 0x00FF00, 0, -80), 0, -60, 1.0, lissage=2)
        animer_objet(DefinirTexte("t_boost", "BOOST", 2, 0xFFFFFF, 0, -40), 0, -60, 1.0, lissage=2)
 
        time.sleep(0.5)
 
        # === PHASE 2 : EXPLOSION ===
        # Ici on réutilise les mêmes noms ("mon_rect", "mon_rond"), le système les retrouve tout seul.
       
        animer_objet(DefinirRect("mon_rect", 30, 30, 0x0000FF, -80, 50), -60, 60, 0.4, lissage=1)
        animer_objet(DefinirCercle("mon_rond", 15, 0xFF00FF, 80, 50), 60, 60, 0.4, lissage=1)
        animer_objet(DefinirTriangle("mon_tri", 30, 30, 0xFFA500, 0, 50), 0, 80, 0.4, lissage=1)
        animer_objet(DefinirTexte("t_fps", "FPS", 3, 0x00FF00, 0, -80), 0, -100, 0.6, lissage=2)
 
        time.sleep(0.5)
 
        # === PHASE 3 : RETOUR ===
        animer_objet(DefinirRect("mon_rect", 30, 30, 0x0000FF, -80, 50), -80, 50, 0.5, lissage=1)
        animer_objet(DefinirCercle("mon_rond", 15, 0xFF00FF, 80, 50), 80, 50, 0.5, lissage=1)
        animer_objet(DefinirTriangle("mon_tri", 30, 30, 0xFFA500, 0, 50), 0, 50, 0.5, lissage=1)
        animer_objet(DefinirTexte("t_fps", "FPS", 3, 0x00FF00, 0, -80), 0, -80, 0.5, lissage=2)
 
if __name__ == "__main__":
    try:
        run_scenario()
    except KeyboardInterrupt:
        pass
 