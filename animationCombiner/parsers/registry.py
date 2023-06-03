from functools import partial


class ParserRegistry:
    def __init__(self, name, clazz) -> None:
        super().__init__()
        self.clazz = clazz
        self.name = name
        self.collection = {}

    def register(self, func=None, *, name):
        """Registers parser for specific extensions"""
        if not func:
            # The only drawback is that for functions there is no thing
            # like "self" - we have to rely on the decorator
            # function name on the module namespace
            return partial(self.register, name=name)
        if not issubclass(func, self.clazz):
            raise ValueError(f"Parsers need to be descendants of {self.clazz.__name__}")
        self.collection[name] = func
        return func

    @property
    def parsers(self):
        return self.collection
