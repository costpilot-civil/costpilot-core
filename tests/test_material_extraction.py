from pathlib import Path

import pytest

from costpilot_core.material.attribute_extractor import AttributeExtractor
from costpilot_core.material.config_loader import MaterialConfigLoader


@pytest.fixture
def concrete_template(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    registry = root / "config/materials/materials_registry.yaml"
    monkeypatch.setenv("MATERIALS_CONFIG_PATH", str(registry))
    return MaterialConfigLoader().load_all()["concrete"]


def extract(text, template):
    result = AttributeExtractor().extract(text, template)
    return {**result.core_attributes, **result.supplementary_attributes}


def test_concrete_grade_with_spacing(concrete_template):
    data = extract("Normalbeton C 30 / 37, XC3, XF1", concrete_template)
    assert data["strength_class"] == "C30/37"
    assert data["exposure_class"] == {"xc": "XC3", "xf": "XF1"}


def test_lightweight_grade_not_confused(concrete_template):
    data = extract("Leichtbeton LC12/13", concrete_template)
    assert data["strength_class"] == "LC12/13"


def test_explicit_numeric_context(concrete_template):
    data = extract("Beton C30/37, Bauteildicke 200 mm, Größtkorn 16 mm", concrete_template)
    assert data["max_aggregate_size"] == 16


def test_no_guess_from_unrelated_number(concrete_template):
    data = extract("Beton C30/37, Bauteildicke 200 mm", concrete_template)
    assert "max_aggregate_size" not in data


def test_conflicting_numbers_are_skipped(concrete_template):
    data = extract("Beton mit Größtkorn 16 mm und Größtkorn 32 mm", concrete_template)
    assert "max_aggregate_size" not in data


def test_numeric_ratio_and_constraint_skipped(concrete_template):
    data = extract("Beton w/z = 0,45", concrete_template)
    assert data["water_cement_ratio"] == 0.45
    data = extract("Beton w/z <= 0,45", concrete_template)
    assert "water_cement_ratio" not in data


def test_applications_and_sichtbeton(concrete_template):
    data = extract("Sichtbeton SB 2 für Sauberkeitsschicht und Fundamente", concrete_template)
    assert data["exposed_concrete_class"] == "SB2"
    assert "Sauberkeitsschicht" in data["applications"]


def test_aliases(concrete_template):
    data = extract("Hochfester Beton für Fundamente", concrete_template)
    assert "Hochfester_Beton" in data["special_properties"]
    assert "Fundamentbeton" in data["applications"]


def test_conflicting_single_attribute_is_skipped(concrete_template):
    data = extract("Beton C12/15 und C30/37 mit XC3", concrete_template)
    assert "strength_class" not in data
    assert data["exposure_class"] == {"xc": "XC3"}


def test_ambiguous_sichtbeton_class_is_skipped(concrete_template):
    data = extract("Sichtbeton SB1 sowie SB2", concrete_template)
    assert "exposed_concrete_class" not in data


def test_no_inference_of_normalbeton(concrete_template):
    data = extract("Beton C12/15-X0", concrete_template)
    assert "concrete_type" not in data


def test_other_numeric_without_patterns_skipped(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.setenv("MATERIALS_CONFIG_PATH", str(root / "config/materials/materials_registry.yaml"))
    template = MaterialConfigLoader().load_all()["reinforcing_steel"]
    data = extract("Betonstahl B500B d=16 mm", template)
    assert "diameter" not in data
