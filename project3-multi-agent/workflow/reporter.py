import os
from datetime import datetime


def save_report(topic: str, report: str) -> str:
    """Save report to disk. Returns the file path."""
    os.makedirs("reports", exist_ok=True)

    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(
        c if c.isalnum() or c in " _-" else ""
        for c in topic
    ).strip().replace(" ", "_")[:40]

    filename = f"reports/{safe_topic}_{timestamp}.md"

    # Add metadata header
    header = (
        f"---\n"
        f"topic: {topic}\n"
        f"generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"system: Multi-Agent Workflow v1.0\n"
        f"---\n\n"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + report)

    return filename


def print_summary(topic: str, filename: str, elapsed: float):
    """Print a clean summary after workflow completes."""
    print("\n" + "="*55)
    print("  WORKFLOW COMPLETE")
    print("="*55)
    print(f"  Topic:     {topic}")
    print(f"  Report:    {filename}")
    print(f"  Time:      {elapsed:.1f} seconds")
    print("="*55)