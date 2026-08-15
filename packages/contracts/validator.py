"""Stdlib JSON Schema subset for draft 2020-12 as used by the five AEGIS contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]


class SchemaError(ValueError):
    """A value failed schema validation."""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_dir() -> Path:
    return _REPO_ROOT / "packages" / "contracts"


def load_schema(name: str) -> dict[str, Any]:
    if name in {"advisory_nonexecuting", "advisory_nonexecuting.schema.json"}:
        path = schema_dir() / "internal" / "advisory_nonexecuting.schema.json"
    else:
        filename = name if name.endswith(".schema.json") else f"{name}"
        path = schema_dir() / "regulated" / filename
    if not path.is_file():
        raise SchemaError(f"unknown contract {name!r}")
    return load_json(path)


def _resolve_ref(ref: str, root: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    if ref.startswith("#"):
        pointer = ref[1:]
        node: Any = root
        for part in pointer.split("/"):
            if not part:
                continue
            node = node[part]
        return node
    filename = Path(ref).name
    for folder in (base_dir, schema_dir() / "regulated", schema_dir() / "internal"):
        candidate = folder / filename
        if candidate.is_file():
            return load_json(candidate)
    raise SchemaError(f"unresolved $ref {ref!r}")


def validate(instance: Any, schema: dict[str, Any], *, base_dir: Path | None = None) -> None:
    errors = list(iter_errors(instance, schema, base_dir=base_dir))
    if errors:
        raise SchemaError("; ".join(errors))


def iter_errors(
    instance: Any,
    schema: dict[str, Any],
    *,
    path: str = "$",
    root: dict[str, Any] | None = None,
    base_dir: Path | None = None,
) -> list[str]:
    root = root if root is not None else schema
    base_dir = base_dir if base_dir is not None else schema_dir() / "regulated"
    errors: list[str] = []

    if "$ref" in schema:
        resolved = _resolve_ref(schema["$ref"], root, base_dir)
        return iter_errors(instance, resolved, path=path, root=root, base_dir=base_dir)

    expected_type = schema.get("type")
    if expected_type is not None:
        allowed = expected_type if isinstance(expected_type, list) else [expected_type]
        if instance is None:
            if "null" not in allowed:
                errors.append(f"{path}: expected {expected_type}, got null")
                return errors
        elif not _type_matches(instance, allowed):
            errors.append(f"{path}: expected {expected_type}, got {type(instance).__name__}")
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} is not in enum {schema['enum']}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < int(schema["minLength"]):
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: does not match pattern {schema['pattern']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < int(schema["minItems"]):
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(
                    iter_errors(item, item_schema, path=f"{path}[{index}]", root=root, base_dir=base_dir)
                )

    if isinstance(instance, dict):
        required = schema.get("required") or []
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties") or {}
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in properties:
                errors.extend(
                    iter_errors(
                        value,
                        properties[key],
                        path=f"{path}.{key}",
                        root=root,
                        base_dir=base_dir,
                    )
                )
            elif additional is False:
                errors.append(f"{path}: undeclared property {key!r}")
            elif isinstance(additional, dict):
                errors.extend(
                    iter_errors(
                        value,
                        additional,
                        path=f"{path}.{key}",
                        root=root,
                        base_dir=base_dir,
                    )
                )
    return errors


def _type_matches(instance: Any, allowed: list[str]) -> bool:
    mapping = {
        "object": dict,
        "array": list,
        "string": str,
        "boolean": bool,
        "integer": int,
        "number": (int, float),
        "null": type(None),
    }
    for name in allowed:
        expected = mapping.get(name)
        if expected is None:
            continue
        if name == "integer" and isinstance(instance, bool):
            continue
        if name == "number" and isinstance(instance, bool):
            continue
        if isinstance(instance, expected):
            return True
    return False
