"""Tests for okf/manifest_scanner.py — all 12 manifest parsers."""

import shutil
from pathlib import Path

import pytest


# ── Fixture helpers ─────────────────────────────────────────────────────────

def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content.strip())
    return p


# ── requirements.txt ────────────────────────────────────────────────────────

def test_parse_requirements_txt_basic(tmp_path):
    from okf.manifest_scanner import parse_requirements_txt
    f = _write(tmp_path, "requirements.txt", "requests==2.31.0\nflask>=2.3\nnumpy")
    deps = parse_requirements_txt(f)
    assert len(deps) == 3
    assert deps[0] == {"name": "requests", "ecosystem": "pip", "version": "==2.31.0", "dev": False}
    assert deps[2] == {"name": "numpy", "ecosystem": "pip", "version": "", "dev": False}


def test_parse_requirements_txt_skips_comments_and_flags(tmp_path):
    from okf.manifest_scanner import parse_requirements_txt
    f = _write(tmp_path, "requirements.txt", "# comment\n-r other.txt\n--index-url https://x\npytest>=7")
    deps = parse_requirements_txt(f)
    assert len(deps) == 1
    assert deps[0]["name"] == "pytest"


# ── pyproject.toml ──────────────────────────────────────────────────────────

def test_parse_pyproject_toml_pep621(tmp_path):
    from okf.manifest_scanner import parse_pyproject_toml
    f = _write(tmp_path, "pyproject.toml", """
[project]
dependencies = ["pyyaml>=6.0", "tqdm"]
optional-dependencies = {dev = ["pytest>=7"]}
""")
    deps = parse_pyproject_toml(f)
    names = {(d["name"], d["dev"]) for d in deps}
    assert ("pyyaml", False) in names
    assert ("tqdm", False) in names
    assert ("pytest", True) in names


def test_parse_pyproject_toml_poetry(tmp_path):
    from okf.manifest_scanner import parse_pyproject_toml
    f = _write(tmp_path, "pyproject.toml", """
[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31"
""")
    deps = parse_pyproject_toml(f)
    assert len(deps) == 1
    assert deps[0]["name"] == "requests"


# ── package.json ────────────────────────────────────────────────────────────

def test_parse_package_json(tmp_path):
    from okf.manifest_scanner import parse_package_json
    f = _write(tmp_path, "package.json", '{"dependencies":{"express":"^4.19"},"devDependencies":{"vitest":"^1.0"}}')
    deps = parse_package_json(f)
    assert len(deps) == 2
    assert {"name": "express", "ecosystem": "npm", "version": "^4.19", "dev": False} in deps
    assert {"name": "vitest", "ecosystem": "npm", "version": "^1.0", "dev": True} in deps


# ── Cargo.toml ──────────────────────────────────────────────────────────────

def test_parse_cargo_toml(tmp_path):
    from okf.manifest_scanner import parse_cargo_toml
    f = _write(tmp_path, "Cargo.toml", """
[package]
name = "test"
[dependencies]
serde = "1.0"
tokio = { version = "1.35", features = ["full"] }
[dev-dependencies]
criterion = "0.5"
""")
    deps = parse_cargo_toml(f)
    assert len(deps) == 3
    assert {"name": "serde", "ecosystem": "cargo", "version": "1.0", "dev": False} in deps
    assert {"name": "tokio", "ecosystem": "cargo", "version": "1.35", "dev": False} in deps
    assert {"name": "criterion", "ecosystem": "cargo", "version": "0.5", "dev": True} in deps


# ── go.mod ──────────────────────────────────────────────────────────────────

def test_parse_go_mod(tmp_path):
    from okf.manifest_scanner import parse_go_mod
    f = _write(tmp_path, "go.mod", """
module test
go 1.21
require (
    github.com/foo/bar v1.2.3
    github.com/baz/qux v0.5.0 // indirect
)
require golang.org/x/sync v0.6.0
""")
    deps = parse_go_mod(f)
    assert len(deps) == 3
    assert {"name": "github.com/foo/bar", "ecosystem": "go", "version": "v1.2.3", "dev": False} in deps
    assert {"name": "github.com/baz/qux", "ecosystem": "go", "version": "v0.5.0", "dev": True} in deps
    assert {"name": "golang.org/x/sync", "ecosystem": "go", "version": "v0.6.0", "dev": False} in deps


# ── composer.json ───────────────────────────────────────────────────────────

def test_parse_composer_json(tmp_path):
    from okf.manifest_scanner import parse_composer_json
    f = _write(tmp_path, "composer.json", '{"require":{"monolog/monolog":"^3.0"},"require-dev":{"phpunit/phpunit":"^10.0"}}')
    deps = parse_composer_json(f)
    assert len(deps) == 2
    assert {"name": "monolog/monolog", "ecosystem": "composer", "version": "^3.0", "dev": False} in deps
    assert {"name": "phpunit/phpunit", "ecosystem": "composer", "version": "^10.0", "dev": True} in deps


def test_parse_composer_json_skips_php_and_ext(tmp_path):
    from okf.manifest_scanner import parse_composer_json
    f = _write(tmp_path, "composer.json", '{"require":{"php":">=8.1","ext-json":"*","monolog/monolog":"^3.0"}}')
    deps = parse_composer_json(f)
    assert len(deps) == 1
    assert deps[0]["name"] == "monolog/monolog"


# ── pom.xml ─────────────────────────────────────────────────────────────────

def test_parse_pom_xml(tmp_path):
    from okf.manifest_scanner import parse_pom_xml
    f = _write(tmp_path, "pom.xml", """<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <dependencies>
    <dependency><groupId>junit</groupId><artifactId>junit</artifactId><version>5.9</version><scope>test</scope></dependency>
    <dependency><groupId>com.google.guava</groupId><artifactId>guava</artifactId><version>32.0</version></dependency>
  </dependencies>
</project>""")
    deps = parse_pom_xml(f)
    assert len(deps) == 2
    assert {"name": "junit:junit", "ecosystem": "maven", "version": "5.9", "dev": True} in deps
    assert {"name": "com.google.guava:guava", "ecosystem": "maven", "version": "32.0", "dev": False} in deps


# ── Gemfile ─────────────────────────────────────────────────────────────────

def test_parse_gemfile(tmp_path):
    from okf.manifest_scanner import parse_gemfile
    f = _write(tmp_path, "Gemfile", """
source "https://rubygems.org"
gem "rails", "7.1"
gem "pg"
group :test do
  gem "rspec", "3.12"
end
group :development do
  gem "pry"
end
""")
    deps = parse_gemfile(f)
    assert len(deps) == 4
    assert {"name": "rails", "ecosystem": "rubygems", "version": "7.1", "dev": False} in deps
    assert {"name": "pg", "ecosystem": "rubygems", "version": "", "dev": False} in deps
    assert {"name": "rspec", "ecosystem": "rubygems", "version": "3.12", "dev": True} in deps
    assert {"name": "pry", "ecosystem": "rubygems", "version": "", "dev": True} in deps


# ── build.gradle ────────────────────────────────────────────────────────────

def test_parse_build_gradle(tmp_path):
    from okf.manifest_scanner import parse_build_gradle
    f = _write(tmp_path, "build.gradle", """
dependencies {
    implementation "org.spring:spring-core:6.0.0"
    testImplementation "org.junit:junit:5.10.0"
    api "com.google:guava:32.0.0"
}
""")
    deps = parse_build_gradle(f)
    assert len(deps) == 3
    assert {"name": "org.spring:spring-core", "ecosystem": "gradle", "version": "6.0.0", "dev": False} in deps
    assert {"name": "org.junit:junit", "ecosystem": "gradle", "version": "5.10.0", "dev": True} in deps
    assert {"name": "com.google:guava", "ecosystem": "gradle", "version": "32.0.0", "dev": False} in deps


# ── Package.swift ────────────────────────────────────────────────────────────

def test_parse_package_swift(tmp_path):
    from okf.manifest_scanner import parse_package_swift
    f = _write(tmp_path, "Package.swift", """
// swift-tools-version:5.9
import PackageDescription
let package = Package(name: "MyLib", dependencies: [
    .package(url: "https://github.com/apple/swift-argument-parser", from: "1.2.0"),
    .package(url: "https://github.com/vapor/vapor.git", exact: "4.76.0"),
])
""")
    deps = parse_package_swift(f)
    assert len(deps) == 2
    assert {"name": "swift-argument-parser", "ecosystem": "swiftpm", "version": "1.2.0", "dev": False} in deps
    assert {"name": "vapor", "ecosystem": "swiftpm", "version": "4.76.0", "dev": False} in deps


# ── project.clj ─────────────────────────────────────────────────────────────

def test_parse_project_clj(tmp_path):
    from okf.manifest_scanner import parse_project_clj
    f = _write(tmp_path, "project.clj", """
(defproject my-lib "0.1.0"
  :dependencies [[org.clojure/clojure "1.11.1"]]
  :profiles {:dev {:dependencies [[cider/cider-nrepl "0.28.5"]]}})
""")
    deps = parse_project_clj(f)
    assert len(deps) == 2
    assert {"name": "org.clojure/clojure", "ecosystem": "clojars", "version": "1.11.1", "dev": False} in deps
    assert {"name": "cider/cider-nrepl", "ecosystem": "clojars", "version": "0.28.5", "dev": True} in deps


# ── mix.exs ─────────────────────────────────────────────────────────────────

def test_parse_mix_exs(tmp_path):
    from okf.manifest_scanner import parse_mix_exs
    f = _write(tmp_path, "mix.exs", """
defmodule MyApp.MixProject do
  use Mix.Project
  defp deps do
    [
      {:phoenix, "1.7.0"},
      {:jason, "1.4", only: :dev},
    ]
  end
end
""")
    deps = parse_mix_exs(f)
    assert len(deps) == 2
    assert {"name": "phoenix", "ecosystem": "hex", "version": "1.7.0", "dev": False} in deps
    assert {"name": "jason", "ecosystem": "hex", "version": "1.4", "dev": True} in deps


# ── End-to-end: scan_codebase discovers manifest deps ───────────────────────

def test_scan_codebase_discovers_manifest_deps(tmp_path):
    from okf.generator import scan_codebase
    src = tmp_path / "project"
    src.mkdir()
    _write(src, "requirements.txt", "requests==2.31.0\nflask>=2.3")
    _write(src, "main.py", "def f(): pass")
    concepts = scan_codebase(src)
    deps = [c for c in concepts if c.type == "Dependency"]
    assert len(deps) == 2
    names = {c.title for c in deps}
    assert "requests" in names
    assert "flask" in names


def test_manifest_deps_have_ecosystem_tag(tmp_path):
    from okf.generator import scan_codebase
    src = tmp_path / "project"
    src.mkdir()
    _write(src, "requirements.txt", "requests==2.31.0")
    _write(src, "main.py", "def f(): pass")
    concepts = scan_codebase(src)
    dep = next(c for c in concepts if c.type == "Dependency")
    tags = set(dep.tags)
    assert "ecosystem:pip" in tags
    assert "manifest:requirements.txt" in tags
    assert "type:Dependency" in tags
    assert dep.body_extra.get("ecosystem") == "pip"
    assert dep.body_extra.get("version_constraint") == "==2.31.0"
    assert dep.body_extra.get("dev_dependency") is False


# ── Lock file parsers ──────────────────────────────────────────────────────

def test_parse_cargo_lock(tmp_path):
    from okf.manifest_scanner import parse_cargo_lock
    f = tmp_path / "Cargo.lock"
    f.write_text('[[package]]\nname = "serde"\nversion = "1.0.197"\n\n[[package]]\nname = "tokio"\nversion = "1.38.0"\n')
    deps = parse_cargo_lock(f)
    assert len(deps) == 2
    assert {"name": "serde", "ecosystem": "cargo", "version": "1.0.197", "dev": False} in deps
    assert {"name": "tokio", "ecosystem": "cargo", "version": "1.38.0", "dev": False} in deps


def test_parse_poetry_lock(tmp_path):
    from okf.manifest_scanner import parse_poetry_lock
    f = tmp_path / "poetry.lock"
    f.write_text('[[package]]\nname = "requests"\nversion = "2.31.0"\ncategory = "main"\n\n[[package]]\nname = "pytest"\nversion = "7.4.0"\ncategory = "dev"\n')
    deps = parse_poetry_lock(f)
    assert len(deps) == 2
    assert {"name": "requests", "ecosystem": "pip", "version": "2.31.0", "dev": False} in deps
    assert {"name": "pytest", "ecosystem": "pip", "version": "7.4.0", "dev": True} in deps


def test_parse_go_sum(tmp_path):
    from okf.manifest_scanner import parse_go_sum
    f = tmp_path / "go.sum"
    f.write_text('github.com/foo/bar v1.0.0 h1:abc=\ngithub.com/baz/qux v2.0.0 h1:def=\n')
    deps = parse_go_sum(f)
    assert len(deps) == 2
    assert {"name": "github.com/foo/bar", "ecosystem": "go", "version": "v1.0.0", "dev": False} in deps


def test_parse_go_sum_skips_go_mod(tmp_path):
    from okf.manifest_scanner import parse_go_sum
    f = tmp_path / "go.sum"
    f.write_text('github.com/foo/bar v1.0.0 h1:abc=\ngithub.com/foo/bar v1.0.0/go.mod h1:abc=\n')
    deps = parse_go_sum(f)
    assert len(deps) == 1  # /go.mod line skipped


def test_parse_yarn_lock(tmp_path):
    from okf.manifest_scanner import parse_yarn_lock
    f = tmp_path / "yarn.lock"
    f.write_text('express@^4.19.0:\n  version "4.19.2"\n\nlodash@^4.17.21:\n  version "4.17.21"\n')
    deps = parse_yarn_lock(f)
    assert len(deps) == 2
    assert {"name": "express", "ecosystem": "npm", "version": "4.19.2", "dev": False} in deps


def test_parse_pnpm_lock(tmp_path):
    from okf.manifest_scanner import parse_pnpm_lock
    f = tmp_path / "pnpm-lock.yaml"
    f.write_text('lockfileVersion: "6.0"\npackages:\n  /express@4.19.2:\n    dev: false\n  /lodash@4.17.21:\n    dev: true\n')
    deps = parse_pnpm_lock(f)
    assert len(deps) == 2
    assert {"name": "express", "ecosystem": "npm", "version": "4.19.2", "dev": False} in deps
    assert {"name": "lodash", "ecosystem": "npm", "version": "4.17.21", "dev": True} in deps


def test_manifest_deps_concept_id_is_ecosystem_colon_name(tmp_path):
    from okf.generator import scan_codebase
    src = tmp_path / "project"
    src.mkdir()
    _write(src, "requirements.txt", "requests==2.31.0")
    _write(src, "main.py", "def f(): pass")
    concepts = scan_codebase(src)
    dep = next(c for c in concepts if c.type == "Dependency")
    assert dep.concept_id == "_dependencies/pip/requests"
