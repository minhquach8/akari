"""
Use Case 0.2.1 – Registry with sklearn Iris model.

This file is reserved by the Implementation Plan.

In a later step we will:
- create a real sklearn Iris classifier,
- wrap it in a ModelSpec with runtime="sklearn",
- register it in the Kernel's IdentityRegistry,
- and print a short summary of the registered model spec.
"""

from __future__ import annotations

from typing import Any

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

from akari import Kernel
from akari.registry.specs import ModelSpec


def train_iris_classifier() -> RandomForestClassifier:
    """Train a small RandomForest classifier on the Iris dataset."""
    iris = load_iris()
    X, y = iris.data, iris.target

    model = RandomForestClassifier(
        n_estimators=50,
        random_state=42,
    )
    model.fit(X, y)
    return model


def main() -> None:
    """Entry point for the sklearn Iris registry use case."""
    kernel = Kernel()
    registry = kernel.get_registry()
    assert registry is not None

    print('=== Use case 0.2.1 - Registry with sklearn Iris model ===\n')

    # 1. Train the model.
    model = train_iris_classifier()

    # 2. Wrap it in a ModelSpec.
    iris_spec = ModelSpec(
        id='model:iris_sklearn',
        name='Iris classifier (sklearn RandomForest)',
        runtime='sklearn',
        metadata={
            'dataset': 'iris',
            'framework': 'sklearn',
            'model_type': 'RandomForestClassifier',
        },
        tags={'demo', 'iris', 'sklearn'},
        binding=model,
    )

    # 3. Register in the IdentityRegistry
    registry.register(iris_spec)

    print('Registered model spec:')
    print(f'  id      : {iris_spec.id}')
    print(f'  name    : {iris_spec.name}')
    print(f'  kind    : {iris_spec.kind.value}')
    print(f'  runtime : {iris_spec.runtime}')
    print(f'  tags    : {sorted(iris_spec.tags)}')
    print()

    # 4. Retrieve and do a quick prediction via the binding
    fetched = registry.get('model:iris_sklearn')
    if fetched is None:
        print('ERROR: could not fetch model from registry.')
        return

    model_binding: Any = fetched.binding
    sample = [[5.1, 3.5, 1.4, 0.2]]  # Iris Setosa
    prediction = model_binding.predict(sample)
    print('Sample prediction for', sample, '-> class index:', int(prediction[0]))


if __name__ == '__main__':
    main()
