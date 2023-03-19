"""
Very ugly and ineffective way to properly calculate rotations for Armatures from only positions:
* Create Armature A:
* Create Armature B from Rest Pose
* For Every frame:
    * Set Armature A to positions from frame
    * Set Armature B to copy Armature A
    * Save rotation from Armature B

"""
from contextlib import contextmanager

import bpy
from bpy.types import Armature
from mathutils import Quaternion

from animationCombiner.api.skeletons import HDMSkeleton
from animationCombiner.utils import create_armature, create_bones


def set_bone(pose, bone):
    """Sets bone tail to the specific position"""
    if bone.parent:
        bone.head = bone.parent.tail
    bone.tail = pose.bones[bone.name]

    for child in bone.children:
        set_bone(pose, child)


def transform_bone(target: Armature, source: Armature, bone):
    """Transforms from one armature to another"""
    target_bone = source.pose.bones[bone.name]
    target_matrix = source.convert_space(
        pose_bone=target_bone, matrix=target_bone.matrix_basis, from_space="LOCAL_WITH_PARENT", to_space="WORLD"
    )

    final = target.convert_space(pose_bone=bone, matrix=target_matrix, from_space="WORLD", to_space="LOCAL")
    bone.rotation_quaternion = final.to_quaternion()
    bpy.context.view_layer.update()

    for child in bone.children:
        transform_bone(target, source, child)


@contextmanager
def create_rotation_armatures(initial_pose, skeleton):
    """Creates two temporary armatures, which can be used for rotation calculations"""
    mode = bpy.context.object.mode
    original = bpy.context.view_layer.objects.active
    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    armature_a = create_armature("A1", exit_mode="EDIT")
    create_bones(armature_a.data, skeleton, initial_pose)

    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    armature_b = create_armature("B1", exit_mode="EDIT")
    create_bones(armature_b.data, skeleton, initial_pose)

    try:
        yield armature_a, armature_b
    finally:
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
        bpy.data.objects.remove(armature_a)
        bpy.data.objects.remove(armature_b)
        bpy.context.view_layer.objects.active = original
        bpy.ops.object.mode_set(mode=mode, toggle=False)


def calculate_frame(armature_a: Armature, armature_b: Armature, pose):
    """Calculates rotation difference between initial pose and pose specified"""
    rotations = {}
    bpy.context.view_layer.objects.active = armature_a
    bpy.ops.object.mode_set(mode="EDIT", toggle=False)
    set_bone(pose, armature_a.data.edit_bones.get("root"))
    bpy.context.view_layer.update()

    bpy.context.view_layer.objects.active = armature_b
    bpy.ops.object.mode_set(mode="POSE", toggle=False)
    transform_bone(armature_b, armature_a, armature_b.pose.bones["root"])
    for bone in armature_b.pose.bones:
        rotations[bone.name] = bone.rotation_quaternion.copy()
    return rotations


def calculate_frames(raw_animation) -> list[dict[str, Quaternion]]:
    """Calculates rotation difference between initial pose and all other poses"""
    poses = []
    with create_rotation_armatures(raw_animation.poses[0], HDMSkeleton()) as armatures:
        armature_a, armature_b = armatures
        for pose in raw_animation.poses[1:]:
            poses.append(calculate_frame(armature_a, armature_b, pose))

    # stabilize animation
    for i in range(len(poses) - 1):
        pose1 = poses[i]
        pose2 = poses[i + 1]
        for bone, rotation in pose1.items():
            rotation2 = pose2[bone]
            if rotation.dot(rotation2) < 0:
                pose2[bone].negate()

    return poses
