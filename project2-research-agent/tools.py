import os
import json
import requests
import subprocess
import tempfile
from dotenv import load_dotenv

load_dotenv()

#Tool 1 — Web Search (using Serper API)

def web_search(query: str, max_results: int = 5) -> dict:
    """
    Search the web using Serper (Google Search API).
    Returns a list of results with title, link, and snippet.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return {"error": "SERPER_API_KEY not set in .env"}

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "num": max_results
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Clean up the response — only keep what the LLM needs
        results = []
        for item in data.get("organic", []):
            results.append({
                "title":   item.get("title", ""),
                "link":    item.get("link", ""),
                "snippet": item.get("snippet", "")
            })

        return {
            "query":        query,
            "result_count": len(results),
            "results":      results
        }

    except requests.exceptions.Timeout:
        return {"error": "Search timed out. Try again."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Search failed: {str(e)}"}

#temp
# if __name__ == "__main__":
#     result = web_search("latest developments in agentic AI 2025")
#     for r in result["results"]:
#         print(f"\n{r['title']}")
#         print(f"{r['link']}")
#         print(f"{r['snippet'][:100]}...")

#Tool 2 — Live Weather (using OpenWeatherMap)

def get_weather(city: str, unit: str = "celsius") -> dict:
    """
    Get current weather for a city using OpenWeatherMap API.
    Returns temperature, conditions, humidity, wind speed.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return {"error": "WEATHER_API_KEY not set in .env"}

    # Map our unit names to OpenWeatherMap's units param
    units_map = {"celsius": "metric", "fahrenheit": "imperial"}
    units = units_map.get(unit, "metric")
    unit_symbol = "°C" if unit == "celsius" else "°F"

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q":     city,
        "appid": api_key,
        "units": units
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 404:
            return {"error": f"City '{city}' not found"}
        if response.status_code == 401:
            return {"error": "Invalid API key — check WEATHER_API_KEY in .env"}

        response.raise_for_status()
        data = response.json()

        return {
            "city":        data["name"],
            "country":     data["sys"]["country"],
            "temperature": f"{round(data['main']['temp'])}{unit_symbol}",
            "feels_like":  f"{round(data['main']['feels_like'])}{unit_symbol}",
            "condition":   data["weather"][0]["description"].capitalize(),
            "humidity":    f"{data['main']['humidity']}%",
            "wind_speed":  f"{data['wind']['speed']} m/s",
        }

    except requests.exceptions.Timeout:
        return {"error": "Weather request timed out"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Weather fetch failed: {str(e)}"}


#Tool 3 — Python Code Executor

def run_python(code: str, timeout: int = 10) -> dict:
    """
    Execute Python code in a safe subprocess and return stdout.
    The agent uses this for calculations, data processing, and logic.
    """
    # Write code to a temp file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = result.stdout.strip()
        error  = result.stderr.strip()

        if result.returncode != 0:
            return {
                "success": False,
                "error":   error or "Code exited with non-zero status",
                "code":    code
            }

        return {
            "success": True,
            "output":  output if output else "(no output)",
            "code":    code
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error":   f"Code timed out after {timeout} seconds",
            "code":    code
        }
    finally:
        os.unlink(tmp_path)   # always clean up the temp file