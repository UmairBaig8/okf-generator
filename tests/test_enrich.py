"""Tests for okf.enrich — the Enricher contract and LLM enrichment functions.

The LLM client is mocked; these tests verify behavior (JSON parsing, fallbacks,
field population) without making network calls.
"""



from okf.parsers.base import Concept

# ── helpers ──────────────────────────────────────────────────────────────────

def _make_concept(**overrides) -> Concept:
    base = dict(
        type="Function",
        title="do_thing",
        description="",
        docstring="",
        signature="def do_thing(x, y):",
        resource="src/mod.py",
        source_lines=(1, 10),
        params=[{"name": "x", "annotation": "int"}, {"name": "y", "annotation": "str"}],
        returns="bool",
        tags=["lang:python"],
        concept_id="src/mod.py/do_thing",
        decorators=[],
        inheritance=[],
    )
    base.update(overrides)
    return Concept(**base)


class _FakeResponse:
    class _Details:
        reasoning_tokens = 0

    class _Usage:
        model = "test-model"
        prompt_tokens = 4
        completion_tokens = 6
        total_tokens = 10
        completion_tokens_details = None  # set in __init__

    def __init__(self, content: str):
        self.choices = [type("C", (), {"message": type("M", (), {"content": content})()})()]
        self.usage = self._Usage()
        self.usage.completion_tokens_details = self._Details()


class _FakeClient:
    """Records the prompt; returns scripted JSON content.

    Mirrors the OpenAI SDK shape: ``client.chat.completions.create(...)``
    (attribute access, not method calls).
    """

    def __init__(self, content: str):
        self.content = content
        self.calls = []

        class _Completions:
            def __init__(self, outer):
                self._outer = outer

            def create(self, **kwargs):
                self._outer.calls.append(kwargs)
                return _FakeResponse(self._outer.content)

        class _Chat:
            def __init__(self, outer):
                self.completions = _Completions(outer)

        self.chat = _Chat(self)


# ── enrichment functions (generator.py is the single source of truth) ────────

def test_enrich_concept_populates_fields():
    from okf.enrich.llm import enrich_concept

    client = _FakeClient('{"description": "Does a thing.", "docstring": "Docs here.", "tags": ["fast"], "design_pattern": "strategy"}')
    c = _make_concept()
    out = enrich_concept(c, client, "test-model")
    assert out.description == "Does a thing."
    assert out.docstring == "Docs here."
    assert "fast" in out.tags
    assert out.design_pattern == "strategy"
    assert len(client.calls) == 1


def test_enrich_concept_skips_when_complete():
    from okf.enrich.llm import enrich_concept

    client = _FakeClient('{"description": "x"}')
    long_desc = "This is a description that is well over one hundred and twenty characters long so that the enrichment logic correctly determines it does not need an LLM call to improve it at all."
    long_doc = "This docstring is also quite long and detailed, easily surpassing the eighty character threshold that the enrichment logic uses to decide whether a concept needs an LLM call to flesh it out further."
    c = _make_concept(description=long_desc, docstring=long_doc)
    out = enrich_concept(c, client, "test-model")
    assert out is c
    assert client.calls == []  # no LLM call


def test_enrich_concept_json_fallback():
    """Non-JSON response is treated as a description fallback (no crash)."""
    from okf.enrich.llm import enrich_concept

    client = _FakeClient("This is not JSON at all, just prose.")
    c = _make_concept()
    out = enrich_concept(c, client, "test-model")
    assert out.description  # fallback description from prose
    assert len(client.calls) == 1


def test_enrich_concept_non_function_type_uses_docstring():
    from okf.enrich.llm import enrich_concept

    client = _FakeClient("{}")
    c = _make_concept(type="Module", docstring="Module does the module thing.")
    out = enrich_concept(c, client, "test-model")
    assert out.description.startswith("Module does")
    assert client.calls == []  # no LLM call for non-enrichable types


def test_enrich_concept_deep_populates_fields(tmp_path):
    from okf.enrich.llm import enrich_concept_deep

    # concept.resource is "src/mod.py" — the source_dir must be its parent root
    src = tmp_path / "root"
    (src / "src").mkdir(parents=True)
    (src / "src" / "mod.py").write_text("def do_thing(x, y):\n    return x\n" * 10)

    client = _FakeClient('{"usage_example": "do_thing(1, 2)", "side_effects": "none", "security": "low", "complexity": "low"}')
    c = _make_concept()
    out = enrich_concept_deep(c, client, "test-model", src)
    assert out.usage_example == "do_thing(1, 2)"
    assert out.side_effects == "none"
    assert out.security == "low"
    assert out.complexity == "low"


def test_enrich_concept_deep_skips_without_body(tmp_path):
    from okf.enrich.llm import enrich_concept_deep

    src = tmp_path / "missing_src"
    client = _FakeClient('{"usage_example": "x"}')
    c = _make_concept()
    enrich_concept_deep(c, client, "test-model", src)
    assert client.calls == []  # body couldn't be resolved → no call


def test_enrich_security_populates(tmp_path):
    from okf.enrich.llm import enrich_security

    src = tmp_path / "root"
    (src / "src").mkdir(parents=True)
    (src / "src" / "mod.py").write_text("def do_thing(x, y):\n    return x\n" * 10)

    client = _FakeClient('{"security": "uses eval on user input", "complexity": "high"}')
    c = _make_concept()
    out = enrich_security(c, client, "test-model", src)
    assert "eval" in out.security
    assert out.complexity == "high"


# ── delegation: enrich/llm.py must forward to generator.py (no drift) ───────

def test_llm_module_delegates_to_generator():
    """The standalone functions in enrich.llm must be the generator's versions."""
    import okf.enrich.llm as llm
    import okf.generator as gen

    assert llm.enrich_concept is not gen.enrich_concept  # wrappers, not aliases
    assert llm.enrich_concept.__module__ == "okf.enrich.llm"
    # The wrappers must call through: monkeypatch generator and verify delegation
    import okf.generator as generator_module

    def _fake_enrich(c, client, model, max_tokens=2000):
        c.description = "from generator"
        return c

    orig = generator_module.enrich_concept
    generator_module.enrich_concept = _fake_enrich
    try:
        c = _make_concept()
        out = llm.enrich_concept(c, object(), "m")
        assert out.description == "from generator"
    finally:
        generator_module.enrich_concept = orig


def test_llm_enricher_contract(tmp_path):
    """LlmEnricher implements the Enricher contract (start/run/stop)."""
    from okf.enrich.base import Enricher
    from okf.enrich.llm import LlmEnricher

    bundle = tmp_path / "bundle"
    bundle.mkdir()
    enricher = LlmEnricher(tmp_path, mode="base")
    assert isinstance(enricher, Enricher)
    # start() without an API key configured should return False gracefully
    # (no crash) since the client can't resolve.
    ok = enricher.start(bundle, [_make_concept()])
    # Either started (if a local LLM is configured) or skipped cleanly
    assert isinstance(ok, bool)
    enricher.stop()
