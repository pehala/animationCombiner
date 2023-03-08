"""Collection of all utility functions/classes that didnt fit anywhere else"""
import bpy
from bpy.types import PropertyGroup, Property, bpy_prop_collection


class Singleton(type):
    """Metaclass for Singleton markings. https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def copy(from_prop: Property, to_prop: Property, depth=0) -> None:
    if type(from_prop) != type(to_prop):
        return

    if isinstance(from_prop, PropertyGroup):
        for propname in from_prop.__annotations__.keys():
            from_subprop = getattr(from_prop, propname)
            if isinstance(from_subprop, PropertyGroup) or isinstance(from_subprop, bpy_prop_collection):
                copy(from_subprop, getattr(to_prop, propname), depth + 1)
            else:
                try:
                    setattr(to_prop, propname, from_subprop)
                # if propname == "name" and depth == 0:
                #     to_prop.name += "_copy"
                except (AttributeError, TypeError):
                    pass

    elif isinstance(from_prop, bpy_prop_collection):
        to_prop.clear()
        for from_subprop in from_prop.values():
            copy(from_subprop, to_prop.add(), depth + 1)


def on_actions_update(self=None, context=None):
    """Recalculates length of final animation after the actions were updated"""
    armature = bpy.context.view_layer.objects.active.data
    length = 0
    for group in armature.groups:
        group.errors.clear()
        group_length = 0
        parts = set()
        for action in group.actions:
            group_length = max(action.length_group.length, group_length)
            action.length_group.length = (
                action.length_group.original_length
                + action.transition.length
                + (action.transition.reset_length if action.transition.reset else 0)
            )
            for part in action.body_parts:
                if part.checked:
                    if part.uuid in parts:
                        group.add_error("COLLIDING_PARTS")
                        break
                    parts.add(part.uuid)
        group.length = group_length
        group.actions_count = len(group.actions)
        length += group_length
    armature.animation_length = length
    armature.is_applied = False


def calculate_rotations(self, bone, skeleton, first_pose, pose, results, parent=None):
    if parent:
        first = first_pose.bones[bone] - first_pose.bones[parent]
        current = pose.bones[bone] - pose.bones[parent]
    else:
        first = first_pose.bones[bone]
        current = pose.bones[bone]
    results[bone] = first.rotation_difference(current)

    for child in skeleton.relations.get(bone, []):
        self.calculate_rotations(child, skeleton, first_pose, pose, results, bone)
