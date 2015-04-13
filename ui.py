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
        
        col = layout.column(align = False)
        
        row = col.row(align = True)
        row.prop(settings, "path", text = "Sound")
        row.operator("audio_to_markers.select_sound_file", text = "", icon = "FILE_SOUND")
        
        row = col.row(align = True)
        row.operator("audio_to_markers.cache_sound_strips", text = "", icon = "LOAD_FACTORY")
        row.operator("audio_to_markers.load_sound_into_sequence_editor", text = "Load Sound")
        row.operator("audio_to_markers.remove_sound_strips", text = "", icon = "X")
        
        
        col = layout.column(align = False)
        
        subcol = col.column(align = True)
        subcol.prop(settings, "frequence_range_preset", text = "")
        subcol.prop(settings.bake, "low")
        subcol.prop(settings.bake, "high")
        subcol.operator("audio_to_markers.bake_sound", text = "Bake", icon = "RNDCURVE")
        
        row = col.row(align = True)
        if settings.hide_unused_fcurves: row.prop(settings, "hide_unused_fcurves", text = "", icon = "RESTRICT_VIEW_ON")
        else: row.prop(settings, "hide_unused_fcurves", text = "", icon = "RESTRICT_VIEW_OFF")
        row.operator("audio_to_markers.bake_all_frequences", text = "Bake All")
        row.operator("audio_to_markers.remove_baked_data", text = "", icon = "X")
        
        
        
        if settings.info != "":
            layout.label(settings.info)