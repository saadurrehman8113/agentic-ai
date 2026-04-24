# agentic-ai
This repository will hold all the agentic ai projects.

Step 1 — Install Python
Windows:

Go to python.org/downloads and download the latest Python 3.12+ installer
Run it — and tick "Add Python to PATH" before clicking Install (this is the #1 mistake beginners make)
Open a new terminal (search "cmd" or "PowerShell") and verify:

python --version

Step 2 — Set up your project folder
Every project we build will live in its own folder with its own isolated environment (called a virtual environment — think of it like a clean sandbox so packages don't collide between projects).
bash# Create your main learning folder
mkdir agentic-ai-course
cd agentic-ai-course

# Create a virtual environment
python -m venv venv          # Windows
python3 -m venv venv         # Mac/Linux

# Activate it
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# You'll see (venv) appear in your terminal prompt — that means it's active

Step 3 — Install the Anthropic SDK
bashpip install anthropic
Verify it installed:
bashpython -c "import anthropic; print('Anthropic SDK ready')"

Step 4 — Get your API key

Go to console.anthropic.com
Sign up / log in
Click "API Keys" → "Create Key"
Copy the key (starts with sk-ant-...)

Now set it as an environment variable so your code can use it without hardcoding secrets:
bash# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"

# Mac/Linux
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
To make it permanent on Mac/Linux, add that export line to your ~/.zshrc or ~/.bashrc file.
Verify everything works — run this:
bashpython -c "
import anthropic
client = anthropic.Anthropic()
r = client.messages.create(
    model='claude-haiku-4-5-20251001',
    max_tokens=50,
    messages=[{'role':'user','content':'Say: setup works!'}]
)
print(r.content[0].text)
"
If you see setup works! printed — you're ready. If you hit any error, paste it here and I'll fix it with you.

Step 5 — Your code editor
If you don't already have one, install VS Code — it's free and the industry standard:
code.visualstudio.com
Then install the Python extension inside VS Code (search "Python" in the Extensions tab). This gives you syntax highlighting, autocomplete, and the ability to run files with one click.
