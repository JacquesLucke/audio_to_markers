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
        
        row = layout.row(align = True)
        row.prop(settings, "path", text = "Sound")
        row.operator("audio_to_markers.select_sound_file", text = "", icon = "FILE_SOUND")
        
        row = layout.row(align = True)
        row.operator("audio_to_markers.cache_sound_strips", text = "", icon = "LOAD_FACTORY")
        row.operator("audio_to_markers.load_sound_into_sequence_editor", text = "Load Sound")
        row.operator("audio_to_markers.remove_sound_strips", text = "", icon = "X")