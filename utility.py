import math
from pygame import draw


def drawDashedLine(surface, start, end, rate, color, width=1):
    x1, y1 = start
    x2, y2 = end
    on, off = rate

    dx = x1 - x2
    dy = y1 - y2
    dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    n = int(dist / (on + off))

    for i in range(n):
        start_x = int(x1 - dx * i / n)
        start_y = int(y1 - dy * i / n)
        end_x = int(x1 - dx * (i + 0.5) / n)
        end_y = int(y1 - dy * (i + 0.5) / n)
        draw.line(surface, color, (start_x, start_y), (end_x, end_y), width)
