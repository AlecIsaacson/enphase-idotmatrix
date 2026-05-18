from PIL import Image, ImageDraw
from collections import deque

# ── Display constants ────────────────────────────────────────────────────────
W, H          = 64, 64
BAR_H         = 12      # height per bar row — fits size-10 font + 1px padding each side
BAR_ROWS      = 3       # CPU / RAM / chosen filesystem
GAP           = 2       # gap between rows
SPARK_Y       = BAR_ROWS * (BAR_H + GAP) + 2   # = 3*(12+2)+2 = 44
SPARK_H       = H - SPARK_Y - 1                # = 19

# Grafana-ish palette
BG            = (12, 12, 22)
TRACK         = (35, 35, 55)
LABEL_C       = (130, 130, 160)
VALUE_C       = (220, 220, 220)
DIVIDER_C     = (45, 45, 70)
SPARK_C       = (80, 160, 255)
GREEN         = (70, 210, 70)
YELLOW        = (240, 190, 0)
RED           = (220, 55, 55)
ORANGE        = (255, 140, 0)

def bar_color(pct: float) -> tuple:
    if pct < 60:   return GREEN
    if pct < 80:   return YELLOW
    if pct < 92:   return ORANGE
    return RED

def get_font():
    """
    Return the best available tiny font.
    PIL's ImageFont.load_default(size=8) needs Pillow >= 10.
    Fall back to the classic 1-arg default (5x8 bitmap) on older builds.
    """
    from PIL import ImageFont
    try:
        # return ImageFont.load_default(size=9)
        return ImageFont.truetype('../PixelOperatorMono.ttf', size=12)
    except TypeError:
        return ImageFont.load_default()


def text_w(draw, text, font):
    """Width of a string in pixels (works for both old and new Pillow)."""
    try:
        return draw.textlength(text, font=font)
    except AttributeError:
        return len(text) * 6   # fallback for very old Pillow

def draw_bar_row(draw: ImageDraw.ImageDraw, font,
                 y: int, label: str, pct: float, right_text: str):
    filled = max(0, int(pct / 100 * (W - 2)))
    color  = bar_color(pct)

    # Track (full width background)
    draw.rectangle([(1, y), (W - 2, y + BAR_H - 1)], fill=TRACK)

    # Filled bar — use full color, text zones will be darkened separately
    if filled > 0:
        draw.rectangle([(1, y), (1 + filled - 1, y + BAR_H - 1)], fill=color)

    # Dark "label zone" on left so text is always readable regardless of fill
    draw.rectangle([(1, y), (22, y + BAR_H - 1)], fill=(20, 20, 40))
    # Dark "value zone" on right
    rw = int(text_w(draw, right_text, font))
    draw.rectangle([(W - rw - 4, y), (W - 2, y + BAR_H - 1)], fill=(20, 20, 40))

    # Text on top
    draw.text((3, y + 2), label, font=font, fill=VALUE_C)
    draw.text((W - rw - 3, y + 2), right_text, font=font, fill=VALUE_C)

def draw_sparkline(draw: ImageDraw.ImageDraw, history: deque):
    if len(history) < 2:
        return
    vals = list(history)
    n    = len(vals)
    hi   = max(vals) or 1
    lo   = min(vals)
    span = hi - lo if hi != lo else 1.0

    bot = H - 2
    pts = []
    for i, v in enumerate(vals):
        x = int(i * (W - 1) / (n - 1))
        y = bot - int((v - lo) / span * (SPARK_H - 3))
        pts.append((x, y))

    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=SPARK_C, width=1)

    # Highlight latest point
    draw.rectangle([pts[-1][0]-1, pts[-1][1]-1,
                    pts[-1][0]+1, pts[-1][1]+1], fill=VALUE_C)

def render_frame(m: dict, cpu_history: deque) -> Image.Image:
	print('In render_frame')
	img	 = Image.new("RGB", (W, H), BG)
	draw = ImageDraw.Draw(img)
	font = get_font()
	print('Fontmode: ' + draw.fontmode)
	draw.fontmode = '1'
	print('Fontmode: ' + draw.fontmode)

	# Mountpoint label: "/" for root, otherwise last path component max 3 chars
	mp = m["fs_mount"]
	fs_label = "/" if mp == "/" else (mp.split("/")[-1] or "fs")[:3].upper()

	rows = [
		("CPU", m["cpu"],	  f"{m['cpu']:.0f} %"),
		("RAM", m["ram_pct"], f"{m['ram_pct']:.0f} %"),
		(fs_label, m["fs_pct"], f"{m['fs_avail']:.0f} G"),
	]
	
	print('Rows:' + str(rows))
	
	for i, (label, pct, right) in enumerate(rows):
		draw_bar_row(draw, font, 1 + i * (BAR_H + GAP), label, pct, right)

	# Divider line
	draw.line([(0, SPARK_Y - 1), (W - 1, SPARK_Y - 1)], fill=DIVIDER_C)

	# Sparkline (no label — more room for the waveform)
	draw_sparkline(draw, cpu_history)

	return img
	
def main():
	m = {"cpu": 10, "ram_pct": 20, "ram_used": 30, "ram_total": 40, "fs_avail": 50, "fs_size": 60, "fs_pct": 70, "fs_mount": "/tmp/mount"}
	cpu_history = [1,2,3,4,5]
	img = render_frame(m, cpu_history)
	img.save('test.png')
	
if __name__ == "__main__":
	main()
