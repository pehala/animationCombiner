"""Core module of the plugin"""
import bpy

from .registry import CLASSES, registered_classes

bl_info = {
    "name": "animationCombiner",
    "author": "phala",
    "description": "Blender plugin for crafting new animations from existing ones ",
    "blender": (3, 0, 0),
    "location": "View3D",
    "warning": "",
    "category": "Generic",
}


def register():
    """Register all custom classes"""
    # register classes so blender knows about them
    for clazz in registered_classes():
        try:
            bpy.utils.register_class(clazz)
        except RuntimeError as err:
            raise ImportError(f"Unable to unregister class {clazz}") from err


def unregister():
    """Unregister all custom classes"""
    for clazz in registered_classes():
        try:
            bpy.utils.unregister_class(clazz)
        except RuntimeError as err:
            raise ImportError(f"Unable to unregister class {clazz}") from err
