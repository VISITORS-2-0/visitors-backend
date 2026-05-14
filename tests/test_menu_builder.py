import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app.services.menu_builder as menu_builder


class MenuBuilderTests(unittest.TestCase):
    def setUp(self):
        menu_builder._navigation_structure = menu_builder._init_navigation_structure()
        menu_builder._is_built = False

    def test_process_file_classifies_supported_concept_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            files = {
                "event.xml": '<event id="e1" name="Event A" concept-type="event" />',
                "context.xml": '<context id="c1" name="Context A" concept-type="context" />',
                "raw.xml": '<numeric-raw-concept id="r1" name="Raw A" concept-type="raw-numeric" />',
                "state.xml": '<state id="s1" name="State A" concept-type="state" />',
            }
            for filename, content in files.items():
                path = directory / filename
                path.write_text(content, encoding="utf-8")
                menu_builder.process_file(str(path), filename)

        structure = menu_builder.get_navigation_structure()
        self.assertEqual(structure["TakEntity"]["Event"][0]["name"], "Event A")
        self.assertEqual(structure["TakEntity"]["Context"][0]["name"], "Context A")
        self.assertEqual(structure["TakEntity"]["Concept"]["RawConcept"][0]["name"], "Raw A")
        self.assertEqual(structure["TakEntity"]["Concept"]["AbstractConcept"][0]["name"], "State A")

    def test_process_file_skips_missing_concept_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "missing.xml")
            path.write_text('<event id="e1" name="Event A" />', encoding="utf-8")

            with patch.object(menu_builder.logger, "warning"):
                menu_builder.process_file(str(path), "missing.xml")

        structure = menu_builder.get_navigation_structure()
        self.assertEqual(structure["TakEntity"]["Event"], [])

    def test_build_hierarchy_is_idempotent_after_first_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            Path(directory, "event.xml").write_text(
                '<event id="e1" name="Event A" concept-type="event" />',
                encoding="utf-8",
            )

            menu_builder.build_hierarchy(str(directory))
            first_result = menu_builder.get_navigation_structure()
            Path(directory, "event2.xml").write_text(
                '<event id="e2" name="Event B" concept-type="event" />',
                encoding="utf-8",
            )
            menu_builder.build_hierarchy(str(directory))

        self.assertIs(first_result, menu_builder.get_navigation_structure())
        self.assertEqual(len(menu_builder.get_navigation_structure()["TakEntity"]["Event"]), 1)


if __name__ == "__main__":
    unittest.main()
