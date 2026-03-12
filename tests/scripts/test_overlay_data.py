#!/usr/bin/env python3
"""
Stratoterra — Intel Overlay Data Tests

Validates all 12 overlay JSON files in data/chunks/global/overlays/.
Checks: existence, structure, count consistency, coordinate validity.
"""

import json
import os
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OVERLAYS_DIR = os.path.join(REPO_ROOT, "data", "chunks", "global", "overlays")

LAYER_IDS = [
    "airports", "ports", "bases", "conflicts", "power", "nuclear",
    "missiles", "chokepoints", "cables", "pipelines", "cyber", "sanctions",
]

REQUIRED_FIELDS = {"layer", "generated_at", "count", "features"}

# Layers that use 'll' (lat/lon point) vs 'path' (polyline)
POINT_LAYERS = {"airports", "ports", "bases", "conflicts", "power", "nuclear",
                "missiles", "chokepoints", "cyber", "sanctions"}
PATH_LAYERS = {"cables", "pipelines"}


def load_overlay(layer_id):
    path = os.path.join(OVERLAYS_DIR, f"{layer_id}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestOverlayFilesExist(unittest.TestCase):
    """All 15 overlay JSON files must exist and be valid JSON."""

    def test_all_overlay_files_exist(self):
        missing = []
        for layer_id in LAYER_IDS:
            path = os.path.join(OVERLAYS_DIR, f"{layer_id}.json")
            if not os.path.isfile(path):
                missing.append(layer_id)
        self.assertEqual(missing, [], f"Missing overlay files: {missing}")

    def test_all_overlay_files_parse_as_json(self):
        errors = []
        for layer_id in LAYER_IDS:
            path = os.path.join(OVERLAYS_DIR, f"{layer_id}.json")
            if not os.path.isfile(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                errors.append(f"{layer_id}: {e}")
        self.assertEqual(errors, [], "JSON parse errors:\n" + "\n".join(errors))


class TestOverlayStructure(unittest.TestCase):
    """Each overlay file must have required metadata fields."""

    def test_required_fields_present(self):
        errors = []
        for layer_id in LAYER_IDS:
            path = os.path.join(OVERLAYS_DIR, f"{layer_id}.json")
            if not os.path.isfile(path):
                continue
            data = load_overlay(layer_id)
            missing = REQUIRED_FIELDS - set(data.keys())
            if missing:
                errors.append(f"{layer_id}: missing {sorted(missing)}")
        self.assertEqual(errors, [], "Missing required fields:\n" + "\n".join(errors))

    def test_layer_field_matches_filename(self):
        errors = []
        for layer_id in LAYER_IDS:
            path = os.path.join(OVERLAYS_DIR, f"{layer_id}.json")
            if not os.path.isfile(path):
                continue
            data = load_overlay(layer_id)
            if data.get("layer") != layer_id:
                errors.append(f"{layer_id}: layer field is '{data.get('layer')}'")
        self.assertEqual(errors, [], "Layer field mismatches:\n" + "\n".join(errors))

    def test_count_matches_features_length(self):
        errors = []
        for layer_id in LAYER_IDS:
            path = os.path.join(OVERLAYS_DIR, f"{layer_id}.json")
            if not os.path.isfile(path):
                continue
            data = load_overlay(layer_id)
            declared = data.get("count", -1)
            actual = len(data.get("features", []))
            if declared != actual:
                errors.append(f"{layer_id}: count={declared}, features length={actual}")
        self.assertEqual(errors, [], "Count mismatches:\n" + "\n".join(errors))

    def test_no_empty_features(self):
        errors = []
        for layer_id in LAYER_IDS:
            path = os.path.join(OVERLAYS_DIR, f"{layer_id}.json")
            if not os.path.isfile(path):
                continue
            data = load_overlay(layer_id)
            if len(data.get("features", [])) == 0:
                errors.append(f"{layer_id}: features array is empty")
        self.assertEqual(errors, [], "Empty features:\n" + "\n".join(errors))


class TestOverlayCoordinates(unittest.TestCase):
    """Coordinate validation for point and path layers."""

    def _validate_point(self, ll, context):
        """Validate a [lat, lon] point."""
        errors = []
        if not isinstance(ll, list) or len(ll) != 2:
            errors.append(f"{context}: ll must be [lat, lon], got {ll}")
            return errors
        lat, lon = ll
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            errors.append(f"{context}: non-numeric coordinates {ll}")
            return errors
        if lat < -90 or lat > 90:
            errors.append(f"{context}: lat {lat} out of range [-90, 90]")
        if lon < -180 or lon > 180:
            errors.append(f"{context}: lon {lon} out of range [-180, 180]")
        return errors

    def test_point_layer_coordinates(self):
        errors = []
        for layer_id in POINT_LAYERS:
            path = os.path.join(OVERLAYS_DIR, f"{layer_id}.json")
            if not os.path.isfile(path):
                continue
            data = load_overlay(layer_id)
            for i, feat in enumerate(data.get("features", [])):
                ll = feat.get("ll")
                if ll is None:
                    errors.append(f"{layer_id}[{i}]: missing 'll' field")
                    continue
                ctx = f"{layer_id}[{i}] {feat.get('name', '?')}"
                errors.extend(self._validate_point(ll, ctx))
        self.assertEqual(errors, [], "Point coordinate errors:\n" + "\n".join(errors))

    def test_path_layer_coordinates(self):
        errors = []
        for layer_id in PATH_LAYERS:
            path_file = os.path.join(OVERLAYS_DIR, f"{layer_id}.json")
            if not os.path.isfile(path_file):
                continue
            data = load_overlay(layer_id)
            for i, feat in enumerate(data.get("features", [])):
                path_coords = feat.get("path")
                if path_coords is None:
                    errors.append(f"{layer_id}[{i}]: missing 'path' field")
                    continue
                if not isinstance(path_coords, list) or len(path_coords) < 2:
                    errors.append(f"{layer_id}[{i}]: path must have >= 2 points")
                    continue
                name = feat.get("name") or feat.get("label") or "?"
                for j, pt in enumerate(path_coords):
                    ctx = f"{layer_id}[{i}] {name} pt[{j}]"
                    errors.extend(self._validate_point(pt, ctx))
        self.assertEqual(errors, [], "Path coordinate errors:\n" + "\n".join(errors))

    def test_every_feature_has_name_or_label(self):
        """Every feature must have a 'name' or 'label' field for display."""
        errors = []
        for layer_id in LAYER_IDS:
            path = os.path.join(OVERLAYS_DIR, f"{layer_id}.json")
            if not os.path.isfile(path):
                continue
            data = load_overlay(layer_id)
            for i, feat in enumerate(data.get("features", [])):
                if not feat.get("name") and not feat.get("label"):
                    errors.append(f"{layer_id}[{i}]: missing 'name' and 'label'")
        self.assertEqual(errors, [], "Features without name/label:\n" + "\n".join(errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
