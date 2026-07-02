"""Tests for okf/init.py — interactive wizard."""

from pathlib import Path


def test_detect_languages_python(tmp_path):
    from okf.init import detect_languages
    (tmp_path / "main.py").write_text("def f(): pass\n")
    (tmp_path / "utils.py").write_text("def g(): pass\n")
    (tmp_path / "requirements.txt").write_text("requests\n")
    langs, manifests, total = detect_languages(tmp_path)
    assert langs.get("Python") == 2
    assert manifests == 1
    assert total >= 3


def test_detect_languages_multi(tmp_path):
    from okf.init import detect_languages
    (tmp_path / "main.py").write_text("x = 1\n")
    (tmp_path / "app.js").write_text("const x = 1;\n")
    (tmp_path / "lib.ts").write_text("const x: number = 1;\n")
    (tmp_path / "main.go").write_text("package main\n")
    (tmp_path / "Hello.java").write_text("class Hello {}\n")
    (tmp_path / "lib.rs").write_text("fn main() {}\n")
    (tmp_path / "app.rb").write_text("puts 'hello'\n")
    (tmp_path / "math.c").write_text("int add(int a, int b) { return a + b; }\n")
    (tmp_path / "calc.cpp").write_text("class Calc {};\n")
    (tmp_path / "hello.cs").write_text("class Hello {}\n")
    (tmp_path / "schema.sql").write_text("CREATE TABLE t (id INT);\n")
    (tmp_path / "schema.sql").write_text("CREATE TABLE t (id INT);\n")
    langs, manifests, total = detect_languages(tmp_path)
    expected = {"Python", "JavaScript", "TypeScript", "Go", "Java", "Rust", "Ruby", "C", "C++", "C#", "SQL"}
    for lang in expected:
        assert lang in langs, f"Missing language: {lang}"
    assert total >= 10


def test_detect_languages_manifests(tmp_path):
    from okf.init import detect_languages
    for name in ("requirements.txt", "pyproject.toml", "package.json", "Cargo.toml", "go.mod"):
        (tmp_path / name).write_text("")
    langs, manifests, total = detect_languages(tmp_path)
    assert manifests >= 5


def test_summary_output(capsys):
    from okf.init import print_summary
    print_summary({"Python": 3, "Go": 2}, 4, 10)
    captured = capsys.readouterr()
    assert "Python" in captured.out
    assert "Go" in captured.out
    assert "Manifests" in captured.out
    assert "10" in captured.out
