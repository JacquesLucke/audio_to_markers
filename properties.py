import bpy
from bpy.props import *
from bpy.types import PropertyGroup

class SoundStripData(PropertyGroup):
    sequence_name = StringProperty(name = "Sequence Name", default = "")

class Settings(PropertyGroup):
    path = StringProperty(name = "File Path", description = "Path of the music file", default = "")
    sound_strips = CollectionProperty(name = "Sound Strips", type = SoundStripData)

def register():
    bpy.types.Scene.audio_to_markers = PointerProperty(name = "Audio to Markers", type = Settings)