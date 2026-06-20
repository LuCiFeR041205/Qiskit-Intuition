import subprocess

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

def analyze_locally(ruff_output):
    """Summarize ruff output without calling an external model."""
    lines = [line for line in ruff_output.splitlines() if line.strip()]
    severe_markers = ("F821", "F822", "F823", "E999", "SyntaxError", "ImportError")
    severe = [line for line in lines if any(marker in line for marker in severe_markers)]

    if severe:
        top_items = "\n".join(f"- {line}" for line in severe[:3])
        return f"Most important issues found:\n{top_items}\n\nStart with these because they can break runtime behavior."

    preview = "\n".join(f"- {line}" for line in lines[:3])
    return f"No obvious runtime-breaking ruff markers found. First reported items:\n{preview}"

if __name__ == "__main__":
    print("🧹 Starting automated bug sweep...")
    ruff_out = run_ruff()
    print("📊 Ruff output generated.")
    
    if "Found 0 errors" in ruff_out or not ruff_out.strip():
        print("✅ No issues found by Ruff! The codebase is clean.")
    else:
        print("🤖 Analyzing issues with local A.C.E. rules ...")
        ai_analysis = analyze_locally(ruff_out)
        
        print("\n" + "="*50)
        print("🚀 AUTOMATED BUG SWEEP REPORT")
        print("="*50)
        print(ai_analysis)
        print("="*50)
