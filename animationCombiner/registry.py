import importlib
import inspect
import pathlib
import pkgutil

__all__ = ["register_class", "registered_classes", "AutoRegister"]

CLASSES = {}
discovered = False
print(str(pathlib.Path(__file__).parent.resolve()))


def register_class(clazz):
    CLASSES[clazz] = None
    return clazz


def registered_classes():
    global discovered
    if not discovered:
        discovered = True
        autodiscover()
    return CLASSES.keys()


def autodiscover():
    for _, module, _ in pkgutil.walk_packages(
        [str(pathlib.Path(__file__).parent.resolve())], prefix="animationCombiner."
    ):
        imported = importlib.import_module(module)
        for item in dir(imported):
            obj = getattr(imported, item)
            if inspect.isclass(obj) and issubclass(obj, AutoRegister) and AutoRegister != obj:
                CLASSES[obj] = None


class AutoRegister:
    @classmethod
    def register(cls):
        pass

    @classmethod
    def unregister(cls):
        pass
