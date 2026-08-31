"""Prompt template registry tests (Phase 2)."""

from __future__ import annotations

import pytest

from app.llm.templates import (
    EXTRACTION_TEMPLATE_ID,
    PromptTemplate,
    TemplateNotFoundError,
    TemplateRenderError,
    TemplateRegistry,
    default_registry,
)


def test_default_registry_contains_extraction_template() -> None:
    template = default_registry().get(EXTRACTION_TEMPLATE_ID)
    assert template.template_id == EXTRACTION_TEMPLATE_ID
    assert template.placeholders == ("user_text", "feedback")


def test_registry_unknown_id_raises() -> None:
    with pytest.raises(TemplateNotFoundError):
        TemplateRegistry().get("missing.v1")


def test_registry_rejects_duplicate_ids() -> None:
    registry = TemplateRegistry()
    template = PromptTemplate(
        template_id="t.v1", system="s", user_template="u", placeholders=()
    )
    registry.register(template)
    with pytest.raises(ValueError, match="duplicate"):
        registry.register(template)


def test_render_requires_all_placeholders() -> None:
    template = PromptTemplate(
        template_id="t.v1", system="s", user_template="a {x} b {y}", placeholders=("x", "y")
    )
    with pytest.raises(TemplateRenderError):
        template.render(x="1")


def test_render_produces_system_and_user_messages() -> None:
    template = default_registry().get(EXTRACTION_TEMPLATE_ID)
    messages = template.render(user_text="I have a cough", feedback="")
    assert messages[0].role == "system"
    assert messages[1].role == "user"
    assert "I have a cough" in messages[1].content
    # The live StructuredCase schema is embedded, keeping prompt and model in sync.
    assert "chief_complaint" in messages[1].content
    assert "red_flag_signals" in messages[1].content


def test_render_is_single_pass_so_values_cannot_inject_markers() -> None:
    template = PromptTemplate(
        template_id="t.v1",
        system="s",
        user_template="first={a} second={b}",
        placeholders=("a", "b"),
    )
    messages = template.render(a="{b}", b="real")
    assert messages[1].content == "first={b} second=real"


def test_extraction_template_treats_user_text_as_data() -> None:
    """Prompt-injection posture: the template marks user text as data and
    forbids the model from following instructions inside it."""
    template = default_registry().get(EXTRACTION_TEMPLATE_ID)
    assert "not" in template.system and "instructions" in template.system
    assert "Never invent information" in template.system
