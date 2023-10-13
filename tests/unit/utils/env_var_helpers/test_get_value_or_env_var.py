from unittest.mock import patch

import pytest

from sec_parser.utils.env_var_helpers import ValueNotSetError, get_value_or_env_var


def test_get_value_with_value_provided():
    # Arrange
    value = "test_value"
    env_var = "UNUSED_ENV_VAR"

    # Act
    result = get_value_or_env_var(value, env_var)

    # Assert
    assert result == value


@patch.dict("os.environ", {"TEST_ENV_VAR": "env_test_value"})
def test_get_value_with_env_var_set():
    # Arrange
    env_var = "TEST_ENV_VAR"

    # Act
    result = get_value_or_env_var(None, env_var)

    # Assert
    assert result == "env_test_value"


@patch.dict("os.environ", {}, clear=True)
def test_get_value_with_default_provided():
    # Arrange
    env_var = "TEST_ENV_VAR"
    default = "default_test_value"

    # Act
    result = get_value_or_env_var(None, env_var, default)

    # Assert
    assert result == default


@patch.dict("os.environ", {}, clear=True)
def test_get_value_raises_exception():
    # Arrange
    env_var = "TEST_ENV_VAR"

    # Act & Assert
    with pytest.raises(
        ValueNotSetError,
        match=f"No value provided and the environment variable '{env_var}' is also not set.",
    ):
        get_value_or_env_var(None, env_var)


def test_get_value_with_empty_string():
    # Arrange
    value = "   "
    env_var = "UNUSED_ENV_VAR"

    # Act & Assert
    with pytest.raises(
        ValueNotSetError,
        match=f"No value provided and the environment variable '{env_var}' is also not set.",
    ):
        get_value_or_env_var(value, env_var)
