import tempfile
import unittest
from pathlib import Path

from app.services.concept_manager import ConceptManager


class ConceptManagerTests(unittest.TestCase):
    def test_missing_directory_raises_file_not_found(self):
        manager = ConceptManager("/path/that/does/not/exist")

        with self.assertRaises(FileNotFoundError):
            manager.init_entities()

    def test_missing_required_name_or_id_raises_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "bad.xml").write_text(
                '<event id="event1" concept-type="event"></event>',
                encoding="utf-8",
            )
            manager = ConceptManager(tmp)

            with self.assertRaises(ValueError) as raised:
                manager.init_entities()

        self.assertIn("Missing '@name'", str(raised.exception))

    def test_loads_entities_and_resolves_relationships(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            Path(directory, "raw.xml").write_text(
                """
                <numeric-raw-concept id="raw1" name="Raw Lab" concept-type="raw-numeric">
                    <numeric-allowed-values min-value="0" max-value="10" />
                </numeric-raw-concept>
                """,
                encoding="utf-8",
            )
            Path(directory, "state.xml").write_text(
                """
                <state id="state1" name="Lab State" concept-type="state">
                    <derived-from>
                        <derived-from-id>raw1</derived-from-id>
                    </derived-from>
                    <ordinal-allowed-values>
                        <values>
                            <ordinal-allowed-value value="Low" />
                            <ordinal-allowed-value value="High" />
                        </values>
                    </ordinal-allowed-values>
                </state>
                """,
                encoding="utf-8",
            )
            Path(directory, "context.xml").write_text(
                """
                <context id="ctx1" name="Visit Context" concept-type="context">
                    <inducer-entities>
                        <inducer-entity id="raw1" />
                    </inducer-entities>
                </context>
                """,
                encoding="utf-8",
            )
            manager = ConceptManager(str(directory))

            manager.init_entities()

            raw = manager.get_entity_by_name("Raw Lab")
            state = manager.get_entity_by_id("state1")
            context = manager.get_entity_by_name("Visit Context")

            self.assertEqual(raw.min, 0)
            self.assertEqual(raw.max, 10)
            self.assertEqual(state.name, "Lab State")
            self.assertEqual(state.derived_from, ["Raw Lab"])
            self.assertEqual(raw.derived_into, ["Lab State"])
            self.assertEqual(raw.context, ["Visit Context"])
            self.assertEqual(context.context, ["Raw Lab"])
            self.assertIn("Raw Lab", manager.get_all_entities())
            self.assertEqual(manager.get_raw_xml_by_name("Raw Lab")["@id"], "raw1")


if __name__ == "__main__":
    unittest.main()
