import bpy
from bgl import *
from . bake_sound import get_current_sound_fcurve

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
        return {"RUNNING_MODAL"}
    
    
    
    def modal(self, context, event):
        context.area.tag_redraw()
            
        if event.type in {"RIGHTMOUSE", "ESC"}:
            self.finish()
            return {"CANCELLED"}
        
        fcurve = get_current_sound_fcurve()
        if not fcurve: 
            self.mode = "NO_FCURVE"
            return {"RUNNING_MODAL"}
        elif self.mode == "NO_FCURVE":
            self.mode = "NONE"
    
        if self.mode == "NONE":
            self.snap_location, snap_frame = self.get_snap_data(event, fcurve)
            
        return {"RUNNING_MODAL"}
    
    def get_snap_data(self, event, fcurve):
        mouse_x = event.mouse_region_x
        search_size = 20
        frame = self.get_frame_under_region_x(mouse_x)
        
        start_frame = round(self.get_frame_under_region_x(mouse_x - search_size))
        end_frame = round(self.get_frame_under_region_x(mouse_x + search_size))
        
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
            while value >= snap_value:
                snap_frame = test_frame
                snap_value = value
                test_frame += change
                value = fcurve.evaluate(test_frame)
                        
        
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
  
    def finish(self):
        bpy.types.SpaceGraphEditor.draw_handler_remove(self._handle, "WINDOW")
        
        
    def draw_callback_px(tmp, self, context):
        if self.mode == "NONE":
            self.draw_marker(self.snap_location)      
    
    def draw_marker(self, location, enabled = True):
        if enabled:
            color = (0.4, 0.8, 0.2, 0.7)
            size = 8.0
        else:
            color = (0.8, 0.8, 0.8, 0.5)
            size = 5.0
          
        glColor4f(*color)
        glEnable(GL_BLEND)
        glPointSize(size)
        glBegin(GL_POINTS)
        glVertex2f(*location)
        glEnd() 
        