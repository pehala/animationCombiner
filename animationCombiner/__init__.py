"""Core module of the plugin"""
import bpy

from animationCombiner import registry

bl_info = {
    "name": "Animation Combiner",
    "author": "phala",
    "description": "Blender plugin for crafting new animations from existing ones",
    "version": (0, 0, 1),
    "blender": (3, 0, 0),
    "location": "View3D -> Animation",
    "warning": "",
    "category": "Animation",
}


def register():
    """Register all custom classes"""
    registry.init()
    registry.register()


def unregister():
    """Unregister all custom classes"""
    registry.unregister()

