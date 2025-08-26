from __future__ import annotations
import typer, json
from .analysis.analyzer import Analyzer
from .report.generator import save_all

from pathlib import Path
from .utils.io import load_transcripts, load_brief_any

app = typer.Typer(add_completion=False)

@app.command()
def run(brief: str = typer.Option(..., help="Путь к brief.yaml"),
        transcripts: str = typer.Option(..., help="Папка с .txt/.md транскриптами"),
        company_name: str = typer.Option("Company", help="Название компании"),
        author: str = typer.Option("Author", help="Автор отчёта"),
        report_title: str = typer.Option("UX Research Report", help="Титул отчёта")):
    brief_dir_or_file = Path(brief)
    if brief_dir_or_file.is_dir():
        brief_paths = sorted([p for p in brief_dir_or_file.glob("**/*") if p.suffix.lower() in (".yaml",".yml",".txt",".docx")])
    else:
        brief_paths = [brief_dir_or_file]
    b = load_brief_any(brief_paths)
    ts = load_transcripts(transcripts)
    analyzer = Analyzer(b)
    payload = analyzer.run(ts)
    paths = save_all(payload, company_name, author, report_title)
    typer.echo(json.dumps({"report_paths": paths}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    app()
