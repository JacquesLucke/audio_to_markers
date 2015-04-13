import bpy
import os
from bpy.props import *
from . utils import *

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
        settings = get_settings()
        self.create_sequence_editor_if_necessary()
        
        path = settings.path
        name = os.path.basename(path)
        frame = scene.frame_start
        channel = self.get_empty_channel_index(scene)
        
        sequence = scene.sequence_editor.sequences.new_sound(
            name = name, 
            filepath = path,
            frame_start = frame,
            channel = channel)
            
        scene.frame_end = sequence.frame_start + sequence.frame_duration
        
        item = settings.sound_strips.add()
        item.sequence_name = sequence.name
        
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
    
    
class RemoveSoundStrips(bpy.types.Operator):
    bl_idname = "audio_to_markers.remove_sound_strips"
    bl_label = "Remove Sound Strips"
    bl_description = "Remove all sound strips which were created with this addon"
    bl_options = {"REGISTER", "INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        return context.scene.sequence_editor
    
    def execute(self, context):
        scene = context.scene
        settings = get_settings()
        sequences = scene.sequence_editor.sequences
        
        for item in settings.sound_strips:
            sequence = sequences.get(item.sequence_name)
            if sequence:
                sequence.sound.use_memory_cache = False
                sequences.remove(sequence)
                
        return {"FINISHED"}
            
            
class CacheSounds(bpy.types.Operator):
    bl_idname = "audio_to_markers.cache_sound_strips"
    bl_label = "Cache Sound Strips"
    bl_description = "Enable 'Use Memory Cache' for the sound strips with the path"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        path = get_settings().path
        for sound in bpy.data.sounds:
            if sound.filepath == path and not sound.use_memory_cache:
                sound.use_memory_cache = True
        return {"FINISHED"}
               