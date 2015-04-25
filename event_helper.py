import bpy

def is_middle_mouse(event):
    return event.type in ["MIDDLEMOUSE", "WHEELDOWNMOUSE", "WHEELINMOUSE", "WHEELOUTMOUSE", "WHEELUPMOUSE"]

def is_left_release(event):
    return check_event(event, "LEFTMOUSE", value = "RELEASE")

def check_event(event, type, value = None, ctrl = False, shift = False, alt = False):
    return event.type == type and \
        (event.value == value or value is None) and \
        event.ctrl == ctrl and \
        event.shift == shift and \
        event.alt == alt