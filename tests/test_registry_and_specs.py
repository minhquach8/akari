from akari.registry.registry import IdentityRegistry
from akari.registry.specs import AgentSpec, ModelSpec, ToolSpec


def test_model_spec_normalises_name_and_generates_id() -> None:
    spec = ModelSpec(
        name='Iris Classifier',
        runtime='callable',
    )

    assert spec.display_name == 'Iris Classifier'

    assert spec.name == 'iris_classifier'

    assert spec.id == 'model:iris_classifier'


def test_tool_and_agent_spec_share_same_naming_conventions() -> None:
    tool = ToolSpec(
        name=' Multiply Numbers ',
        runtime='callable',
    )
    agent = AgentSpec(
        name=' Planner Agent',
        runtime='python',
    )

    assert tool.display_name == ' Multiply Numbers '
    assert tool.name == 'multiply_numbers'
    assert tool.id == 'tool:multiply_numbers'

    assert agent.display_name == ' Planner Agent'
    assert agent.name == 'planner_agent'
    assert agent.id == 'agent:planner_agent'


def test_registry_get_by_id_and_human_name() -> None:
    registry = IdentityRegistry()

    spec = ModelSpec(
        name='Iris Classifier',
        runtime='callable',
    )
    registry.register(spec)

    by_id = registry.get('model:iris_classifier')
    assert by_id is spec

    by_name_1 = registry.get('Iris Classifier')
    by_name_2 = registry.get('iris classifier')
    by_name_3 = registry.get('  IRIS   Classifier  ')

    assert by_name_1 is spec
    assert by_name_2 is spec
    assert by_name_3 is spec


def test_registry_disable_and_list_filters_by_enabled() -> None:
    registry = IdentityRegistry()

    model = ModelSpec(
        name='Iris Classifier',
        runtime='callable',
    )
    tool = ToolSpec(
        name='Logging Tool',
        runtime='callable',
    )
    registry.register(model)
    registry.register(tool)

    models_before = registry.list(kind='model')
    assert model in models_before

    disabled = registry.disable('iris classifier')
    assert disabled is True
    assert model.enabled is False

    models_after = registry.list(kind='model')
    assert model not in models_after

    models_with_disabled = registry.list(kind='model', include_disabled=True)
    assert model in models_with_disabled
