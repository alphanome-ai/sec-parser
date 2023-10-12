import json
from pathlib import Path

from sec_parser import Edgar10QParser


def write_snapshot(data_dir: str) -> None:
    dir_path = Path(data_dir)
    for document_type_dir in dir_path.iterdir():
        if document_type_dir.name.startswith("."):
            continue
        if not document_type_dir.is_dir():
            continue
        for company_dir in document_type_dir.iterdir():
            if not company_dir.is_dir():
                continue
            for report_dir in company_dir.iterdir():
                html_file = report_dir / "primary-document.html"
                json_file = report_dir / "semantic-elements-list.json"
                if not html_file.exists():
                    msg = f"HTML file not found: {html_file}"
                    raise FileNotFoundError(msg)

                with html_file.open("r") as f:
                    html_content = f.read()

                elements = Edgar10QParser().parse(html_content)

                with json_file.open("w") as f:
                    items = [{"id": i, **e.to_dict()} for i, e in enumerate(elements)]
                    json.dump(items, f, indent=4)
