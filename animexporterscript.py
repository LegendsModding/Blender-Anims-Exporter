import bpy
import json
from mathutils import Euler, Quaternion
import math

def get_location(obj, frame, bone):
    frame = int(frame)  # Convert frame to an integer
    bpy.context.scene.frame_set(frame)
    pose_bone = obj.pose.bones.get(bone)  # Use bone instead of bone.name
    if pose_bone:
        loc = pose_bone.matrix.translation
        xloc = round(loc.x, 2)
        yloc = round(loc.y, 2)
        zloc = round(loc.z, 2)
        return xloc, yloc, zloc
    return 0.0, 0.0, 0.0  # Return default values if pose bone is not found


def convert_bone_animation(obj, bone):
    anim_data = {}

    # Get bone name
    bone_name = bone.name

    # Check if the object has animation data
    if not obj.animation_data or not obj.animation_data.action:
        return anim_data

    # Get bone location and rotation keyframes
    location_keyframes = []
    rotation_keyframes = []

    # Iterate over all keyframes of the bone
    for fc in obj.animation_data.action.fcurves:
        if fc.data_path == f'pose.bones["{bone_name}"].location':
            # Convert location keyframes to JSON format
            for kp in fc.keyframe_points:
                frame = kp.co.x
                loc_x = kp.handle_left.y
                loc_y, loc_z = get_location(obj, frame, bone.name)[1:]
                location_keyframes.append((frame, loc_x, loc_y, loc_z))

        elif fc.data_path == f'pose.bones["{bone_name}"].rotation_quaternion':
            # Convert rotation keyframes to JSON format
            for kp in fc.keyframe_points:
                frame = kp.co.x
                rot_x = kp.co.y
                rot_y = kp.handle_right.y
                rot_z = kp.handle_right[1]  # Access the w-component of the 2D vector for z-coordinate
                rotation_keyframes.append((frame, rot_x, rot_y, rot_z))

    # Convert bone location keyframes to JSON format
    location_data = {}
    for frame, loc_x, loc_y, loc_z in location_keyframes:
        position = [loc_x, loc_y, loc_z]
        location_data[str(frame)] = {
            "lerp_mode": "catmullrom",
            "post": position
        }

    # Convert bone rotation keyframes to JSON format
    rotation_data = {}
    for frame, rot_x, rot_y, rot_z in rotation_keyframes:
        rotation = Quaternion((rot_x, rot_y, rot_z, 1.0)).to_euler()  # Convert quaternion to Euler angles
        rotation = [rotation.x * 180 / 3.141592653589793,
                    rotation.y * 180 / 3.141592653589793,
                    rotation.z * 180 / 3.141592653589793]
        rotation_data[str(frame)] = {
            "lerp_mode": "catmullrom",
            "post": rotation
        }

    # Update anim_data with location and rotation data
    anim_data[bone_name] = {
        "lod_distance": 0.0,
        "rotation": rotation_data,
        "position": location_data
    }

    return anim_data

def convert_selected_objects_animation(path):
    objects = bpy.context.selected_objects

    anim_data = {}

    for obj in objects:
        if obj.type == 'ARMATURE':
            armature = obj.data

            # Check if the armature has an associated action
            if not obj.animation_data or not obj.animation_data.action:
                continue

            action = obj.animation_data.action
            anim_name = action.name
            anim_data[anim_name] = {}

            # Set bones data
            bones_data = {}
            for bone in armature.bones:
                if bone.name not in obj.pose.bones:
                    continue

                bone_data = convert_bone_animation(obj, obj.pose.bones[bone.name]) # Access the local bone data
                bones_data[bone.name] = bone_data[bone.name]

            anim_data[anim_name]["bones"] = bones_data

    # Save animation data to JSON file
    with open(path, 'w') as file:
        json.dump(anim_data, file, indent=4)

    print("Animation data saved to", path)

# Usage: Replace 'path/to/output.json' with the desired output file path
convert_selected_objects_animation('C:/Users/fr33d/Desktop/MCLModding/kgoledmdddtest1.json')
