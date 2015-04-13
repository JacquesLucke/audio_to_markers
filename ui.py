import bpy
from . utils import *

class AudioToMarkersPanel(bpy.types.Panel):
    bl_idname = "audio_to_markers_panel"
    bl_label = "Audio to Markers"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        settings = get_settings()
        
        layout.prop(settings, "path", text = "Sound")