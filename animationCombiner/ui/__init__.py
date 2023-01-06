import bpy
from bpy.types import Context

from animationCombiner.operators import Empty, RunAnimationOperator, BackToStartOperator
from animationCombiner.operators.files.importer import ImportActionOperator
from animationCombiner.operators.process import ProcessOperator


class ACTIONS_UL_name(bpy.types.UIList):
    # The draw_item function is called for each item of the collection that is visible in the list.
    #   data is the RNA object containing the collection,
    #   item is the current drawn item of the collection,
    #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
    #   have custom icons ID, which are not available as enum items).
    #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
    #   active item of the collection).
    #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
    #   index is index of the current item in the collection.
    #   flt_flag is the result of the filtering process for this item.
    #   Note: as index and flt_flag are optional arguments, you do not have to use/declare them here if you don't
    #         need them.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, **kwargs):
        ob = data
        slot = item
        ma = slot
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            if ma:
                layout.prop(ma, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="", translate=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class UIListPanelExample1(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "Actions"
    # bl_idname = "OBJECT_PT_ui_list_example_1"
    bl_idname = "VIEW3D_PT_example_panel"
    # bl_label = 'Example Panel'
    # bl_space_type = 'PROPERTIES'
    # bl_region_type = 'WINDOW'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnimationCombiner"
    bl_context = ".posemode"

    @classmethod
    def poll(cls, context):
        return context.object.name == "Armature"

    def draw(self, context):
        obj = context.object.data
        layout = self.layout
        layout.label(text="Actions that will be processed")
        #
        # # template_list now takes two new args.
        # # The first one is the identifier of the registered UIList to use (if you want only the default list,
        # # with no custom draw code, use "UI_UL_list").
        layout.template_list("ACTIONS_UL_name", "", obj, "actions", obj, "active")
        layout.separator()
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator(Empty.bl_idname, text="Add", icon="ADD")
        row.operator(Empty.bl_idname, text="Remove", icon="REMOVE")
        col.operator(ProcessOperator.bl_idname, text="Process", icon="WORKSPACE")
        # # The second one can usually be left as an empty string.
        # # It's an additional ID used to distinguish lists in case you use the same list several times in a given area.
        # layout.template_list("ActionsList", "compact", obj, "actions",
        #                      obj, "active_material_index", type='COMPACT')


class ControlPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "Controls"
    bl_idname = "VIEW3D_PT_controls"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnimationCombiner"
    bl_context = ".posemode"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        col.prop(bpy.context.scene.render, "fps", text="FPS", slider=True)
        row.operator(RunAnimationOperator.bl_idname, text="Play", icon="PLAY")
        row.operator(BackToStartOperator.bl_idname, text="Back To Start", icon="PREV_KEYFRAME")


class ImportPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "Import/Export"
    bl_idname = "VIEW3D_PT_import"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnimationCombiner"
    bl_context = ".posemode"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator(ImportActionOperator.bl_idname, text="Import", icon="IMPORT")
        row.operator(Empty.bl_idname, text="Export", icon="EXPORT")
