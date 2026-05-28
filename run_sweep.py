import subprocess
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def run_ruff():
    """Runs ruff and returns the output string."""
    try:
        # Run ruff check on the current directory
        result = subprocess.run(
            ["./venv/bin/ruff", "check", "."],
            capture_output=True,
            text=True,
        )
        return result.stdout + result.stderr
    except FileNotFoundError:
        return "Error: ruff not found. Ensure it is installed."
    except Exception as e:
        return f"Error running ruff: {str(e)}"

def analyze_with_ai(ruff_output):
    """Uses Gemini to analyze ruff output and suggest fixes."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "GEMINI_API_KEY not found in environment. Cannot perform AI analysis."

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
You are an expert Python debugger and Qiskit developer.
I just ran a static analysis sweep on our quantum computing educational app using `ruff`.

Here is the output from `ruff`:
```text
{ruff_output}
```

Please provide a concise summary of the most critical issues. 
Ignore style warnings (like line length) and focus on actual bugs, undefined variables, or syntax errors.
Suggest how to fix the top 3 most severe issues.
"""
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

if __name__ == "__main__":
    print("🧹 Starting automated bug sweep...")
    ruff_out = run_ruff()
    print("📊 Ruff output generated.")
    
    if "Found 0 errors" in ruff_out or not ruff_out.strip():
        print("✅ No issues found by Ruff! The codebase is clean.")
    else:
        print("🤖 Analyzing issues with A.C.E. ...")
        ai_analysis = analyze_with_ai(ruff_out)
        
        print("\n" + "="*50)
        print("🚀 AUTOMATED BUG SWEEP REPORT")
        print("="*50)
        print(ai_analysis)
        print("="*50)
