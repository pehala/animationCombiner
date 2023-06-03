from animationCombiner.parsers.base.exporter import BaseExportOperator
from animationCombiner.parsers.base.importer import BaseImportOperator
from animationCombiner.parsers.registry import ParserRegistry


importers = ParserRegistry("importers", BaseImportOperator)
exporters = ParserRegistry("exporters", BaseExportOperator)
