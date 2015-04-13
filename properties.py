import bpy
from bpy.props import *

class Settings(bpy.types.PropertyGroup):
    path = StringProperty(name = "File Path", description = "Path of the music file", default = "")

def register():
    bpy.types.Scene.audio_to_markers = PointerProperty(name = "Audio to Markers", type = Settings)