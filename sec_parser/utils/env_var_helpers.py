from __future__ import annotations

import os


class ValueNotSetError(ValueError):
    pass


def get_value_or_env_var(
    value: str | None,
    env_var: str,
    default: str | None = None,
    exc: type[Exception] = ValueNotSetError,
) -> str:
    value = (value or "").strip()
    if value:
        return value

    env_value = os.environ.get(env_var, "").strip()
    if env_value:
        return env_value

    if default is not None:
        return default

    msg = f"No value provided and the environment variable '{env_var}' is also not set."
    raise exc(msg)
