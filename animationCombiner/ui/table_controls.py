from bpy.props import EnumProperty, CollectionProperty


class BaseControlsMixin:
    """Base class for ControlMixins"""

    @property
    def active(self):
        return 0

    @active.setter
    def active(self, active):
        pass

    def callback(self):
        pass

    @property
    def list(self) -> CollectionProperty:
        return []


class BaseDeleteItem(BaseControlsMixin):
    """Base class for deleting the selected item."""

    bl_label = "Deletes an item"

    def execute(self, context):
        index = self.active

        self.list.remove(index)
        self.active = min(max(0, index - 1), len(self.list) - 1)
        self.callback()
        return {"FINISHED"}


class BaseMoveItem(BaseControlsMixin):
    """Base class for moving the selected item up/down."""

    bl_label = "Move an item in the list"

    direction: EnumProperty(
        items=(
            ("UP", "Up", ""),
            ("DOWN", "Down", ""),
        )
    )

    def move_index(self):
        """Move index of an item render queue while clamping it."""

        index = self.active
        list_length = len(self.list) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == "UP" else 1)

        self.active = max(0, min(new_index, list_length))
        if index != self.active:
            self.callback()

    def execute(self, context):
        my_list = self.list
        index = self.active

        neighbor = index + (-1 if self.direction == "UP" else 1)
        my_list.move(neighbor, index)
        self.move_index()

        return {"FINISHED"}
