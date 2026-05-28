import os

files_to_update = [
    "CONTRIBUTING.md",
    "backend/routers/agents.py",
    "agents/router_agent.py",
    "agents/composer_agent.py",
    "agents/socratic_tutor.py",
    "agents/feynman_agent.py",
    "agents/qiskit_engineer.py",
    "frontend/agents/router_agent.py",
    "frontend/agents/composer_agent.py",
    "frontend/streamlit_app.py",
]

for filepath in files_to_update:
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            content = f.read()
        
        # Replace instances of Boss and Creator with Explorer
        content = content.replace("Boss / Creator", "Explorer")
        content = content.replace("Boss or Creator", "Explorer")
        content = content.replace("'Boss' or 'Creator'", "'Explorer'")
        content = content.replace("Boss,", "Explorer,")
        content = content.replace(" Boss ", " Explorer ")
        content = content.replace(" Boss!", " Explorer!")
        content = content.replace(" Boss.", " Explorer.")
        content = content.replace(" Boss?", " Explorer?")
        content = content.replace("Boss", "Explorer")
        
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"Skipping {filepath}, not found")
