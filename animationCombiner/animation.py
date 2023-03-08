"""Animation processing module"""
import math

import bpy
import numpy as np
from bpy.types import EditBone, Armature
from mathutils import Quaternion

from .api.actions import Action
from .api.model import Pose
from .api.skeletons import Skeleton


def create_bone(armature, name, parent: EditBone, pose: Pose, skeleton: Skeleton):
    bone = armature.edit_bones.new(name)
    bone.head = parent.tail
    bone.tail = pose.bones[name]
    bone.parent = parent

    for child in skeleton.relations.get(name, []):
        create_bone(armature, child, bone, pose, skeleton)


def create_bones(armature: Armature, skeleton: Skeleton, pose: Pose, root: EditBone = None):
    if not root:
        root = armature.edit_bones.new("root")
        root.head = np.array((0, 0.1, 0))
        root.tail = pose.bones["root"]

    for child in skeleton.relations["root"]:
        create_bone(armature, child, root, pose, skeleton)


def create_armature(name: str = "Armature"):
    """Create the entire Armature"""
    bpy.ops.object.armature_add(enter_editmode=True)
    armature = bpy.data.armatures[bpy.context.view_layer.objects.active.name]
    armature.edit_bones.remove(armature.edit_bones.get("Bone"))

    armature_object = bpy.context.view_layer.objects.active
    armature_object.name = name

    # Exit Armature editing
    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

    armature_object.rotation_mode = "XYZ"
    armature_object.rotation_euler.rotate_axis("X", math.radians(90))

    bpy.ops.object.mode_set(mode="POSE", toggle=False)
    return armature


def process_animation(armature, action: Action, base_skeleton, parts, frame_start=0, frame_delay=1):
    """Test"""
    animation = action.animation
    order = animation.order
    disabled_parts = {part.uuid for part in action.body_parts if not part.checked}

    disabled_bones = {"root"}
    for uuid, bones in parts.items():
        if uuid in disabled_parts:
            disabled_bones.update(bones)
    # # Set it to base rotation
    # for name, rotation in zip(order, base_skeleton):
    #     bone = armature.pose.bones[name]
    #     bone.rotation_mode = "QUATERNION"
    #     bone.rotation_quaternion = rotation
    #     bone.keyframe_insert(
    #         data_path="rotation_quaternion",
    #         frame=frame_start,
    #         group=name,
    #     )

    last_frame = frame_start
    for i, frame in enumerate(animation.animation[action.length_group.start : action.length_group.end]):
        last_frame = frame_start + (i * frame_delay)
        for name, rotation in zip(order, frame.rotations):
            if name not in disabled_bones:
                bone = armature.pose.bones[name]
                # bone.rotation_quaternion = (
                #     bone.bone.matrix_local @ Quaternion(rotation.rotation).normalized().to_matrix().to_4x4()
                # ).to_quaternion()
                bone.rotation_quaternion = (
                    bone.matrix @ bone.bone.matrix_local.inverted() @ Quaternion(rotation.rotation).to_matrix().to_4x4()
                ).to_quaternion()
                bone.keyframe_insert(
                    data_path="rotation_quaternion",
                    frame=last_frame,
                    group=name,
                )
    if action.transition.reset:
        last_frame = last_frame + action.transition.reset_length
        for name, rotation in zip(order, base_skeleton):
            if name not in disabled_bones:
                bone = armature.pose.bones[name]
                bone.rotation_quaternion = (
                    bone.matrix @ bone.bone.matrix_local.inverted() @ Quaternion(rotation.rotation).to_matrix().to_4x4()
                ).to_quaternion()
                bone.keyframe_insert(
                    data_path="rotation_quaternion",
                    frame=last_frame,
                    group=name,
                )
    return last_frame + action.transition.length
