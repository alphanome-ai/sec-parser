from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import streamlit as st
import toml


class Environment(Enum):
    UNKNOWN = "unknown"
    DEV = "dev"
    CI_CD = "ci_cd"
    PROD = "prod"

    @property
    def is_dev(self) -> bool:
        return self == Environment.DEV

    @property
    def is_prod(self) -> bool:
        return self == Environment.PROD

    @property
    def is_ci_cd(self) -> bool:
        return self == Environment.CI_CD

    @property
    def is_unknown(self) -> bool:
        return self == Environment.UNKNOWN


@dataclass
class Config:
    environment: Environment
    sec_parser_version: str
    root_dir: Path


@st.cache_data
def get_config() -> Config:
    root_dir = Path(__file__).parent.parent.parent
    return Config(
        environment=Environment(
            os.environ.get("ENVIRONMENT", "unknown").strip().lower(),
        ),
        sec_parser_version=toml.load(root_dir / "pyproject.toml")["tool"]["poetry"][
            "version"
        ],
        root_dir=root_dir,
    )
