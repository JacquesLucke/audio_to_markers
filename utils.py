import bpy

def get_settings():
    return bpy.context.scene.audio_to_markers


def only_select_fcurve(fcurve):
    deselect_all_fcurves()
    if fcurve:
        fcurve.select = True

def deselect_all_fcurves():
    for action in bpy.data.actions:
        for fcurve in action.fcurves:
            fcurve.select = False
            

def get_fcurve_from_path(object, data_path):
    try:
        for fcurve in object.animation_data.action.fcurves:
            if fcurve.data_path == data_path:
                return fcurve
    except: pass
    return None