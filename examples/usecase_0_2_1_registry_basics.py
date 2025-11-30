from __future__ import annotations

from akari import Kernel
from akari.registry.specs import ModelSpec, ResourceSpec, ToolSpec


def main() -> None:
    kernel = Kernel.from_config()
    registry = kernel.get_registry()

    print('=== AKARI v0.2.0 – Identity & Registry basics ===')
    print()

    # Register a ModelSpec
    iris_model = ModelSpec(
        name='Iris Classifier',
        runtime='callable',
        metadata={'dataset': 'iris'},
    )
    registry.register(iris_model)

    print('Registered model spec:')
    print(f'  id          = {iris_model.id}')
    print(f'  name        = {iris_model.name!r}')
    print(f'  display_name= {iris_model.display_name!r}')
    print()

    # Register a ToolSpec
    multiply_tool = ToolSpec(
        name='Multiply Numbers',
        runtime='callable',
        metadata={'description': 'Multiply two numbers together.'},
    )
    registry.register(multiply_tool)

    print('Registered tool spec:')
    print(f'  id          = {multiply_tool.id}')
    print(f'  name        = {multiply_tool.name!r}')
    print(f'  display_name= {multiply_tool.display_name!r}')
    print()

    # Register a ResourceSpec
    iris_resource = ResourceSpec(
        name='Iris CSV Path',
        runtime='file',
        metadata={'path': 'data/iris.csv'},
    )
    registry.register(iris_resource)

    print('Registered resource spec:')
    print(f'  id          = {iris_resource.id}')
    print(f'  name        = {iris_resource.name!r}')
    print(f'  display_name= {iris_resource.display_name!r}')
    print()

    # Lookup by id and name
    print('Lookup by id:')
    print(
        "  registry.get('model:iris_classifier') ->",
        registry.get('model:iris_classifier'),
    )
    print()

    print('Lookup by human-friendly name (normalised):')
    print("  registry.get('Iris Classifier') ->", registry.get('Iris Classifier'))
    print("  registry.get('iris classifier') ->", registry.get('iris classifier'))
    print(
        "  registry.get('  IRIS   Classifier  ') ->",
        registry.get('  IRIS   Classifier  '),
    )
    print()


if __name__ == '__main__':
    main()
