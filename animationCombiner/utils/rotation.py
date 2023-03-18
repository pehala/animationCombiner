"""
Very ugly and ineffective way to properly calculate rotations for Armatures from only positions:
* Create Armature A:
* Create Armature B from Rest Pose
* For Every frame:
    * Set Armature A to positions from frame
    * Set Armature B to copy Armature A
    * Save rotation from Armature B

"""
import bpy
from mathutils import Quaternion

from animationCombiner.api.skeletons import HDMSkeleton
from animationCombiner.utils import create_armature, create_bones


def set_bone(pose, bone):
    """Sets bones to the position"""
    if bone.parent:
        bone.head = bone.parent.tail
    bone.tail = pose.bones[bone.name]

    for child in bone.children:
        set_bone(pose, child)


def transform_bone(armature1, armature2, bone):
    target_bone = armature2.pose.bones[bone.name]
    target_matrix = armature2.convert_space(
        pose_bone=target_bone, matrix=target_bone.matrix_basis, from_space="LOCAL_WITH_PARENT", to_space="WORLD"
    )

    final = armature1.convert_space(pose_bone=bone, matrix=target_matrix, from_space="WORLD", to_space="LOCAL")
    bone.rotation_quaternion = final.to_quaternion()
    bpy.context.view_layer.update()

    for child in bone.children:
        transform_bone(armature1, armature2, child)


def calculate_rotations(raw_animation) -> list[dict[str, Quaternion]]:
    original = bpy.context.view_layer.objects.active
    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    armatureA = create_armature("A1", exit_mode="EDIT")
    create_bones(armatureA.data, HDMSkeleton(), raw_animation.poses[0])

    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    armatureB = create_armature("B1", exit_mode="EDIT")
    create_bones(armatureB.data, HDMSkeleton(), raw_animation.poses[0])

    bpy.context.view_layer.update()
    poses = []
    for i, pose in enumerate(raw_animation.poses[1:]):
        # print(i)
        rotations = {}
        bpy.context.view_layer.objects.active = armatureA
        bpy.ops.object.mode_set(mode="EDIT", toggle=False)
        set_bone(pose, armatureA.data.edit_bones.get("root"))
        bpy.context.view_layer.update()

        bpy.context.view_layer.objects.active = armatureB
        bpy.ops.object.mode_set(mode="POSE", toggle=False)
        transform_bone(armatureB, armatureA, armatureB.pose.bones["root"])
        for bone in armatureB.pose.bones:
            rotations[bone.name] = bone.rotation_quaternion.copy()
        poses.append(rotations)

    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    bpy.data.objects.remove(armatureA)
    bpy.data.objects.remove(armatureB)
    bpy.context.view_layer.objects.active = original
    bpy.ops.object.mode_set(mode="POSE", toggle=False)
    return poses
