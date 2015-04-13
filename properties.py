import bpy
import re
from bpy.props import *
from bpy.types import PropertyGroup
from . utils import *


frequence_ranges = [
    (0, 20),
    (20, 40),
    (40, 80),
    (80, 250),
    (250, 600),
    (600, 4000),
    (4000, 6000),
    (6000, 8000),
    (8000, 20000) ]
    
def get_frequence_range_items(self, context):
    items = []
    bake = get_settings().bake
    ranges = [(bake.low, bake.high)] + frequence_ranges
    
    for low, high in ranges:
        ui_name = make_frequence_ui_name(low, high)
        item = (ui_name, ui_name, "")
        items.append(item)
    return items

is_setting = False
def apply_preset(self, context):
    global is_setting
    if not is_setting:
        is_setting = True
        settings = get_settings()
        bake = settings.bake
        match = re.match("([0-9]+) - ([0-9]+)", settings.frequence_range_preset)
        low, high = float(match.group(1)), float(match.group(2))
        bake.low, bake.high = low, high
        settings.frequence_range_preset = make_frequence_ui_name(low, high)
        is_setting = False
        
def make_frequence_ui_name(low, high):
    return "{} - {} Hz".format(round(low), round(high))   


def fits_current_settings(self):
    settings = get_settings()
    return settings.path == self.path and \
        settings.bake.low == self.settings.low and \
        settings.bake.high == self.settings.high     
        
        

class SoundStripData(PropertyGroup):
    sequence_name = StringProperty(name = "Sequence Name", default = "")
    
class BakeSettings(PropertyGroup):
    low = FloatProperty(name = "Low Frequence", default = 80, step = 100, min = 0, max = 50000)
    high = FloatProperty(name = "High Frequence", default = 250, step = 100, min = 0, max = 50000)

class BakedData(PropertyGroup):
    settings = PointerProperty(name = "Bake Settings", type = BakeSettings)
    path = StringProperty(name = "File Path", default = "")
    strength = FloatProperty(name = "Strength", default = 0)
    fits_current_settings = property(fits_current_settings)

class Settings(PropertyGroup):
    path = StringProperty(name = "File Path", description = "Path of the sound file", default = "")
    sound_strips = CollectionProperty(name = "Sound Strips", type = SoundStripData)
    
    frequence_range_preset = EnumProperty(name = "Frequence Range Preset", items = get_frequence_range_items, update = apply_preset)
    bake = PointerProperty(name = "Bake Settings", type = BakeSettings)
    baked_data = CollectionProperty(name = "Baked Data", type = BakedData)
    
    info = StringProperty(name = "Info Text", default = "")
    

def register():
    bpy.types.Scene.audio_to_markers = PointerProperty(name = "Audio to Markers", type = Settings)