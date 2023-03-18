from bpy.types import Panel, Context

from animationCombiner.ui import MainPanel
from animationCombiner.utils.weakget import weakget


class ActionPanel(Panel):
    """Panel containing list of actions."""

    bl_label = "Actions"
    bl_idname = "AC_PT_actions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = MainPanel.bl_idname
    bl_context = ".posemode"
    bl_order = 20

    @classmethod
    def poll(cls, context):
        return weakget(context).object.type % "NONE" == "ARMATURE" and weakget(context).object.data % False

    def draw(self, context):
        pass


class EditActionPanel(Panel):
    bl_label = "Edit Action"
    bl_idname = "AC_PT_edit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = ActionPanel.bl_idname
    bl_order = 20

    @classmethod
    def poll(cls, context):
        if weakget(context).object.type % "NONE" != "ARMATURE" or not weakget(context).object.data % False:
            return False
        armature = context.object.data
        if armature.active < 0 or not armature.groups:
            return False
        group = armature.groups[armature.active]
        return group.active >= 0 and group.actions

    def active_action(self, context):
        group = context.object.data.groups[context.object.data.active]
        return group.actions[group.active]

    def draw(self, context: Context) -> None:
        item = self.active_action(context)
        col = self.layout.column(align=True)
        item.draw(col)
