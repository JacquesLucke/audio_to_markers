import bpy
import os
from bpy.props import *
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


class SelectSoundFile(bpy.types.Operator):
    bl_idname = "audio_to_markers.select_sound_file"
    bl_label = "Select Sound File"
    bl_description = "Select a music file with the file selector"
    bl_options = {"REGISTER", "INTERNAL"}
    
    filepath = StringProperty(subtype = "FILE_PATH")
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
    
    def execute(self, context):
        get_settings().path = self.filepath
        return {"FINISHED"}
        
        
class LoadSoundIntoSequenceEditor(bpy.types.Operator):
    bl_idname = "audio_to_markers.load_sound_into_sequence_editor"
    bl_label = "Load Sound into Sequence Editor"
    bl_description = "Create a new sound strip"
    bl_options = {"REGISTER", "INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        return os.path.exists(get_settings().path)
    
    def execute(self, context):
        scene = context.scene
        self.create_sequence_editor_if_necessary()
        
        path = get_settings().path
        name = os.path.basename(path)
        frame = scene.frame_start
        channel = self.get_empty_channel_index(scene)
        
        sequence = scene.sequence_editor.sequences.new_sound(
            name = name, 
            filepath = path,
            frame_start = frame,
            channel = channel)
            
        scene.frame_end = sequence.frame_start + sequence.frame_duration
        
        return {"FINISHED"}
    
    def create_sequence_editor_if_necessary(self):
        scene = bpy.context.scene
        if not scene.sequence_editor:
            scene.sequence_editor_create() 
    
    def get_empty_channel_index(self, scene):
        used_channels = [sequence.channel for sequence in scene.sequence_editor.sequences]
        for channel in range(1, 32):
            if not channel in used_channels:
                return channel
        return 0