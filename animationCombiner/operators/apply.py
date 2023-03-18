import bpy

from animationCombiner.animation import process_animation
from animationCombiner.api.model import Pose
from animationCombiner.api.skeletons import HDMSkeleton
from animationCombiner.utils import create_bones


def skeleton_diff(base_skeleton, skeleton):
    """Calculates rotational difference between base skeleton and the new one"""
    return [base.coords.rotation_difference(pos.coords) for base, pos in zip(base_skeleton, skeleton)]


class ApplyOperator(bpy.types.Operator):
    """Applies the actions to the Armature."""

    bl_idname = "ac.process"
    bl_label = "Applies all actions to the armature"

    def execute(self, context):
        """
        * Delete armature bones
        * TODO: Rescale all other skeletons (=set bone length to specific lengths)
        * Create new armature bones based on chosen skeleton
         For each action
            * Apply rotation
            * TODO: Apply translation to root
            * Calculate transition
        """

        bpy.context.scene.frame_set(bpy.context.scene.frame_start)
        armature = bpy.context.view_layer.objects.active
        armature_data = armature.data
        armature.animation_data_clear()

        if len(armature_data.groups) == 0:
            return {"FINISHED"}

        # Select skeleton from poses
        base_skeleton = armature_data.groups[0].actions[0].animation.skeleton
        skeleton = HDMSkeleton()

        # Recreate all Bones
        order = skeleton.order()
        bpy.ops.object.mode_set(mode="EDIT", toggle=False)
        for name in order:
            bone = armature_data.edit_bones.get(name)
            if bone is not None:
                armature_data.edit_bones.remove(bone)

        pose = Pose({name: coords.coords for name, coords in zip(order, base_skeleton)})
        create_bones(armature_data, skeleton, pose)
        bpy.ops.object.mode_set(mode="POSE", toggle=False)

        groups = []
        for group in armature_data.groups:
            group_list = []
            for action in group.actions:
                group_list.append((action, skeleton_diff(base_skeleton, action.animation.skeleton)))
            if len(group_list) > 0:
                groups.append(group_list)

        parts_dict = {part.uuid: {bone.bone for bone in part.bones} for part in armature_data.body_parts.body_parts}
        starting = 0
        for group in groups:
            ending = starting
            for action, diff in group:
                ending = max(
                    ending, process_animation(armature, action, diff, skeleton, parts_dict, frame_start=starting)
                )
            starting = ending
        bpy.context.scene.frame_end = starting
        armature_data.is_applied = True
        return {"FINISHED"}
