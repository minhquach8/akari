"""Tests for registry Spec models."""

from akari.registry.specs import (
    AgentSpec,
    BaseSpec,
    ModelSpec,
    ResourceSpec,
    SpecKind,
    ToolSpec,
    WorkspaceSpec,
)


def test_model_spec_defaults_and_kind() -> None:
    """ModelSpec should set kind=MODEL and sensible defaults."""
    spec = ModelSpec(
        id="model:iris",
        name="Iris classifier",
        runtime="sklearn",
    )

    assert isinstance(spec, BaseSpec)
    assert spec.kind is SpecKind.MODEL
    assert spec.id == "model:iris"
    assert spec.name == "Iris classifier"
    assert spec.runtime == "sklearn"

    # Default fields
    assert spec.enabled is True
    assert spec.metadata == {}
    assert spec.config == {}
    assert spec.tags == set()
    assert spec.binding is None
    assert spec.version is None
    
    
def test_tool_spec_has_correct_kind_and_tags() -> None:
    """ToolSpec should set kind=TOOL and support tags."""
    spec = ToolSpec(
        id="tool:multiply",
        name="Multiply numbers",
        runtime="callable",
        tags={"math", "demo"},
    )

    assert spec.kind is SpecKind.TOOL
    # Tags should be preserved as a set
    assert spec.tags == {"math", "demo"}

    # add_tag helper should work
    spec.add_tag("utility")
    assert "utility" in spec.tags


def test_disable_and_enable_spec() -> None:
    """BaseSpec should correctly toggle the enabled flag."""
    spec = ResourceSpec(
        id="resource:datafile",
        name="Local CSV file",
        runtime="file",
    )

    assert spec.enabled is True
    spec.disable()
    assert spec.enabled is False
    spec.enable()
    assert spec.enabled is True


def test_workspace_spec_kind_is_workspace() -> None:
    """WorkspaceSpec should always have kind=WORKSPACE."""
    ws = WorkspaceSpec(
        id="workspace:default",
        name="Default workspace",
        runtime="logical",
    )
    assert ws.kind is SpecKind.WORKSPACE