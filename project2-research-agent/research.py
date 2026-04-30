#This is the entry point — it connects all three agents in sequence and saves the final report.
import os
import sys
from datetime import datetime

from agents.searcher import search_topic
from agents.reader   import read_sources
from agents.writer   import write_report

def research(topic: str) -> str:
    """
    Full research pipeline:
    topic → search → read → write → save
    """
    print(f"\n{'='*55}")
    print(f"  Research Assistant")
    print(f"  Topic: {topic}")
    print(f"{'='*55}")

    # ── Stage 1: Search ──
    search_result = search_topic(topic)

    # ── Stage 2: Read and extract ──
    reader_output = read_sources(search_result)

    # ── Stage 3: Write report ──
    report = write_report(reader_output)

    # ── Save to file ──
    os.makedirs("reports", exist_ok=True)
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = topic.replace(" ", "_")[:40]
    filename   = f"reports/{safe_topic}_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n{'='*55}")
    print(f"  Report saved: {filename}")
    print(f"{'='*55}\n")
    print(report)

    return filename

if __name__ == "__main__":
    # Get topic from command line or use a default
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Agentic AI trends 2025"
    research(topic)