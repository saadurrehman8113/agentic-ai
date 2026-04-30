#The writer takes all the extracted points and synthesises them into a clean, structured markdown report.
import anthropic
from datetime import datetime

client = anthropic.Anthropic()

def write_report(reader_output: dict) -> str:
    """
    Synthesise all key points into a structured markdown report.
    """
    topic   = reader_output["topic"]
    sources = reader_output["sources"]

    print(f"\n[Writer] Synthesising report on '{topic}'...")

    # Build a structured brief for the writer
    source_brief = ""
    for i, src in enumerate(sources, 1):
        points = "\n".join(f"  - {p}" for p in src["key_points"])
        source_brief += f"\nSource [{i}]: {src['title']}\n{points}\n"

    # Citation list for the report footer
    citations = "\n".join(
        f"[{i}] {src['title']} — {src['link']}"
        for i, src in enumerate(sources, 1)
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system=f"""You are an expert research writer.
Write a comprehensive, well-structured research report in markdown format.

The report must include:
1. A title (# heading)
2. An executive summary (2-3 sentences)
3. 3-4 main sections with ## headings covering different aspects
4. A "Key Takeaways" section with 4-5 bullet points
5. A "References" section listing the sources as numbered citations

Rules:
- Write in clear, professional prose
- Reference sources inline using [1], [2], [3] etc.
- Do not invent facts — only use what is in the source material
- Date the report: {datetime.now().strftime('%B %d, %Y')}""",
        messages=[{
            "role": "user",
            "content": f"""Write a research report on: {topic}

Source material:
{source_brief}

Citations to use in References section:
{citations}"""
        }]
    )

    report = response.content[0].text
    print("[Writer] Report complete.")
    return report