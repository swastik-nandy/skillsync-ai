import os
from core.pipeline import process_resume_file
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# ---------------------------------------------------------------
# 🌍 Load Environment
# ---------------------------------------------------------------
load_dotenv(dotenv_path="./core/.env")
console = Console()


# ---------------------------------------------------------------
# 💼 Job Description Sample
# ---------------------------------------------------------------
JD_TEXT = """
We are hiring an AI Engineer with strong skills in Python, Machine Learning,
FastAPI, and Retrieval-Augmented Generation (RAG) systems. Experience with
LangChain, cloud platforms (AWS or Azure), and vector databases is a plus.
"""


# ---------------------------------------------------------------
# 🧾 Resume Path
# ---------------------------------------------------------------
RESUME_PATH = "./samples/resume.pdf"


# ---------------------------------------------------------------
# 🚀 Run Pipeline
# ---------------------------------------------------------------
def run_test():
    if not os.path.exists(RESUME_PATH):
        console.print(f"[red]❌ Resume file not found at {RESUME_PATH}[/red]")
        return

    console.print("[bold cyan]⚙️  Starting Gemini + FAISS Resume Analysis...[/bold cyan]")

    with open(RESUME_PATH, "rb") as f:
        file_bytes = f.read()

    result = process_resume_file(file_bytes, "resume.pdf", JD_TEXT)

    console.print("[green]✅ Analysis completed successfully![/green]\n")

    # Extract details
    analysis = result.get("analysis", {})
    feedback = result.get("feedback", {})

    # ---------------------------------------------------------------
    # 🎨 Display Results Nicely
    # ---------------------------------------------------------------
    console.print(Panel.fit(
        f"[bold magenta]🧠  AI Resume Match Summary[/bold magenta]",
        border_style="magenta",
    ))

    # Main metrics table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="bold yellow")
    table.add_column("Result", style="bold white")

    table.add_row("Match Percentage", f"{feedback.get('match_percentage', 'N/A')}%")
    table.add_row("Top Strengths", feedback.get("strengths", "—").strip() or "—")
    table.add_row("Weaknesses", feedback.get("weaknesses", "—").strip() or "—")
    table.add_row("Suggestions", feedback.get("suggestions", "—").strip() or "—")

    console.print(table)
    console.print("\n")

    # Optional: show raw Gemini response for debugging
    if os.getenv("DEBUG_RAW_OUTPUT", "false").lower() == "true":
        console.print(Panel(
            analysis.get("raw_output", "[No raw output]"),
            title="[grey]Gemini Raw Output[/grey]",
            border_style="dim",
        ))


# ---------------------------------------------------------------
# 🏁 Entry Point
# ---------------------------------------------------------------
if __name__ == "__main__":
    run_test()
