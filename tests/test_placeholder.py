from pathlib import Path


def test_pr_template_contains_required_sections() -> None:
    content = Path(".github/pull_request_template.md").read_text(encoding="utf-8")
    assert "## 4.1 目标" in content
    assert "## 4.2 验收（DoD 勾选）" in content
    assert "## 4.3 证据（必须贴）" in content


def test_contributing_enforces_feat_branch_flow() -> None:
    content = Path("CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "feat/* -> main" in content
    assert "禁止直接 push 到 `main`" in content
