#!/usr/bin/env python3
"""Simple Ollama chat client. Uses curl, no dependencies."""
import json
import subprocess
import sys

model = sys.argv[1] if len(sys.argv) > 1 else "dolphin-mistral"
history = []

print(f"Chatting with {model}. Type 'exit' to quit.\n")
while True:
    try:
        user = input("You: ")
    except (KeyboardInterrupt, EOFError):
        print()
        break
    if user.lower() in ("exit", "quit"):
        break
    history.append({"role": "user", "content": user})
    payload = json.dumps({"model": model, "messages": history})
    out = subprocess.run(
        ["curl", "-s", "http://localhost:11434/api/chat", "-d", payload],
        capture_output=True, text=True,
    ).stdout
    reply = "".join(json.loads(line)["message"]["content"] for line in out.splitlines() if line)
    history.append({"role": "assistant", "content": reply})
    print(f"\n{model[:12]}: {reply}\n")


if __name__ == "__main__":
    pass