import pandas as pd
import pytest
from loguru import logger

from sec_parser.semantic_elements.table_element.table_parser import TableParser
from tests.unit.semantic_elements.table_element._data_for_table_parser import (
    TABLE_10Q_AAPL_0000320193_23_000077__001,
)


@pytest.mark.parametrize(
    ("name", "html_input", "expected_output"),
    tests := [
        (
            "simple table",
            TABLE_10Q_AAPL_0000320193_23_000077__001,
            pd.DataFrame(
                data={
                    "1": [
                        "Due after 1 year through 5 years",
                        "Due after 5 years through 10 years",
                        "Due after 10 years",
                        "Total fair value",
                    ],
                    "2": ["$", "11148", "16646", "$"],
                    "3": ["76267.0", "11148.0", "16646.0", "104061.0"],
                },
            ),
        ),
    ],
    ids=[t[0] for t in tests],
)
def test_parse_as_df(name, html_input, expected_output):
    # Arrange
    parser = TableParser(html_input)
    result_df = parser.parse_as_df()

    # Assert
    try:
        pd.testing.assert_frame_equal(result_df, expected_output)
    except AssertionError:
        logger.error(
            "Tables are different:\nResult DataFrame:\n{}\nExpected DataFrame:\n{}".format(
                result_df.to_json(),
                expected_output.to_json(),
            ),
        )
        raise


@pytest.mark.parametrize(
    ("name", "html_input", "expected_error"),
    error_tests := [
        (
            "invalid input",
            "<p>not a table</p>",
            ValueError("No tables found"),
        ),
    ],
    ids=[t[0] for t in error_tests],
)
def test_parse_as_df_error(name, html_input, expected_error):
    # Arrange
    parser = TableParser(html_input)

    # Act & Assert
    with pytest.raises(type(expected_error)) as result_error:
        parser.parse_as_df()
    assert str(expected_error) in str(result_error.value)
