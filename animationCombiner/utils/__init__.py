"""Collection of all utility functions/classes that didnt fit anywhere else"""
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
