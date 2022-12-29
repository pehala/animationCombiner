"""Core module of the plugin"""
import bpy

from animationCombiner import registry

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
    registry.init()
    registry.register()


def unregister():
    """Unregister all custom classes"""
    registry.unregister()

