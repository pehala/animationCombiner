from bpy.types import Menu

from animationCombiner.parsers import exporters, importers


class ExporterMenu(Menu):
    bl_idname = "AC_MT_EXPORTERS"
    bl_label = "Select Exporter"

    def draw(self, context):
        layout = self.layout

        for name, exporter in exporters.parsers.items():
            layout.operator(exporter.bl_idname, text=name)


class ImporterMenu(Menu):
    bl_idname = "AC_MT_Importers"
    bl_label = "Select Importer"

    def draw(self, context):
        layout = self.layout

        for name, exporter in importers.parsers.items():
            layout.operator(exporter.bl_idname, text=name)
