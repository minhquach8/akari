"""Tests for registry integration with real sklearn models and resources."""

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

from akari.registry.registry import IdentityRegistry
from akari.registry.specs import ModelSpec, ResourceSpec, SpecKind


def test_register_sklearn_iris_model_spec() -> None:
    """IdentityRegistry should accept a real sklearn model wrapped in ModelSpec."""
    iris = load_iris()
    X, y = iris.data, iris.target

    model = RandomForestClassifier(
        n_estimators=20,
        random_state=0,
    )
    model.fit(X, y)

    spec = ModelSpec(
        id='model:iris_sklearn_test',
        name='Iris classifier (test)',
        runtime='sklearn',
        tags={'iris', 'sklearn', 'test'},
        binding=model,
    )

    registry = IdentityRegistry()
    registry.register(spec)

    fetched = registry.get('model:iris_sklearn_test')
    assert fetched is not None
    assert fetched.kind is SpecKind.MODEL
    assert fetched.runtime == 'sklearn'
    assert fetched.binding is model

    # Quick sanity check that the binding behaves like a trained model.
    sample = X[0:1]
    prediction = fetched.binding.predict(sample)
    assert prediction.shape == (1,)


def test_register_file_resource_and_disable() -> None:
    """IdentityRegistry should handle ResourceSpec and honour enabled-only logic."""
    registry = IdentityRegistry()

    resource = ResourceSpec(
        id='resource:iris_csv_test',
        name='Iris CSV resource (test)',
        runtime='file',
        metadata={
            'path': 'data/iris_test.csv',
            'format': 'csv',
        },
        tags={'iris', 'csv', 'resource', 'test'},
    )

    registry.register(resource)

    # Initially, the resource should appear in RESOURCE listings.
    resources = registry.list(kind=SpecKind.RESOURCE)
    assert any(res.id == 'resource:iris_csv_test' for res in resources)

    # Disable the resource.
    registry.disable('resource:iris_csv_test')
    assert resource.enabled is False

    # It should no longer appear in enabled-only listings.
    resources_after_disable = registry.list(kind=SpecKind.RESOURCE)
    assert all(res.id != 'resource:iris_csv_test' for res in resources_after_disable)

    # Default get() should hide it...
    assert registry.get('resource:iris_csv_test') is None
    # ...but include_disabled=True should still retrieve it.
    fetched = registry.get('resource:iris_csv_test', include_disabled=True)
    assert fetched is resource
