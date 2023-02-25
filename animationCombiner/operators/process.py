import bpy

from animationCombiner.animation import process_animation, create_bones
from animationCombiner.api.model import Pose
from animationCombiner.api.skeletons import HBMSkeleton


def skeleton_diff(base_skeleton, skeleton):
    """Calculates rotational difference between base skeleton and the new one"""
    return [pos.coords.rotation_difference(base.coords) for pos, base in zip(base_skeleton, skeleton)]


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
        armature = bpy.data.armatures[bpy.context.view_layer.objects.active.name]
        base_skeleton = armature.actions[0].animation.skeleton
        skeleton = HBMSkeleton()

        # Recreate all Bones
        order = skeleton.order()
        bpy.ops.object.mode_set(mode="EDIT", toggle=False)
        for bone in order:
            armature.edit_bones.remove(armature.edit_bones.get(bone))

        pose = Pose({
            name: coords.coords for name, coords in zip(order, base_skeleton)
        })
        create_bones(armature, skeleton, pose)
        bpy.ops.object.mode_set(mode="POSE", toggle=False)

        ending = 0
        if len(armature.actions) == 0:
            return {"FINISHED"}

        base_skeleton = armature.actions[0].animation.skeleton
        actions = []
        for action in armature.actions:
            actions.append((action, skeleton_diff(base_skeleton, action.animation.skeleton)))

        for action, diff in actions:
            ending = process_animation(bpy.context.view_layer.objects.active, action, diff, frame_start=ending)
        bpy.context.scene.frame_end = ending
        armature.is_applied = True
        return {"FINISHED"}
