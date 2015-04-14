import bpy

class BakeFCurves(bpy.types.Operator):
    bl_idname = "audio_to_markers.bake_fcurves"
    bl_label = "Bake FCurves"
    bl_description = "Bake Selected FCurves"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        bpy.ops.graph.bake()
        return {"FINISHED"}
        