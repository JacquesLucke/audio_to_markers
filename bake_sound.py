import bpy
import os
from bpy.props import *
from . utils import *
from . event_helper import *
from . properties import frequence_ranges

def update_fcurve_selection():   
    current_fcurve = get_current_sound_fcurve()
    if current_fcurve:
        settings = get_settings() 
        fcurves = get_sound_fcurves()
        for fcurve in fcurves:
            fcurve.hide = settings.hide_unused_fcurves
        current_fcurve.hide = False
        only_select_fcurve(current_fcurve)  

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
        settings.sound_strips.clear()   
             
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
               
               
class BakeSound(bpy.types.Operator):
    bl_idname = "audio_to_markers.bake_sound"
    bl_label = "Bake Sound"
    bl_description = "Bake the sound from current settings"
    bl_options = {"REGISTER", "INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        return os.path.exists(get_settings().path)
    
    def execute(self, context):
        scene = context.scene
        scene.sync_mode = "AUDIO_SYNC"
        
        settings = get_settings()
        
        frame_before = scene.frame_current
        scene.frame_current = scene.frame_start
        
        fcurve = self.new_fcurve_from_settings(settings)
        only_select_fcurve(fcurve)
        
        fcurve.lock = False
        bpy.ops.graph.sound_bake(
            filepath = settings.path,
            low = settings.bake.low,
            high = settings.bake.high)
        
        scene.frame_current = frame_before            
        update_fcurve_selection()
        return {"FINISHED"}
    
    def new_fcurve_from_settings(self, settings):
        baked_data = settings.baked_data
        
        item = baked_data.add()
        item.path = settings.path
        item.bake.low = settings.bake.low
        item.bake.high = settings.bake.high
        item.keyframe_insert("strength", frame = 0)
        
        return get_fcurve_from_item_index(len(baked_data) - 1)
    
    
class BakeAllFrequences(bpy.types.Operator):
    bl_idname = "audio_to_markers.bake_all_frequences"
    bl_label = "Bake All Frequences"
    bl_description = "Bake all template frequences"
    bl_options = {"REGISTER", "INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        return os.path.exists(get_settings().path)
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(0.001, context.window)
        self.progress_index = 0
        self.counter = 1
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}
    
    def modal(self, context, event):
        if is_middle_mouse(event): return {"PASS_THROUGH"}
    
        if check_event(event, "ESC") or self.progress_index == len(frequence_ranges):
            self.finish()
            return {"FINISHED"}
        
        settings = get_settings()
        settings.info = "Bake {} of {}".format(self.progress_index, len(frequence_ranges))
        bake_settings = settings.bake
        self.counter += 1    
        
        if event.type == "TIMER" and self.counter % 30 == 0:
            context.area.tag_redraw()
            bake_settings.low, bake_settings.high = frequence_ranges[self.progress_index]
            bpy.ops.audio_to_markers.bake_sound()
            self.progress_index += 1
        
        return {"RUNNING_MODAL"}
    
    def finish(self):
        bpy.context.window_manager.event_timer_remove(self.timer)
        get_settings().info = ""
            
                   
class RemoveBakedData(bpy.types.Operator):
    bl_idname = "audio_to_markers.remove_baked_data"
    bl_label = "Remove Baked Data"
    bl_description = "Remove all sound fcurves created by this addon"
    bl_options = {"REGISTER", "INTERNAL"}
    
    def execute(self, context):
        get_settings().baked_data.clear()
        for fcurve in get_sound_fcurves():
            context.scene.animation_data.action.fcurves.remove(fcurve)
        context.area.tag_redraw()
        return {"FINISHED"}
                               

def get_sound_fcurves():
    fcurves = []
    try:
        for fcurve in bpy.context.scene.animation_data.action.fcurves:
            if fcurve.data_path.startswith("audio_to_markers.baked_data["):
                fcurves.append(fcurve)
    except: pass
    return fcurves                              
                               
def get_current_sound_fcurve():
    def is_current_item(item):
        return item.path == settings.path and \
            item.bake.low == settings.bake.low and \
            item.bake.high == settings.bake.high
                     
    settings = get_settings()   
    for i, item in enumerate(settings.baked_data):   
        if is_current_item(item):
            return get_fcurve_from_item_index(i)
    return None    

def get_fcurve_from_item_index(index):
    data_path = "audio_to_markers.baked_data[{}].strength".format(index)
    return get_fcurve_from_path(bpy.context.scene, data_path)                      