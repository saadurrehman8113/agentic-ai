import sys
import time
from workflow.coordinator import run_workflow
from workflow.reporter    import save_report, print_summary


def main():
    # Get topic from command line or use default
    topic = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "AI agent development tools and platforms in 2025"
    )

    start = time.time()

    print("\n" + "="*55)
    print("  Multi-Agent Business Intelligence System")
    print("  Project 3 -- Agentic AI Course")
    print("="*55)
    print(f"  Topic: {topic}")
    print("="*55)

    # Run the full workflow
    report = run_workflow(topic)

    # Save to disk
    filename = save_report(topic, report)
    elapsed  = time.time() - start

    print_summary(topic, filename, elapsed)

    # Also print the report to terminal
    print("\n" + "="*55)
    print("  REPORT PREVIEW")
    print("="*55)
    print(report[:1500])
    if len(report) > 1500:
        print(f"\n... ({len(report) - 1500} more characters in file)")


if __name__ == "__main__":
    main()