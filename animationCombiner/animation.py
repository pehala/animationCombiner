"""Animation processing module"""
from mathutils import Quaternion

from .api.actions import Action


def process_animation(armature, action: Action, base_skeleton, skeleton, parts, frame_start=0):
    """Test"""
    frame_delay = action.length_group.slowdown
    animation = action.animation
    order = animation.order
    disabled_parts = {part.uuid for part in action.body_parts if not part.checked}

    disabled_bones = {"root"}
    for uuid, bones in parts.items():
        if uuid in disabled_parts:
            disabled_bones.update(bones)

    # Set it to base rotation
    for name, rotation in base_skeleton.items():
        if name not in disabled_bones:
            bone = armature.pose.bones[name]
            bone.rotation_mode = "QUATERNION"
            bone.rotation_quaternion = rotation
            bone.keyframe_insert(
                data_path="rotation_quaternion",
                frame=frame_start,
                group=name,
            )

    last_frame = frame_start
    for i, frame in enumerate(animation.animation[action.length_group.start : action.length_group.end]):
        last_frame = frame_start + (i * frame_delay)
        for name, rotation in zip(order, frame.rotations):
            if action.use_movement and name == "root":
                bone = armature.pose.bones[name]
                bone.location = animation.movement[i].translation
                bone.keyframe_insert(
                    data_path="location",
                    frame=last_frame,
                    group=name,
                )

            if name not in disabled_bones:
                bone = armature.pose.bones[name]
                bone.rotation_quaternion = base_skeleton[name] @ Quaternion(rotation.rotation)
                bone.keyframe_insert(
                    data_path="rotation_quaternion",
                    frame=last_frame,
                    group=name,
                )
    if action.transition.reset:
        last_frame = last_frame + action.transition.reset_length
        for name, rotation in base_skeleton.items():
            if name not in disabled_bones:
                bone = armature.pose.bones[name]
                bone.rotation_quaternion = rotation
                bone.keyframe_insert(
                    data_path="rotation_quaternion",
                    frame=last_frame,
                    group=name,
                )
    return last_frame + action.transition.length
