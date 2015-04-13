import bpy
from . utils import *

frequence_ranges = (
    ("0 - 20 Hz", (0, 20)),
    ("20 - 40 Hz", (20, 40)),
    ("40 - 80 Hz", (40, 80)),
    ("80 - 250 Hz", (80, 250)),
    ("250 - 600 Hz", (250, 600)),
    ("600 - 4000 Hz", (600, 4000)),
    ("4 - 6 kHz", (4000, 6000)),
    ("6 - 8 kHz", (6000, 8000)),
    ("8 - 20 kHz", (8000, 20000)) )
frequence_range_dict = {frequence_range[0]: frequence_range[1] for frequence_range in frequence_ranges} 
frequence_range_items = [(frequence_range[0], frequence_range[0], "") for frequence_range in frequence_ranges]

