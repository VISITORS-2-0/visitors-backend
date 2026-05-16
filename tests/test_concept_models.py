import unittest

from app.models.concept import (
    NominalRawConcept,
    NumericRawConcept,
    Pattern,
    State,
    TAKEntity,
    parse_mapping_abstractions,
)


class ConceptModelTests(unittest.TestCase):
    def test_derived_from_accepts_nested_string_and_list_shapes(self):
        nested_string = TAKEntity(**{"@id": "1", "@name": "Child", "derived-from": {"derived-from-id": "parent"}})
        nested_list = TAKEntity(**{"@id": "2", "@name": "Child2", "derived-from": {"derived-from-id": [1, "2"]}})

        self.assertEqual(nested_string.derived_from, ["parent"])
        self.assertEqual(nested_list.derived_from, ["1", "2"])

    def test_numeric_raw_concept_extracts_min_max_and_types(self):
        concept = NumericRawConcept(
            **{
                "@id": "lab",
                "@name": "Lab",
                "@concept-type": "raw-numeric",
                "numeric-allowed-values": {"@min-value": "1.5", "@max-value": "9.5"},
            }
        )

        self.assertEqual(concept.min, 1.5)
        self.assertEqual(concept.max, 9.5)
        self.assertEqual(concept.output_type, "range")
        self.assertEqual(concept.duration_type, "point")

    def test_nominal_and_state_concepts_extract_allowed_values(self):
        nominal = NominalRawConcept(
            **{
                "@id": "sex",
                "@name": "Sex",
                "@concept-type": "raw-nominal",
                "nominal-allowed-values": {
                    "values": {
                        "nominal-allowed-value": [{"@value": "M"}, {"@value": "F"}],
                    }
                },
            }
        )
        state = State(
            **{
                "@id": "status",
                "@name": "Status",
                "@concept-type": "state",
                "ordinal-allowed-values": {
                    "values": {
                        "ordinal-allowed-value": {"@value": "True"},
                    }
                },
            }
        )

        self.assertEqual(nominal.values, ["M", "F"])
        self.assertEqual(state.values, ["True"])
        self.assertEqual(nominal.output_type, "categorial")
        self.assertEqual(state.duration_type, "interval")

    def test_pattern_defaults_to_true_when_no_range_or_values_exist(self):
        pattern = Pattern(**{"@id": "p", "@name": "Pattern", "@concept-type": "pattern"})

        self.assertEqual(pattern.values, ["True"])
        self.assertEqual(pattern.output_type, "categorial")

    def test_parse_mapping_abstractions_compresses_and_conditions_for_same_concept(self):
        raw_data = {
            "mapping-function": {
                "mapping-functions-to-values": {
                    "mapping-function-2-value": {
                        "@order": "1",
                        "@value": "Normal",
                        "evaluation-tree": {
                            "logical-function": {
                                "@logical-operator": "and",
                                "operands": {
                                    "operand": [
                                        {
                                            "comparison-function": {
                                                "@comparison-operator": "bigger-equal",
                                                "left": {"concept-id-allowed-values": {"@id": "lab"}},
                                                "right": {"double": "10"},
                                            }
                                        },
                                        {
                                            "comparison-function": {
                                                "@comparison-operator": "smaller",
                                                "left": {"concept-id-allowed-values": {"@id": "lab"}},
                                                "right": {"double": "20"},
                                            }
                                        },
                                    ]
                                },
                            }
                        },
                    }
                }
            }
        }

        result = parse_mapping_abstractions(raw_data, lambda concept_id: {"lab": "Lab Result"}[concept_id])

        self.assertEqual(len(result.category_mappings), 1)
        mapping = result.category_mappings[0]
        self.assertEqual(mapping.order, 1)
        self.assertEqual(mapping.category, "Normal")
        self.assertIsNone(mapping.logical_operation)
        self.assertEqual(mapping.conditions[0].abstracted_from_concept, "Lab Result")
        self.assertEqual(mapping.conditions[0].values_accepted, ">=10 and <20")


if __name__ == "__main__":
    unittest.main()
