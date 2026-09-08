from html import escape
from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement

import numpy as np
import pandas as pd


def export_table(table: pd.DataFrame, path: str | Path) -> Path:
    """CSV or optional Excel export; neutralize spreadsheet formula injection in text cells."""
    path = Path(path)
    safe = table.copy()

    def sanitize(value):
        if isinstance(value, pd.Timestamp) and value.tzinfo is not None:
            return value.isoformat()
        return (
            "'" + value
            if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r"))
            else value
        )

    safe = safe.map(sanitize)
    safe.columns = [sanitize(c) for c in safe.columns]
    safe.index = safe.index.map(sanitize)
    if path.suffix.lower() == ".csv":
        safe.to_csv(path)
    elif path.suffix.lower() == ".xlsx":
        safe.to_excel(path, engine="openpyxl")
    else:
        raise ValueError("export path must end in .csv or .xlsx")
    return path


def network_gexf(correlation: pd.DataFrame, path: str | Path, threshold: float = 0.2) -> Path:
    """Undirected dependence graph with signed weights, readable by Gephi."""
    if (
        not correlation.index.equals(pd.Index(correlation.columns))
        or not np.isfinite(correlation).all().all()
    ):
        raise ValueError("finite square labeled matrix required")
    if not 0 <= threshold <= 1 or not np.allclose(correlation, correlation.T):
        raise ValueError("symmetric matrix and threshold in [0,1] required")
    root = Element("gexf", xmlns="http://www.gexf.net/1.2draft", version="1.2")
    graph = SubElement(root, "graph", mode="static", defaultedgetype="undirected")
    nodes, edges = SubElement(graph, "nodes"), SubElement(graph, "edges")
    for i, ticker in enumerate(correlation):
        SubElement(nodes, "node", id=str(i), label=str(ticker))
    count = 0
    for i in range(len(correlation)):
        for j in range(i + 1, len(correlation)):
            weight = correlation.iloc[i, j]
            if abs(weight) >= threshold:
                SubElement(
                    edges, "edge", id=str(count), source=str(i), target=str(j), weight=str(weight)
                )
                count += 1
    path = Path(path)
    ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path


def research_report(
    tables: dict[str, pd.DataFrame], path: str | Path, *, title: str = "Market research"
) -> Path:
    """Standalone HTML tables, with source/timestamp metadata when available."""
    parts = [
        '<!doctype html><meta charset="utf-8">',
        f"<title>{escape(title)}</title>",
        "<style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:20px}table{border-collapse:collapse}td,th{padding:8px;border-bottom:1px solid #ddd;text-align:right}h2{margin-top:40px}</style>",
        f"<h1>{escape(title)}</h1>",
    ]
    for name, table in tables.items():
        parts.extend([f"<h2>{escape(name)}</h2>", table.to_html(escape=True)])
        metadata = {
            key: table.attrs[key]
            for key in ("source", "retrieved_at", "complete", "total_matches")
            if key in table.attrs
        }
        if metadata:
            parts.append(f"<p>{escape(str(metadata))}</p>")
    path = Path(path)
    path.write_text("\n".join(parts), encoding="utf-8")
    return path
