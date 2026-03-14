#!/usr/bin/env python3
"""
Simple Gemini vs Qwen Debate using CLI tools

Usage:
    python debate_cli.py [topic]
    
Or just run:
    python debate_cli.py
    
Requirements:
    - Gemini CLI: gemini
    - Qwen CLI: qwen
"""

import subprocess
import sys
import os


def run_cli_command(command: list) -> str:
    """Run a CLI command and return output"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {e}"


def debate(topic: str, rounds: int = 3):
    """Run a debate between Gemini and Qwen using CLI tools"""
    
    print("\n" + "=" * 70)
    print("  GEMINI vs QWEN DEBATE (CLI Mode)")
    print("=" * 70)
    print(f"\nTopic: {topic}")
    print(f"Rounds: {rounds}")
    print("-" * 70)
    
    # Check if CLI tools are available - try multiple paths
    gemini_paths = ["gemini", "gemini.cmd", 
                    os.path.expandvars(r"%APPDATA%\npm\gemini.cmd"),
                    r"C:\Users\chokk\AppData\Roaming\npm\gemini.cmd"]
    qwen_paths = ["qwen", "qwen.cmd",
                  os.path.expandvars(r"%APPDATA%\npm\qwen.cmd"),
                  r"C:\Users\chokk\AppData\Roaming\npm\qwen.cmd"]
    
    has_gemini = False
    has_qwen = False
    gemini_cmd = None
    qwen_cmd = None
    
    # Find gemini
    for path in gemini_paths:
        try:
            expanded = os.path.expandvars(path)
            result = subprocess.run([expanded, "--version"], capture_output=True, timeout=5)
            has_gemini = True
            gemini_cmd = expanded
            print(f"✅ Found Gemini CLI: {expanded}")
            break
        except:
            continue
    
    # Find qwen
    for path in qwen_paths:
        try:
            expanded = os.path.expandvars(path)
            result = subprocess.run([expanded, "--version"], capture_output=True, timeout=5)
            has_qwen = True
            qwen_cmd = expanded
            print(f"✅ Found Qwen CLI: {expanded}")
            break
        except:
            continue
    
    if not has_gemini:
        print("⚠️  Gemini CLI not found. Install with: npm install -g @google/gemini-cli")
    
    if not has_qwen:
        print("⚠️  Qwen CLI not found. Install with: npm install -g @anthropic/qwen-cli")
    
    if not has_gemini or not has_qwen:
        print("\n❌ Required CLI tools not found. Please install them first.")
        return
    
    # System prompts
    gemini_system = f'You are debating the topic: "{topic}". You are taking the AFFIRMATIVE side (supporting the topic). Present logical arguments with evidence and reasoning. Be concise but persuasive. Keep responses under 200 words.'
    
    qwen_system = f'You are debating the topic: "{topic}". You are taking the NEGATIVE side (opposing the topic). Present logical arguments with evidence and reasoning. Be concise but persuasive. Keep responses under 200 words.'
    
    # Opening statements
    print("\n--- ROUND 1: Opening Statements ---\n")
    
    print("**Gemini (Affirmative):**")
    gemini_arg = run_cli_command([
        gemini_cmd, "-y", "-p", 
        gemini_system + " Start your response directly with your argument."
    ])
    print(gemini_arg)
    print()
    
    print("**Qwen (Negative):**")
    qwen_arg = run_cli_command([
        qwen_cmd, "-y", "-p",
        qwen_system + " Start your response directly with your argument."
    ])
    print(qwen_arg)
    print()
    
    # Debate rounds
    for round_num in range(2, rounds + 1):
        print(f"--- ROUND {round_num}: Rebuttals ---\n")
        
        # Gemini rebuts Qwen
        print(f"**Gemini (rebutting Qwen):**")
        gemini_prompt = f'{gemini_system} Qwen\'s previous argument was: "{qwen_arg}". Rebut their points and strengthen your position. Keep under 200 words.'
        gemini_arg = run_cli_command([gemini_cmd, "-y", "-p", gemini_prompt])
        print(gemini_arg)
        print()
        
        # Qwen rebuts Gemini
        print(f"**Qwen (rebutting Gemini):**")
        qwen_prompt = f'{qwen_system} Gemini\'s previous argument was: "{gemini_arg}". Rebut their points and strengthen your position. Keep under 200 words.'
        qwen_arg = run_cli_command([qwen_cmd, "-y", "-p", qwen_prompt])
        print(qwen_arg)
        print()
    
    # Closing statements
    print("--- CLOSING STATEMENTS ---\n")
    
    print("**Gemini (Closing):**")
    gemini_closing = run_cli_command([
        gemini_cmd, "-y", "-p",
        f'{gemini_system} Provide a strong closing statement summarizing your key points. Keep under 150 words.'
    ])
    print(gemini_closing)
    print()
    
    print("**Qwen (Closing):**")
    qwen_closing = run_cli_command([
        qwen_cmd, "-y", "-p",
        f'{qwen_system} Provide a strong closing statement summarizing your key points. Keep under 150 words.'
    ])
    print(qwen_closing)
    print()
    
    print("=" * 70)
    print("  DEBATE COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    # Get topic from command line or prompt
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
        rounds = 3  # Default rounds for non-interactive mode
    else:
        topic = input("\nEnter debate topic: ").strip()
        while not topic:
            topic = input("Enter debate topic: ").strip()
        
        # Get number of rounds
        rounds_input = input("Number of rounds (default 3): ").strip()
        rounds = int(rounds_input) if rounds_input.isdigit() and int(rounds_input) > 0 else 3
    
    # Run the debate
    debate(topic, rounds)
