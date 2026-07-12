"""Tests for the domain classification engine — generic matching + crossplane rules."""

import pytest
from pathlib import Path

from okf.domains.engine import (
    classify, load_rules, _matches_conditions, _extract_field, _deep_get
)
from okf.parsers.base import Concept


# ── _deep_get tests ─────────────────────────────────────────────────────────

def test_deep_get_simple():
    doc = {"apiVersion": "v1", "kind": "Pod", "metadata": {"name": "nginx"}}
    assert _deep_get(doc, "apiVersion") == "v1"
    assert _deep_get(doc, "kind") == "Pod"
    assert _deep_get(doc, "metadata.name") == "nginx"
    assert _deep_get(doc, "nonexistent") is None


def test_deep_get_list_index():
    doc = {"spec": {"containers": [{"name": "nginx", "image": "nginx:1.25"}]}}
    assert _deep_get(doc, "spec.containers[0].name") == "nginx"
    assert _deep_get(doc, "spec.containers[0].image") == "nginx:1.25"


def test_deep_get_list_wildcard():
    doc = {"spec": {"containers": [{"name": "nginx"}]}}
    assert _deep_get(doc, "spec.containers[*].name") == "nginx"


def test_deep_get_nested_missing():
    doc = {"kind": "Pod"}
    assert _deep_get(doc, "spec.containers") is None


# ── _matches_conditions tests ───────────────────────────────────────────────

def test_match_exact():
    doc = {"kind": "Composition", "apiVersion": "apiextensions.crossplane.io/v1"}
    assert _matches_conditions(doc, {"kind": "Composition"})
    assert not _matches_conditions(doc, {"kind": "XRD"})


def test_match_glob():
    doc = {"apiVersion": "apiextensions.crossplane.io/v1"}
    assert _matches_conditions(doc, {"apiVersion": {"$glob": "apiextensions.crossplane.io/*"}})
    assert not _matches_conditions(doc, {"apiVersion": {"$glob": "aws.crossplane.io/*"}})


def test_match_multiple_conditions():
    doc = {"apiVersion": "apiextensions.crossplane.io/v1", "kind": "Composition"}
    match = {"apiVersion": {"$glob": "apiextensions.crossplane.io/*"}, "kind": "Composition"}
    assert _matches_conditions(doc, match)
    assert not _matches_conditions(doc, {**match, "kind": "XRD"})


def test_match_default_with_require_keys():
    doc = {"apiVersion": "v1", "kind": "Pod"}
    assert _matches_conditions(doc, {"default": True, "require_keys": ["apiVersion", "kind"]})

    doc2 = {"name": "config"}
    assert not _matches_conditions(doc2, {"default": True, "require_keys": ["apiVersion", "kind"]})


def test_match_default_no_keys():
    doc = {"random": "data"}
    assert _matches_conditions(doc, {"default": True})


# ── _extract_field tests ────────────────────────────────────────────────────

def test_extract_simple():
    doc = {"spec": {"group": "example.org"}}
    assert _extract_field(doc, "spec.group") == "example.org"


def test_extract_nested_with_list():
    doc = {
        "spec": {
            "versions": [{"name": "v1alpha1", "schema": {"openAPIV3Schema": {"properties": {"spec": {"type": "object"}}}}}]
        }
    }
    assert _extract_field(doc, "spec.versions[0].name") == "v1alpha1"


# ── classify tests ──────────────────────────────────────────────────────────

def _make_concept(title: str, type_: str = "Resource", yaml_doc: dict | None = None,
                  cid: str = "") -> Concept:
    return Concept(
        type=type_, title=title, resource="test.yaml",
        tags=["yaml"], concept_id=cid or title,
        body_extra={"yaml_doc": yaml_doc or {}},
    )


def test_classify_retype():
    """Rule matches by kind and changes type."""
    concepts = [_make_concept("Composition", yaml_doc={
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "Composition",
    })]
    rules = [{
        "match": {"apiVersion": {"$glob": "apiextensions.crossplane.io/*"}, "kind": "Composition"},
        "type": "Composition",
        "add_tags": ["domain:crossplane"],
    }]
    result = classify(concepts, rules)
    assert result[0].type == "Composition"
    assert "domain:crossplane" in result[0].tags


def test_classify_add_tags():
    concepts = [_make_concept("XPostgreSQLInstance", yaml_doc={
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "CompositeResourceDefinition",
    })]
    rules = [{
        "match": {"kind": "CompositeResourceDefinition"},
        "type": "XRD",
        "add_tags": ["domain:crossplane", "xrd"],
    }]
    result = classify(concepts, rules)
    assert "domain:crossplane" in result[0].tags
    assert "xrd" in result[0].tags


def test_classify_extract_fields():
    concepts = [_make_concept("xpostgresqlinstances.example.org", yaml_doc={
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "CompositeResourceDefinition",
        "spec": {"group": "example.org", "names": {"kind": "XPostgreSQLInstance"}},
    })]
    rules = [{
        "match": {"kind": "CompositeResourceDefinition"},
        "type": "XRD",
        "extract": [
            {"from": "spec.group", "to": "returns"},
            {"from": "spec.names.kind", "to": "signature"},
        ],
    }]
    result = classify(concepts, rules)
    assert result[0].returns == "example.org"
    assert result[0].signature == "XPostgreSQLInstance"


def test_classify_first_match_wins():
    """Only the first matching rule is applied."""
    concepts = [_make_concept("MyResource", yaml_doc={
        "apiVersion": "v1", "kind": "Pod",
    })]
    rules = [
        {"match": {"kind": "Pod"}, "type": "Pod", "add_tags": ["first"]},
        {"match": {"apiVersion": "v1"}, "type": "V1Resource", "add_tags": ["second"]},
    ]
    result = classify(concepts, rules)
    assert result[0].type == "Pod"
    assert "first" in result[0].tags
    assert "second" not in result[0].tags


def test_classify_catch_all_with_guard():
    """Catch-all with require_keys only matches docs that have those keys."""
    k8s_doc = _make_concept("nginx", yaml_doc={"apiVersion": "v1", "kind": "Pod"})
    config_doc = _make_concept("config", yaml_doc={"name": "config"})
    rules = [{
        "match": {"default": True, "require_keys": ["apiVersion", "kind"]},
        "type": "ManagedResource",
    }]
    result = classify([k8s_doc, config_doc], rules)
    assert result[0].type == "ManagedResource"
    assert result[1].type == "Resource"  # unchanged


def test_classify_no_match_leaves_unchanged():
    concepts = [_make_concept("random", yaml_doc={"color": "blue"})]
    rules = [{"match": {"kind": "Pod"}, "type": "Pod"}]
    result = classify(concepts, rules)
    assert result[0].type == "Resource"  # default type from fixture


def test_classify_no_yaml_doc():
    """Concepts without body_extra.yaml_doc are never matched."""
    c = Concept(type="Module", title="main.py", resource="main.py",
                tags=["python"], concept_id="main")
    result = classify([c], [{"match": {"default": True}, "type": "Something"}])
    assert result[0].type == "Module"


# ── Linker tests ────────────────────────────────────────────────────────────

def test_classify_link_xrd_to_composition():
    """Composition links to XRD via compositeTypeRef."""
    xrd = _make_concept("XPostgreSQLInstance", type_="XRD", cid="xrd",
                        yaml_doc={"apiVersion": "example.org/v1", "kind": "XPostgreSQLInstance"})
    comp = _make_concept("comp", type_="Composition", cid="comp",
                         yaml_doc={
                             "apiVersion": "apiextensions.crossplane.io/v1",
                             "kind": "Composition",
                             "spec": {
                                 "compositeTypeRef": {
                                     "apiVersion": "example.org/v1",
                                     "kind": "XPostgreSQLInstance",
                                 }
                             },
                         })
    rules = [
        {"match": {"kind": "CompositeResourceDefinition"}, "type": "XRD"},
        {"match": {"kind": "Composition"}, "type": "Composition",
         "links": [{"field": "spec.compositeTypeRef", "target_type": "XRD",
                     "match_on": ["apiVersion", "kind"]}]},
    ]
    result = classify([xrd, comp], rules)
    comp_result = [c for c in result if c.concept_id == "comp"][0]
    assert "xrd" in comp_result.related


# ── load_rules tests ────────────────────────────────────────────────────────

def test_load_rules_builtin():
    """Built-in crossplane rules load without error."""
    rules = load_rules(domain_names=["crossplane"])
    assert len(rules) >= 5, f"Expected >=5 crossplane rules, got {len(rules)}"
    domains = {r.get("_domain") for r in rules}
    assert "crossplane" in domains


def test_list_domains():
    from okf.domains.engine import list_domains
    domains = list_domains()
    assert len(domains) >= 1
    assert any(d["domain"] == "crossplane" for d in domains)
    assert any(d["source"].startswith("builtin") for d in domains)


# ── Crossplane integration ──────────────────────────────────────────────────

def test_crossplane_xrd_classification():
    rules = load_rules(domain_names=["crossplane"])
    c = _make_concept("xpostgresqlinstances.example.org", yaml_doc={
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "CompositeResourceDefinition",
        "spec": {"group": "example.org", "names": {"kind": "XPostgreSQLInstance"},
                 "versions": [{"name": "v1alpha1", "schema": {"openAPIV3Schema": {"properties": {}}}}]},
    })
    result = classify([c], rules)
    assert result[0].type == "XRD"
    assert "domain:crossplane" in result[0].tags


def test_crossplane_composition_classification():
    rules = load_rules(domain_names=["crossplane"])
    c = _make_concept("comp", yaml_doc={
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "Composition",
        "spec": {"compositeTypeRef": {"apiVersion": "example.org/v1", "kind": "XPostgreSQLInstance"}},
    })
    result = classify([c], rules)
    assert result[0].type == "Composition"


def test_crossplane_provider_config_classification():
    rules = load_rules(domain_names=["crossplane"])
    c = _make_concept("default", yaml_doc={
        "apiVersion": "aws.crossplane.io/v1beta1", "kind": "ProviderConfig",
        "spec": {"credentials": {"source": "Secret"}},
    })
    result = classify([c], rules)
    assert result[0].type == "ProviderConfig"


def test_crossplane_catch_all_only_k8s_resources():
    """Catch-all should NOT match non-k8s YAML (no apiVersion)."""
    rules = load_rules(domain_names=["crossplane"])
    c = _make_concept("config", yaml_doc={"name": "app-config", "data": {"KEY": "val"}})
    result = classify([c], rules)
    assert result[0].type == "Resource"  # unchanged by catch-all


def test_crossplane_catch_all_matches_k8s_resource():
    """Catch-all should match k8s-like resources (apiVersion + kind)."""
    rules = load_rules(domain_names=["crossplane"])
    c = _make_concept("my-bucket", yaml_doc={
        "apiVersion": "s3.aws.crossplane.io/v1beta1",
        "kind": "Bucket",
    })
    result = classify([c], rules)
    assert result[0].type == "ManagedResource"


# ── has_key tests ────────────────────────────────────────────────────────────

def test_match_has_key_present():
    doc = {"spec": {"resources": [{"name": "r1"}]}}
    assert _matches_conditions(doc, {"has_key": "spec.resources"})


def test_match_has_key_missing():
    doc = {"spec": {"mode": "Pipeline"}}
    assert not _matches_conditions(doc, {"has_key": "spec.resources"})


def test_match_has_key_nested():
    doc = {"spec": {"pipeline": [{"step": "a"}], "compositeTypeRef": {"kind": "X"}}}
    assert _matches_conditions(doc, {"has_key": "spec.pipeline"})
    assert not _matches_conditions(doc, {"has_key": "spec.resources"})


# ── V1/V2 Composition tests ──────────────────────────────────────────────────

def test_v2_pipeline_composition_tagged():
    """V2 Pipeline Composition gets crossplane-v2-pipeline tag."""
    rules = load_rules(domain_names=["crossplane"])
    c = _make_concept("pipeline-comp", yaml_doc={
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "Composition",
        "spec": {
            "mode": "Pipeline",
            "pipeline": [{"functionRef": {"name": "function-kro"}, "step": "a"}],
            "compositeTypeRef": {"apiVersion": "example.org/v1", "kind": "XPostgreSQLInstance"},
        },
    })
    result = classify([c], rules)
    assert result[0].type == "Composition"
    assert "crossplane-v2-pipeline" in result[0].tags
    assert "crossplane-v1-style" not in result[0].tags


def test_v1_resources_composition_tagged():
    """V1 Resources Composition gets crossplane-v1-style tag."""
    rules = load_rules(domain_names=["crossplane"])
    c = _make_concept("resources-comp", yaml_doc={
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "Composition",
        "spec": {
            "resources": [{"name": "r1", "base": {"apiVersion": "v1", "kind": "Bucket"}}],
            "compositeTypeRef": {"apiVersion": "example.org/v1", "kind": "XPostgreSQLInstance"},
        },
    })
    result = classify([c], rules)
    assert result[0].type == "Composition"
    assert "crossplane-v1-style" in result[0].tags
    assert "crossplane-v2-pipeline" not in result[0].tags


def test_v2_pipeline_function_name_extracted():
    """Pipeline functionRef.name is extracted into concept fields."""
    rules = load_rules(domain_names=["crossplane"])
    c = _make_concept("fn-comp", yaml_doc={
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "Composition",
        "spec": {
            "mode": "Pipeline",
            "pipeline": [{"functionRef": {"name": "function-kro"}}],
            "compositeTypeRef": {"apiVersion": "example.org/v1", "kind": "XPostgreSQLInstance"},
        },
    })
    result = classify([c], rules)
    assert result[0].type == "Composition"
    field_names = [f["name"] for f in result[0].fields]
    assert "function-kro" in field_names


# ── validate_rule_file tests ─────────────────────────────────────────────────

def test_validate_rule_file_valid(tmp_path):
    from okf.domains.engine import validate_rule_file
    f = tmp_path / "test.yaml"
    f.write_text("""domain: test
rules:
  - name: rule1
    match:
      kind: "Pod"
    type: Pod
""")
    errors = validate_rule_file(f)
    assert errors == [], f"Unexpected errors: {errors}"


def test_validate_rule_file_missing_domain(tmp_path):
    from okf.domains.engine import validate_rule_file
    f = tmp_path / "bad.yaml"
    f.write_text("""rules: []
""")
    errors = validate_rule_file(f)
    assert any("domain" in e for e in errors)


def test_validate_rule_file_missing_match(tmp_path):
    from okf.domains.engine import validate_rule_file
    f = tmp_path / "bad.yaml"
    f.write_text("""domain: test
rules:
  - name: no-match
    type: Pod
""")
    errors = validate_rule_file(f)
    assert any("match" in e for e in errors)


def test_validate_rule_file_empty(tmp_path):
    from okf.domains.engine import validate_rule_file
    f = tmp_path / "bad.yaml"
    f.write_text("""domain: test
rules: []
""")
    errors = validate_rule_file(f)
    assert any("empty" in e for e in errors)


def test_validate_rule_file_bad_operator(tmp_path):
    from okf.domains.engine import validate_rule_file
    f = tmp_path / "bad.yaml"
    f.write_text("""domain: test
rules:
  - match:
      kind: {"$badop": "Pod"}
    type: Pod
""")
    errors = validate_rule_file(f)
    assert any("$badop" in e for e in errors)


def test_validate_rule_file_missing_extract_fields(tmp_path):
    from okf.domains.engine import validate_rule_file
    f = tmp_path / "bad.yaml"
    f.write_text("""domain: test
rules:
  - match:
      kind: "Pod"
    type: Pod
    extract:
      - from: spec.field
""")
    errors = validate_rule_file(f)
    assert any("to" in e for e in errors)
