from __future__ import annotations

import os


class ValueNotSetError(ValueError):
    pass


def get_value_or_env_var(
    value: str | None, env_var: str, default: str | None = None,
) -> str:
    value = (value or "").strip()
    if value:
        return value

    env_value = os.environ.get(env_var, "").strip()
    if env_value:
        return env_value

    if default is not None:
        return default

    msg = f"Value for {env_var} not set."
    raise ValueNotSetError(msg)
