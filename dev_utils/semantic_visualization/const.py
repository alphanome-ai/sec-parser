import sec_parser as sp


HEADERS = {
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "company01, joe@company01.com",
    "Host": 'www.sec.gov',
}
PARENT_EXTRA_STYLE = {
    'position': 'relative',
    'width': '100%',
}
TRANSPARENT_EXTRA_STYLE = {
    'position': 'absolute',
    'top': 0,
    'left': 0,
    'width': '100%',
    'height': '100%',
    'z-index': 10,
}
COLOR_PAIR = [
    (sp.TopLevelSectionTitle, "rgba(247, 217, 196, 0.7)"),
    (sp.semantic_elements.SupplementaryText, "rgba(247, 0, 196, 0.7)"),
    (sp.TitleElement, "rgba(250, 237, 203, 0.7)"),
    (sp.TextElement, "rgba(201, 228, 222, 0.7)"),
    (sp.ImageElement, "rgba(198, 222, 241, 0.7)"),
    (sp.IrrelevantElement, "rgba(219, 205, 240, 0.7)"),
    (sp.TableElement, "rgba(242, 198, 222, 0.7)"),
]
COLORING_COVER_TEMPLATE = """
<div style="position: relative;width: 100%">
    {real_tag}
    <div style="position: absolute;top: 0;left: 0;width: 100%;height: 100%;z-index: 10;background-color: {bg_color}">
    </div>
</div>
"""

__all__ = [
    "PARENT_EXTRA_STYLE",
    "TRANSPARENT_EXTRA_STYLE",
    "COLOR_PAIR",
    "COLORING_COVER_TEMPLATE",
    "HEADERS",
]
