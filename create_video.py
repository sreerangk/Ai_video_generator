

import asyncio, json, os, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    from moviepy import AudioFileClip, CompositeVideoClip
    from moviepy.video.VideoClip import VideoClip
except ImportError:
    print("pip install moviepy Pillow numpy edge-tts"); sys.exit(1)
try:
    import edge_tts
except ImportError:
    print("pip install edge-tts"); sys.exit(1)

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
OUTPUT_FILE   = "output_final.mp4"
AUDIO_FILE    = "voiceover.mp3"
WORDS_FILE    = "word_timings.json"
VOICE         = "en-US-AndrewMultilingualNeural"
RATE          = "+0%"
W, H          = 1920, 1080
FPS           = 30
WORDS_PER_SUB = 5
FONT_SIZE     = 72
SUB_Y_FRAC    = 0.82

# ─────────────────────────────────────────────
#  SCRIPT
# ─────────────────────────────────────────────
SCRIPT = (
    "Okay so let me just be honest with you. "
    "Most people who want to get rich they are looking for the one thing. "
    "The one trick. The shortcut. And that is exactly why they stay broke. "
    "So I am gonna walk you through every real way people are actually making money in 2026. "
    "Not theory. Not motivation. Just what is actually working. "
    "Let us start with the obvious one a job. But not just any job. "
    "There are people making 80 90 a hundred thousand dollars a year doing cloud computing cybersecurity sales. "
    "You learn the skill you get paid for it. Simple. "
    "The problem is most people pick careers based on what sounds cool not what pays. "
    "Next freelancing. "
    "If you can edit videos run ads write emails that sell things or build websites companies will pay you. "
    "Not because you have a degree. Because you can do the thing they need done. "
    "I know a guy who learned video editing in four months. "
    "Now he makes six thousand dollars a month working from his apartment. "
    "That is it. No magic. "
    "Then there is starting a business. "
    "I am not talking about some big startup with investors. "
    "I mean a small boring business that solves one problem. "
    "Pressure washing. A bookkeeping service. A cleaning company. "
    "A good cleaning business in a mid size city can clear two hundred thousand dollars a year. "
    "Nobody talks about this because it is not glamorous. But it works. "
    "Content creation is real but people misunderstand it. "
    "You do not blow up and suddenly get rich. That is not how it works. "
    "You build an audience around something specific and then you sell them something. "
    "A course. A service. A product. A membership. "
    "The content is just how people find you. The money comes from what you are actually selling. "
    "Real estate. Look I know everyone says real estate. "
    "But the reason everyone says it is because it actually works over time. "
    "Buy a property. Rent it out. The tenant pays your mortgage. You build equity. "
    "It is slow. It is not exciting. But in ten years that property could be worth twice what you paid. "
    "Stock market. Index funds specifically. "
    "You put money in every single month you do not touch it and you let time do the work. "
    "This is not how you get rich fast. This is how you do not end up broke at sixty. "
    "Everyone should be doing this. Most people are not. "
    "Then there is buying websites or small businesses. "
    "This one flies under the radar. "
    "People sell websites that already make money five hundred dollars a month a thousand dollars a month. "
    "You buy it you run it you improve it you sell it for more. "
    "Crypto. I will keep this short. "
    "Some people made a lot of money. Some people lost everything. "
    "If you do not understand what you are buying you are not investing you are gambling. "
    "Learn it properly or stay out. "
    "And then there is sales. "
    "Honestly one of the most underrated ways to make real money. "
    "Commission based sales real estate software insurance cars. "
    "If you are good at it there is no ceiling on what you can earn. "
    "The best salespeople at tech companies make more than the engineers. "
    "Here is the thing nobody tells you though. "
    "It is not really about which path you pick. "
    "It is about how long you stick with it. "
    "Most people switch every six months because they are not seeing results fast enough. "
    "But the people who actually get rich picked something and stayed with it for years. "
    "That is the whole thing. That is actually it. "
    "Pick one. Go deep. Do not quit when it gets boring."
)
 
SECTIONS = [
    {
        "keyword": "~start",
        "title": "EVERY WAY TO\nGET RICH IN 2026",
        "sub": "",
        "colors": [(8, 8, 18), (25, 15, 55)],
        "accent": (200, 255, 0),
        "anim": "zoom_punch",
        "stat": None,
    },
    {
        "keyword": "job",
        "title": "HIGH-INCOME\nSKILLS",
        "sub": "Cloud · Cybersecurity · Sales",
        "colors": [(4, 16, 36), (8, 40, 80)],
        "accent": (0, 180, 255),
        "anim": "slide_left",
        "stat": "$100K/yr",
    },
    {
        "keyword": "freelancing",
        "title": "FREELANCING",
        "sub": "$6,000/mo from your apartment",
        "colors": [(18, 8, 36), (50, 15, 70)],
        "accent": (220, 80, 255),
        "anim": "slide_up",
        "stat": "$6K/mo",
    },
    {
        "keyword": "business",
        "title": "SMALL BORING\nBUSINESSES",
        "sub": "Not glamorous. But it works.",
        "colors": [(28, 12, 4), (70, 35, 8)],
        "accent": (255, 160, 0),
        "anim": "zoom_punch",
        "stat": "$200K/yr",
    },
    {
        "keyword": "misunderstand",
        "title": "CONTENT\nCREATION",
        "sub": "Build audience. Then sell.",
        "colors": [(4, 26, 16), (8, 60, 40)],
        "accent": (0, 230, 130),
        "anim": "slide_left",
        "stat": None,
    },
    {
        "keyword": "estate",
        "title": "REAL ESTATE",
        "sub": "Tenant pays mortgage. You own it.",
        "colors": [(22, 8, 8), (65, 18, 18)],
        "accent": (255, 70, 70),
        "anim": "slide_up",
        "stat": "2× value",
    },
    {
        "keyword": "specifically",
        "title": "INDEX FUNDS",
        "sub": "Put in monthly. Don't touch. Wait.",
        "colors": [(8, 22, 8), (16, 55, 26)],
        "accent": (60, 255, 100),
        "anim": "zoom_punch",
        "stat": "30yr avg +10%",
    },
    {
        "keyword": "radar",
        "title": "BUYING\nWEBSITES",
        "sub": "Buy. Improve. Sell for more.",
        "colors": [(8, 18, 28), (16, 45, 65)],
        "accent": (0, 200, 230),
        "anim": "slide_left",
        "stat": "3× revenue",
    },
    {
        "keyword": "crypto",
        "title": "CRYPTO",
        "sub": "Not investing — gambling. Learn first.",
        "colors": [(18, 18, 4), (55, 50, 8)],
        "accent": (255, 210, 0),
        "anim": "glitch",
        "stat": "⚠ HIGH RISK",
    },
    {
        "keyword": "underrated",
        "title": "SALES",
        "sub": "No ceiling. No limit.",
        "colors": [(28, 4, 18), (75, 8, 45)],
        "accent": (255, 50, 140),
        "anim": "slide_up",
        "stat": "∞ ceiling",
    },
    {
        "keyword": "nobody",
        "title": "THE REAL\nSECRET",
        "sub": "Pick one. Go deep. Don't quit.",
        "colors": [(8, 8, 18), (25, 15, 55)],
        "accent": (200, 255, 0),
        "anim": "zoom_punch",
        "stat": None,
    },
]

def ease_out_expo(t):
    return 1 - math.pow(2, -10 * t) if t < 1 else 1.0

def ease_out_back(t, s=1.5):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1

def ease_out_elastic(t):
    if t == 0 or t == 1: return t
    return math.pow(2, -10*t) * math.sin((t*10 - 0.75) * (2*math.pi) / 3) + 1

def ease_in_out(t):
    return t * t * (3 - 2 * t)

_fonts = {}
def get_font(size):
    if size in _fonts: return _fonts[size]
    paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                f = ImageFont.truetype(p, size)
                _fonts[size] = f
                return f
            except: pass
    f = ImageFont.load_default()
    _fonts[size] = f
    return f

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * max(0, min(1, t))) for i in range(3))

def alpha_blend(base, overlay_rgba, alpha_mult=1.0):
    r, g, b, a = overlay_rgba
    a = int(a * alpha_mult)
    base_arr = np.array(base, dtype=np.float32)
    ov = np.array([r, g, b], dtype=np.float32)
    t  = a / 255.0
    result = base_arr * (1 - t) + ov * t
    return Image.fromarray(result.astype(np.uint8))

random.seed(42)

class Particle:
    def __init__(self, accent):
        self.x     = random.uniform(0, W)
        self.y     = random.uniform(0, H)
        self.vx    = random.uniform(-0.4, 0.4)
        self.vy    = random.uniform(-0.8, -0.2)
        self.size  = random.uniform(1.5, 4.5)
        self.alpha = random.uniform(80, 200)
        self.color = accent

def draw_particles(draw, particles, t):
    for p in particles:
        x = (p.x + p.vx * t * 60) % W
        y = (p.y + p.vy * t * 60) % H
        a = int(p.alpha * (0.5 + 0.5 * math.sin(t * 2 + p.x)))
        r = int(p.size)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=p.color + (a,))

def add_scanlines(img, alpha=18):
    ov = Image.new("RGBA", (W, H), (0,0,0,0))
    d  = ImageDraw.Draw(ov)
    for y in range(0, H, 4):
        d.line([(0,y),(W,y)], fill=(0,0,0,alpha))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

_vignette_cache = None
def get_vignette():
    global _vignette_cache
    if _vignette_cache is not None:
        return _vignette_cache
    vig = np.zeros((H, W, 4), dtype=np.uint8)
    cx, cy = W/2, H/2
    max_d  = math.sqrt(cx**2 + cy**2)
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            d = math.sqrt((x-cx)**2 + (y-cy)**2) / max_d
            a = int(min(255, d**2 * 220))
            vig[y:y+2, x:x+2] = [0, 0, 0, a]
    _vignette_cache = Image.fromarray(vig, "RGBA")
    return _vignette_cache

def make_gradient(c1, c2):
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / H
        arr[y] = lerp(c1, c2, t)
    return arr

def draw_text_centered(draw, text, y, font, color, shadow=True, shadow_col=(0,0,0,180)):
    bb = draw.textbbox((0,0), text, font=font)
    tw = bb[2] - bb[0]
    tx = (W - tw) // 2
    if shadow:
        for ox, oy in [(4,4),(-2,2),(2,-2)]:
            draw.text((tx+ox, y+oy), text, font=font, fill=shadow_col)
    draw.text((tx, y), text, font=font, fill=color)
    return tw

def draw_glowing_text(img, text, y, font, color, glow_radius=8):
    # Draw text on temp image, then blur for glow
    tmp  = Image.new("RGBA", (W, H), (0,0,0,0))
    td   = ImageDraw.Draw(tmp)
    bb   = td.textbbox((0,0), text, font=font)
    tw   = bb[2] - bb[0]
    tx   = (W - tw) // 2
    gc   = color + (120,)
    td.text((tx, y), text, font=font, fill=gc)
    glow = tmp.filter(ImageFilter.GaussianBlur(glow_radius))
    img  = Image.alpha_composite(img.convert("RGBA"), glow)
    d    = ImageDraw.Draw(img)
    d.text((tx, y), text, font=font, fill=color + (255,))
    return img.convert("RGB")

def make_section_frame(t, dur, sec, particles):
    """
    t   = time within this section (0 → dur)
    Returns numpy RGB array (H, W, 3)
    """
    progress  = t / dur if dur > 0 else 1.0
    anim      = sec.get("anim", "zoom_punch")
    accent    = sec["accent"]
    c1, c2    = sec["colors"]
    title     = sec["title"]
    sub_text  = sec.get("sub", "")
    stat_text = sec.get("stat", None)

    # ── Base gradient ─────────────────────────
    # Slowly shift gradient over time
    shift   = math.sin(t * 0.3) * 0.12
    bg_arr  = make_gradient(
        lerp(c1, lerp(c1, c2, 0.3), shift + 0.5),
        lerp(c2, lerp(c1, c2, 0.7), shift + 0.5),
    )
    img = Image.fromarray(bg_arr)

    # ── Particle layer ────────────────────────
    part_ov = Image.new("RGBA", (W, H), (0,0,0,0))
    pd      = ImageDraw.Draw(part_ov)
    draw_particles(pd, particles, t)
    img = Image.alpha_composite(img.convert("RGBA"), part_ov).convert("RGB")

    # ── Moving background grid ────────────────
    grid_ov = Image.new("RGBA", (W, H), (0,0,0,0))
    gd      = ImageDraw.Draw(grid_ov)
    grid_col = accent + (12,)
    offset   = int(t * 20) % 80
    for x in range(-80, W+80, 80):
        gd.line([(x+offset, 0), (x+offset, H)], fill=grid_col, width=1)
    for y in range(-80, H+80, 80):
        yo = int(t * 12) % 80
        gd.line([(0, y+yo), (W, y+yo)], fill=grid_col, width=1)
    img = Image.alpha_composite(img.convert("RGBA"), grid_ov).convert("RGB")

    # ── Vignette ──────────────────────────────
    vig = get_vignette()
    img = Image.alpha_composite(img.convert("RGBA"), vig).convert("RGB")

    # ── Animated accent bar (top) ─────────────
    bar_w = int(W * min(1.0, t * 3))
    bar_img = Image.new("RGBA", (W, H), (0,0,0,0))
    bd      = ImageDraw.Draw(bar_img)
    bd.rectangle([0, 0, bar_w, 5], fill=accent + (255,))
    img = Image.alpha_composite(img.convert("RGBA"), bar_img).convert("RGB")

    draw = ImageDraw.Draw(img)

    # ── ANIMATION TYPE ────────────────────────
    title_lines = title.split("\n")
    tf  = get_font(120)
    sf  = get_font(46)
    smf = get_font(30)

    if anim == "zoom_punch":
        # Title scales from 200% to 100% with bounce
        if t < 0.5:
            scale_t = ease_out_back(t * 2)
            alpha_t = min(1.0, t * 6)
        else:
            scale_t = 1.0
            alpha_t = 1.0

        title_y_center = H // 2 - len(title_lines) * 70
        for li, line in enumerate(title_lines):
            bb  = draw.textbbox((0,0), line, font=tf)
            tw  = bb[2] - bb[0]
            th  = bb[3] - bb[1]
            tx  = (W - tw) // 2
            ty  = title_y_center + li * 140

            # Scale around center
            scaled_size = int(120 * (0.4 + 0.6 * scale_t))
            sf2 = get_font(scaled_size)
            bb2 = draw.textbbox((0,0), line, font=sf2)
            tw2 = bb2[2] - bb2[0]
            tx2 = (W - tw2) // 2

            a   = int(alpha_t * 255)
            # Glow passes
            for gx, gy in [(0,0),(3,3),(-3,-3),(0,3)]:
                draw.text((tx2+gx, ty+gy), line, font=sf2,
                          fill=(accent[0]//3, accent[1]//3, accent[2]//3, a//3))
            draw.text((tx2, ty), line, font=sf2, fill=accent + (a,))

    elif anim == "slide_left":
        # Each word slides in from right with stagger
        title_y_center = H // 2 - len(title_lines) * 70
        for li, line in enumerate(title_lines):
            stagger  = li * 0.12
            local_t  = max(0, t - stagger)
            slide_t  = ease_out_expo(min(1.0, local_t * 3))
            start_x  = W + 200
            bb       = draw.textbbox((0,0), line, font=tf)
            tw       = bb[2] - bb[0]
            tx_final = (W - tw) // 2
            tx       = int(start_x + (tx_final - start_x) * slide_t)
            ty       = title_y_center + li * 140
            a        = int(min(1.0, local_t * 4) * 255)
            for gx, gy in [(3,3),(-2,2)]:
                draw.text((tx+gx, ty+gy), line, font=tf,
                          fill=(accent[0]//4, accent[1]//4, accent[2]//4, a//3))
            draw.text((tx, ty), line, font=tf, fill=accent + (a,))

    elif anim == "slide_up":
        # Title slides up from below
        title_y_center = H // 2 - len(title_lines) * 70
        for li, line in enumerate(title_lines):
            stagger  = li * 0.1
            local_t  = max(0, t - stagger)
            slide_t  = ease_out_back(min(1.0, local_t * 2.5))
            start_y  = H + 100
            ty_final = title_y_center + li * 140
            ty       = int(start_y + (ty_final - start_y) * slide_t)
            bb       = draw.textbbox((0,0), line, font=tf)
            tw       = bb[2] - bb[0]
            tx       = (W - tw) // 2
            a        = int(min(1.0, local_t * 5) * 255)
            draw.text((tx+3, ty+3), line, font=tf,
                      fill=(accent[0]//4, accent[1]//4, accent[2]//4, a//3))
            draw.text((tx, ty), line, font=tf, fill=accent + (a,))

    elif anim == "glitch":
        # Glitch effect: random horizontal shifts + color splits
        title_y_center = H // 2 - len(title_lines) * 70
        for li, line in enumerate(title_lines):
            bb  = draw.textbbox((0,0), line, font=tf)
            tw  = bb[2] - bb[0]
            tx  = (W - tw) // 2
            ty  = title_y_center + li * 140

            # RGB split
            glitch_strength = int(12 * (0.5 + 0.5 * math.sin(t * 15)))
            draw.text((tx - glitch_strength, ty), line, font=tf,
                      fill=(255, 0, 0, 120))
            draw.text((tx + glitch_strength, ty), line, font=tf,
                      fill=(0, 255, 255, 120))
            # Random horizontal noise bars
            if random.random() < 0.3:
                noise_y = random.randint(ty, ty+120)
                noise_x = tx + random.randint(-20, 20)
                draw.text((noise_x, noise_y), line, font=tf,
                          fill=accent + (80,))
            draw.text((tx, ty), line, font=tf, fill=accent + (255,))

    # ── Accent divider line (animated width) ──
    div_progress = ease_out_expo(min(1.0, max(0, t - 0.3) * 4))
    div_w        = int(180 * div_progress)
    title_bottom = H // 2 - len(title_lines) * 70 + len(title_lines) * 140 + 10
    draw.rectangle([W//2 - div_w//2, title_bottom,
                    W//2 + div_w//2, title_bottom + 5],
                   fill=accent)

    # ── Subtitle (fade in) ────────────────────
    sub_alpha = int(min(1.0, max(0, t - 0.4) * 3) * 220)
    if sub_alpha > 0:
        bb = draw.textbbox((0,0), sub_text, font=sf)
        sw = bb[2] - bb[0]
        draw.text(((W-sw)//2, title_bottom + 28), sub_text,
                  font=sf, fill=(200, 200, 200, sub_alpha))

    # ── Stat badge (bounces in) ───────────────
    if stat_text and t > 0.6:
        stat_t     = ease_out_elastic(min(1.0, (t - 0.6) * 4))
        badge_w    = 320
        badge_h    = 90
        badge_x    = W - badge_w - 60
        badge_y_f  = 60
        badge_y    = int(H + (badge_y_f - H) * stat_t)

        badge_ov = Image.new("RGBA", (W, H), (0,0,0,0))
        bvd      = ImageDraw.Draw(badge_ov)
        bvd.rounded_rectangle(
            [badge_x, badge_y, badge_x+badge_w, badge_y+badge_h],
            radius=12, fill=accent+(230,)
        )
        img = Image.alpha_composite(img.convert("RGBA"), badge_ov).convert("RGB")
        draw = ImageDraw.Draw(img)
        stf  = get_font(44)
        sbb  = draw.textbbox((0,0), stat_text, font=stf)
        stw  = sbb[2] - sbb[0]
        draw.text(
            (badge_x + (badge_w-stw)//2, badge_y + 18),
            stat_text, font=stf, fill=(0, 0, 0)
        )

    pulse = 0.5 + 0.5 * math.sin(t * 3)
    r     = int(8 + 4 * pulse)
    for cx2, cy2 in [(30, 30), (W-30, 30), (30, H-30), (W-30, H-30)]:
        draw.ellipse([cx2-r, cy2-r, cx2+r, cy2+r],
                     fill=accent + (int(180*pulse),))
    scan_ov = Image.new("RGBA", (W, H), (0,0,0,0))
    sd      = ImageDraw.Draw(scan_ov)
    for y in range(0, H, 4):
        sd.line([(0,y),(W,y)], fill=(0,0,0,20))
    img = Image.alpha_composite(img.convert("RGBA"), scan_ov).convert("RGB")

    # Brief white flash at section start
    flash_alpha = int(max(0, (0.08 - t) / 0.08) * 180) if t < 0.08 else 0
    if flash_alpha > 0:
        fl = Image.new("RGBA", (W,H), (255,255,255,flash_alpha))
        img = Image.alpha_composite(img.convert("RGBA"), fl).convert("RGB")

    return np.array(img)


def render_subtitle(chunk, current_time):
    words  = [w["word"] for w in chunk["words"]]
    active = 0
    for wi, w in enumerate(chunk["words"]):
        if w["start"] <= current_time: active = wi

    font = get_font(FONT_SIZE)
    GAP, PX, PY = 22, 44, 24
    tmp  = ImageDraw.Draw(Image.new("RGBA",(1,1)))
    sizes = [tmp.textbbox((0,0),w,font=font) for w in words]
    wws   = [s[2]-s[0] for s in sizes]
    whs   = [s[3]-s[1] for s in sizes]
    max_h = max(whs) if whs else FONT_SIZE
    tot_w = sum(wws) + GAP*(len(words)-1)

    SH   = 170
    img  = Image.new("RGBA",(W,SH),(0,0,0,0))
    cx, cy = W//2, SH//2

    box = Image.new("RGBA",(W,SH),(0,0,0,0))
    bd  = ImageDraw.Draw(box)
    bd.rounded_rectangle(
        [cx-tot_w//2-PX, cy-max_h//2-PY,
         cx+tot_w//2+PX, cy+max_h//2+PY],
        radius=16, fill=(0,0,0,175)
    )
    img  = Image.alpha_composite(img,box)
    draw = ImageDraw.Draw(img)

    x = cx - tot_w//2
    y = cy - max_h//2
    for wi,(word,ww) in enumerate(zip(words,wws)):
        col = (200,255,0,255) if wi==active else (255,255,255,255)
        draw.text((x+2,y+2),word,font=font,fill=(0,0,0,200))
        draw.text((x,y),word,font=font,fill=col)
        x += ww+GAP

    return np.array(img)[:,:,:3]


async def generate_audio():
    print("\n[1/4] Generating voiceover...")
    comm = edge_tts.Communicate(text=SCRIPT, voice=VOICE, rate=RATE)
    timings = []
    with open(AUDIO_FILE,"wb") as f:
        async for chunk in comm.stream():
            if chunk["type"]=="audio": f.write(chunk["data"])
            elif chunk["type"]=="WordBoundary":
                timings.append({
                    "word":     chunk["text"],
                    "start":    chunk["offset"]/10_000_000,
                    "duration": chunk["duration"]/10_000_000,
                })
    with open(WORDS_FILE,"w") as f: json.dump(timings,f,indent=2)
    mb = os.path.getsize(AUDIO_FILE)/(1024*1024)
    print(f"    ✓ {AUDIO_FILE} ({mb:.2f}MB) | {len(timings)} words")
    return timings

def build_chunks(timings):
    print("\n[2/4] Building subtitle chunks...")
    chunks, n = [], WORDS_PER_SUB
    for i in range(0,len(timings),n):
        g = timings[i:i+n]
        chunks.append({
            "start": g[0]["start"],
            "end":   g[-1]["start"]+g[-1]["duration"],
            "words": [{"word":w["word"],"start":w["start"],
                       "end":w["start"]+w["duration"]} for w in g],
        })
    print(f"    ✓ {len(chunks)} subtitle chunks")
    return chunks

def resolve_sections(timings, audio_dur):
    print("\n[3/4] Resolving section timestamps...")
    def find_kw(kw):
        for t in timings:
            if kw.lower() in t["word"].lower():
                return t["start"]
        print(f"    ⚠ '{kw}' not found, skipping")
        return None

    resolved = []
    for sec in SECTIONS:
        kw = sec["keyword"]
        ts = 0.0 if kw == "~start" else find_kw(kw)
        if ts is None: continue
        resolved.append((ts, sec))
    resolved.sort(key=lambda x: x[0])

    result = []
    for i,(start,sec) in enumerate(resolved):
        end = resolved[i+1][0] if i+1<len(resolved) else audio_dur
        if end<=start: end = start+2.0
        result.append((start, end, sec))
        print(f"    [{i+1:02d}] {sec['title'].split(chr(10))[0]:<22}  {start:.1f}s → {end:.1f}s")
    return result

def compose(section_times, chunks, audio_dur):
    audio  = AudioFileClip(AUDIO_FILE)
    sub_y  = int(H * SUB_Y_FRAC)

    all_clips = []

    # Background + animation clips
    for start, end, sec in section_times:
        dur       = max(end - start, 0.1)
        particles = [Particle(sec["accent"]) for _ in range(55)]

        def make_frame(t, s=sec, d=dur, ps=particles):
            return make_section_frame(t, d, s, ps)

        clip = (
            VideoClip(make_frame, duration=dur)
            .with_start(start)
        )
        all_clips.append(clip)

    # Subtitle clips
    for chunk in chunks:
        cs  = chunk["start"]
        dur = max(chunk["end"]-cs, 0.05)
        def make_sub(t, ch=chunk, c=cs):
            return render_subtitle(ch, c+t)
        clip = (
            VideoClip(make_sub, duration=dur)
            .with_start(cs)
            .with_position(("center", sub_y))
        )
        all_clips.append(clip)

    print(f"\nExporting → {OUTPUT_FILE}  (takes a few minutes...)\n")
    final = (
        CompositeVideoClip(all_clips, size=(W,H))
        .with_duration(audio_dur)
        .with_audio(audio)
    )
    final.write_videofile(
        OUTPUT_FILE, fps=FPS,
        codec="libx264", audio_codec="aac",
        preset="fast", ffmpeg_params=["-crf","20"],
        threads=4, logger="bar",
    )
    print(f"\n✅  Done!  →  {OUTPUT_FILE}")

async def main():
    print("="*55)
    print("  ANIMATED VIDEO CREATOR  —  YouTube 16:9")
    print("="*55)

    # Audio
    if os.path.exists(AUDIO_FILE) and os.path.exists(WORDS_FILE):
        with open(WORDS_FILE) as f: timings = json.load(f)
        if len(timings)==0:
            print("\n[1/4] Timings empty — regenerating...")
            os.remove(AUDIO_FILE); os.remove(WORDS_FILE)
            timings = await generate_audio()
        else:
            print(f"\n[1/4] Using existing audio ({len(timings)} words)")
    else:
        timings = await generate_audio()

    audio_dur = AudioFileClip(AUDIO_FILE).duration
    print(f"    Duration: {audio_dur:.1f}s")

    chunks        = build_chunks(timings)
    section_times = resolve_sections(timings, audio_dur)
    compose(section_times, chunks, audio_dur)

if __name__ == "__main__":
    asyncio.run(main())