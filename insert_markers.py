import bpy
from bgl import *
from . bake_sound import get_current_sound_fcurve
from . event_helper import *

class InsertMarkers(bpy.types.Operator):
    bl_idname = "audio_to_markers.insert_markers"
    bl_label = "Insert Markers"
    bl_description = "Start the interactive marker placement mode"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return get_current_sound_fcurve()
        
    def invoke(self, context, event):
        args = (self, context)
        self._handle = bpy.types.SpaceGraphEditor.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        self.mode = "NONE"
        self.snap_size = 20
        return {"RUNNING_MODAL"}
    
    
    
    def modal(self, context, event):
        context.area.tag_redraw()
            
        if event.type in {"RIGHTMOUSE", "ESC"}:
            self.finish()
            return {"CANCELLED"}
        
        if 20 < event.mouse_region_x < context.region.width - 20 and 20 < event.mouse_region_y < context.region.height - 20:
            if is_middle_mouse(event):
                return {"PASS_THROUGH"} 
        else:
            return {"PASS_THROUGH"}
        
        fcurve = get_current_sound_fcurve()
        if not fcurve: 
            self.mode = "NO_FCURVE"
            return {"RUNNING_MODAL"}
        elif self.mode == "NO_FCURVE":
            self.mode = "NONE"
    
        if self.mode == "NONE":
            snap_location, snap_frame = self.get_snap_data(event, fcurve)
            self.mouse_x = event.mouse_region_x
            
            self.temporary_markers = [(snap_location, not marker_exists(snap_frame))]
            
            if is_left_click(event):
                self.insert_marker(snap_frame)
            
        return {"RUNNING_MODAL"}
    
    def get_snap_data(self, event, fcurve):
        mouse_x = event.mouse_region_x
        frame = self.get_frame_under_region_x(mouse_x)
        
        start_frame = round(self.get_frame_under_region_x(mouse_x - self.snap_size))
        end_frame = round(self.get_frame_under_region_x(mouse_x + self.snap_size))
        
        snap_frame = 0
        snap_value = -1000000
        for frame in range(start_frame, end_frame):
            value = fcurve.evaluate(frame)
            if value > snap_value:
                snap_frame = frame
                snap_value = value
                
        if snap_frame in [start_frame, end_frame-1]:
            change = -1 if snap_frame == start_frame else 1
            value = snap_value
            test_frame = snap_frame
            safety_counter = 0
            while value >= snap_value:
                snap_frame = test_frame
                snap_value = value
                test_frame += change
                value = fcurve.evaluate(test_frame)
                safety_counter += 1
                if safety_counter > 30:
                    break
        
        snap_location = self.view_to_region(snap_frame, snap_value)
        return snap_location, snap_frame
    
    def get_snap_region_y(self, x, fcurve):
        frame = self.get_frame_under_region_x(x)
        view_y = fcurve.evaluate(frame)
        return self.get_region_y_above_view_y(view_y)
        
    def get_frame_under_region_x(self, x):
        return bpy.context.region.view2d.region_to_view(x, 0)[0]
    def get_region_x_above_frame(self, frame):
        return bpy.context.region.view2d.view_to_region(frame, 0)[0]
    def view_to_region(self, x, y):
        return bpy.context.region.view2d.view_to_region(x, y, clip = False)
  
  
    def insert_marker(self, frame):
        bpy.context.scene.timeline_markers.new(frame = frame, name = "# " + str(frame))
  
    def finish(self):
        bpy.types.SpaceGraphEditor.draw_handler_remove(self._handle, "WINDOW")
        
        
    def draw_callback_px(tmp, self, context):
        if self.mode == "NONE":
            self.draw_temporary_markers()   
            x = self.mouse_x
            size = self.snap_size
            self.draw_marked_area(x-size, x+size, [0.1, 0.1, 0.1, 0.01])
            
    def draw_temporary_markers(self):
        for location, enabled in self.temporary_markers:
            self.draw_marker(location, enabled) 
    
    def draw_marker(self, location, enabled = True):
        if enabled:
            color = [0.4, 0.8, 0.2, 0.7]
            size = 8.0
        else:
            color = [0.8, 0.8, 0.8, 0.5]
            size = 5.0
          
        glColor4f(*color)
        glEnable(GL_BLEND)
        glPointSize(size)
        glBegin(GL_POINTS)
        glVertex2f(*location)
        glEnd() 
        
        color[3] = 0.2
        glColor4f(*color)
        glBegin(GL_LINES)
        glVertex2f(*location)
        glVertex2f(location[0], 0)
        glEnd()
        
    def draw_marked_area(self, start, end, color):
        glColor4f(*color)
        glEnable(GL_BLEND)
        glBegin(GL_POLYGON)
        glVertex2f(start, 5000)
        glVertex2f(end, 5000)
        glVertex2f(end, 0)
        glVertex2f(start, 0)
        glEnd()
        
def insert_markers(frames):
    scene = bpy.context.scene
    marked_frames = get_marked_frames()
    for frame in frames:
        if frame not in marked_frames:
            scene.timeline_markers.new(name = "#{}".format(frame), frame = frame)     
     
def marker_exists(frame):
    return frame in get_marked_frames()    
        
def get_marked_frames():
    return [marker.frame for marker in bpy.context.scene.timeline_markers]        
        
        
class RemoveMarkers(bpy.types.Operator):
    bl_idname = "audio_to_markers.remove_markers"
    bl_label = "Remove Markers"
    bl_description = "Remove all timeline markers of the current scene"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return bpy.context.scene
    
    def execute(self, context):
        bpy.context.scene.timeline_markers.clear()
        return {"FINISHED"}
                