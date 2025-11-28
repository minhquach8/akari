"""
Use Case 0.2.3 – Registry with a file resource.

This example shows how to:

1. Create a ResourceSpec that represents a file on disk.
2. Register the resource in the Kernel's IdentityRegistry.
3. List RESOURCE specs from the registry and inspect their metadata.
4. Demonstrate how disabled resources are hidden by default.
"""

from __future__ import annotations

from akari import Kernel
from akari.registry.specs import ResourceSpec, SpecKind


def main() -> None:
    """Entry point for the file resource registry use case."""
    kernel = Kernel()
    registry = kernel.get_registry()
    assert registry is not None

    print('=== Use Case 0.2.3 – Registry with file resource ===\n')

    # 1. Define a ResourceSpec representing a local CSV file.
    # We do not need the file to actually exist for this use case; we only care about the metadata stored in the registry.
    iris_resource = ResourceSpec(
        id='resource:iris_csv',
        name='Iris CSV file',
        runtime='file',
        metadata={
            'path': 'data/iris.csv',
            'format': 'csv',
            'description': 'CSV export of the Iris dataset',
        },
        tags={'iris', 'csv', 'resource'},
    )

    # 2. Register the resource spec.
    registry.register(iris_resource)

    print('Registered resource spec:')
    print(f'  id      : {iris_resource.id}')
    print(f'  name    : {iris_resource.name}')
    print(f'  kind    : {iris_resource.kind.value}')
    print(f'  runtime : {iris_resource.runtime}')
    print(f'  tags    : {sorted(iris_resource.tags)}')
    print(f'  path    : {iris_resource.metadata.get("path")}')
    print()

    # 3. List all RESOURCE specs.
    resources = registry.list(kind=SpecKind.RESOURCE)
    print('Listing RESOURCE specs (enabled-only):')
    for res in resources:
        print(f'  - {res.id} -> path={res.metadata.get("path")}')
    print()
    
    # 4. Disable the resource and show that it is hidden by default.
    registry.disable("resource:iris_csv")
    
    print("After disabling 'resource:iris_csv':")
    resources_after_disable = registry.list(kind=SpecKind.RESOURCE)
    print("  Enabled-only listing:", [res.id for res in resources_after_disable])

    fetched_default = registry.get("resource:iris_csv")
    fetched_including_disabled = registry.get(
        "resource:iris_csv", include_disabled=True
    )
    print("  get(...):", fetched_default)
    print("  get(..., include_disabled=True):", fetched_including_disabled.id if fetched_including_disabled else None)


if __name__ == '__main__':
    main()
