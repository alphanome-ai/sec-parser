from __future__ import annotations

from sec_parser.semantic_elements import IrrelevantElement
from sec_parser.semantic_elements.abstract_semantic_element import AbstractSemanticElement
from sec_parser.processing_engine.processing_log import LogItemOrigin, ProcessingLog


class PageElement(IrrelevantElement):
    """
    The PageElement class represents the page content of a paragraph or other content object.
    It relates to an irrelevant element, storing page numbers and context for the document.
    """

    PageNum = 0
    
    def is_page(source: AbstractSemanticElement):
        try:
            if source.text.__contains__('|'):
                pageNum = source.text.replace(" ","").split('|')[-1]
            else:
                pageNum = int(source.text.strip())
        except ValueError:
            return False
        
        if PageElement.PageNum == 0:
            PageElement.PageNum = int(pageNum)
            
        if int(pageNum) == PageElement.PageNum:
            PageElement.PageNum = PageElement.PageNum + 1
            return True
        
        return False
