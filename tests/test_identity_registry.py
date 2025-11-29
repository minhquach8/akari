"""Tests for the IdentityRegistry implementation."""

from akari.registry.registry import IdentityRegistry
from akari.registry.specs import ModelSpec, SpecKind, ToolSpec


def test_register_and_get_by_id() -> None:
    """Registry should register specs and retrieve them by id."""
    registry = IdentityRegistry()

    model = ModelSpec(
        id='model:iris',
        name='Iris classifier',
        runtime='sklearn',
    )
    registry.register(model)

    fetched = registry.get('model:iris')
    assert fetched is model
    assert fetched.kind is SpecKind.MODEL


def test_register_duplicate_id_raises() -> None:
    """Registering two specs with the same id should fail."""
    registry = IdentityRegistry()

    first = ToolSpec(
        id='tool:multiply',
        name='Multiply',
        runtime='callable',
    )
    second = ToolSpec(
        id='tool:multiply',
        name='Multiply again',
        runtime='callable',
    )

    registry.register(first)
    try:
        registry.register(second)
        assert False, 'Expected ValueError for duplicate id'
    except ValueError:
        pass


def test_get_by_name_and_disable() -> None:
    """Registry should allow lookup by name and disabling specs."""
    registry = IdentityRegistry()

    tool = ToolSpec(
        id="tool:sum",
        name="Summation tool",
        runtime="callable",
    )
    registry.register(tool)

    # Lookup by name.
    fetched = registry.get("Summation tool")
    assert fetched is tool

    # Disable and ensure it is hidden by default.
    assert registry.disable('tool:sum') is True
    assert tool.enabled is False
    assert registry.get('tool:sum') is None
    assert registry.get('tool:sum', include_disabled=True) is tool


def test_list_filters_by_kind_and_tags() -> None:
    """Registry.list should filter by kind and tags."""
    registry = IdentityRegistry()

    iris = ModelSpec(
        id='model:iris',
        name='Iris classifier',
        runtime='sklearn',
        tags=['demo', 'iris'],
    )
    digits = ModelSpec(
        id='model:digits',
        name='Digits classifier',
        runtime='sklearn',
        tags=['demo', 'digits'],
    )
    helper = ToolSpec(
        id='tool:helper',
        name='Helper tool',
        runtime='callable',
        tags={'demo'},
    )

    registry.register(iris)
    registry.register(digits)
    registry.register(helper)

    # Filter by kind.
    models = registry.list(kind=SpecKind.MODEL)
    assert set(s.id for s in models) == {'model:iris', 'model:digits'}

    # Filter by tags
    iris_only = registry.list(kind=SpecKind.MODEL, tags={'iris'})
    assert [s.id for s in iris_only] == ['model:iris']

    # Tools with tag "demo"
    tools_demo = registry.list(kind=SpecKind.TOOL, tags={'demo'})
    assert [s.id for s in tools_demo] == ['tool:helper']
