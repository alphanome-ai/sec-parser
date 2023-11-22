from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import TYPE_CHECKING

import streamlit as st
from pyinstrument import Profiler

from dev_utils.core.config import get_config
from dev_utils.core.sec_edgar_reports_getter import (
    get_filing_metadatas,
    get_sec_edgar_reports_getter,
)

if TYPE_CHECKING:
    from sec_parser.processing_engine.core import AbstractSemanticElementParser
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )

import sec_parser as sp


@dataclass
class ProfiledResult:
    elements: list[AbstractSemanticElement]
    parse_time: float
    profile: Profiler | None


class ProfiledParser:
    def __init__(
        self,
        *,
        parser: AbstractSemanticElementParser | None = None,
        interval: float | None = None,
    ) -> None:
        parsing_options = sp.ParsingOptions(
            html_integrity_checks=get_config().environment.is_dev,
        )
        self._parser = parser or sp.Edgar10QParser(parsing_options=parsing_options)
        self._interval = interval

    @property
    def parser(self) -> AbstractSemanticElementParser:
        return self._parser

    def parse(
        self,
        html: str | bytes,
    ) -> ProfiledResult:
        profiler = None
        start_time = perf_counter()
        if self._interval is not None:
            with Profiler(interval=self._interval) as profiler:
                elements = self.parser.parse(html, unwrap_elements=False)
        else:
            elements = self.parser.parse(html, unwrap_elements=False)
        end_time = perf_counter()
        parse_time = end_time - start_time

        return ProfiledResult(
            elements=elements,
            profile=profiler,
            parse_time=parse_time,
        )


@dataclass
class ParsingOutput:
    html: bytes
    result: ProfiledResult
    parser: AbstractSemanticElementParser


@st.cache_resource()
def get_parsing_output(url):
    html = get_sec_edgar_reports_getter().download_filing(url)
    profiled_parser = ProfiledParser()
    result = profiled_parser.parse(html)
    return ParsingOutput(html, result=result, parser=profiled_parser.parser)
