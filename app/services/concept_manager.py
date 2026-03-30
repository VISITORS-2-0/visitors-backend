import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
from app.models.schemas import ConceptSchema
from app.core.config import settings


class ConceptManager:
    """
    Reads concept metadata (type + allowed values) directly from the
    TakEntities XML files.  For concept-types that carry a <values> tag
    (state, pattern, raw-nominal, trend) the allowed values are extracted
    from the XML.  For raw-numeric the concept is returned with an empty
    allowed_values dict (i.e. treated as raw / continuous).
    """

    # In-memory cache so we parse each XML file only once per process.
    _cache: Dict[str, ConceptSchema] = {}

    @staticmethod
    def get_or_create_concept(concept_name: str) -> ConceptSchema:
        if concept_name in ConceptManager._cache:
            return ConceptManager._cache[concept_name]

        schema = ConceptManager._parse_from_xml(concept_name)
        if schema is not None:
            ConceptManager._cache[concept_name] = schema
            return schema

        # Fallback: concept not found in TakEntities – return a bare schema
        fallback = ConceptSchema(
            name=concept_name,
            type="unknown",
            allowed_values={}
        )
        ConceptManager._cache[concept_name] = fallback
        return fallback

    # ------------------------------------------------------------------
    # XML helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_from_xml(concept_name: str) -> Optional[ConceptSchema]:
        """
        Look for an XML file whose root-element ``name`` attribute matches
        *concept_name*.  We first try the obvious filename
        ``<concept_name>.xml``; if that does not exist we fall back to a
        linear scan of the directory.
        """
        tak_dir = settings.TAK_FILES_DIR

        # Fast path – filename matches concept name
        candidate = os.path.join(tak_dir, f"{concept_name}.xml")
        if os.path.isfile(candidate):
            return ConceptManager._parse_single_xml(candidate)

        # Slow path – scan every file (handles renames / casing mismatches)
        for fname in os.listdir(tak_dir):
            if not fname.endswith(".xml"):
                continue
            fpath = os.path.join(tak_dir, fname)
            try:
                tree = ET.parse(fpath)
                root = tree.getroot()
                if root.attrib.get("name") == concept_name:
                    return ConceptManager._parse_single_xml(fpath)
            except ET.ParseError:
                continue

        return None

    @staticmethod
    def _parse_single_xml(filepath: str) -> ConceptSchema:
        tree = ET.parse(filepath)
        root = tree.getroot()

        concept_name = root.attrib.get("name", os.path.basename(filepath).replace(".xml", ""))
        concept_type = root.attrib.get("concept-type", "unknown")

        allowed_values: Dict[str, Any] = {}

        # For types that have a <values> tag, extract the allowed values
        values_el = root.find(".//values")
        if values_el is not None:
            vals: List[str] = []
            ordering: Optional[str] = None

            for child in values_el:
                val = child.attrib.get("value")
                if val is not None:
                    vals.append(val)

                # ordinal-allowed-value carries an 'order' attr -> ordinal ordering
                if "order" in child.attrib:
                    ordering = "asc"

            allowed_values["values"] = vals
            if ordering:
                allowed_values["ordering"] = ordering

        # For raw-numeric: allowed_values stays empty – treated as raw / continuous

        return ConceptSchema(
            name=concept_name,
            type=concept_type,
            allowed_values=allowed_values
        )
