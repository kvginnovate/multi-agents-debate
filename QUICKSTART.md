# Quick Start: Gemini vs Qwen Debate

## Overview

This framework allows **Gemini** and **Qwen** AI models to debate any topic. You can use either:
1. **CLI Tools** (recommended - already installed on your system)
2. **Python SDK** (requires additional setup)

---

## Method 1: Using CLI Tools (Recommended ✅)

### Prerequisites

You already have the CLI tools installed:
- ✅ Gemini CLI: `C:\Users\chokk\AppData\Roaming\npm\gemini.cmd`
- ✅ Qwen CLI: `C:\Users\chokk\AppData\Roaming\npm\qwen.cmd`

### Quick Start

**Option A: Batch Script (Easiest)**
```batch
cd E:\Ai Agents\Debate\Multi-Agents-Debate
debate_gemini_qwen.bat "AI will replace programmers"
```

**Option B: Python Script with CLI**
```bash
cd E:\Ai Agents\Debate\Multi-Agents-Debate
python debate_cli.py "AI will replace programmers"
```

**Option C: Interactive Mode**
```bash
python debate_cli.py
# Then enter your topic when prompted
```

---

## Method 2: Using Python SDK (Alternative)

### Installation

```bash
pip install -r requirements.txt
```

### Set API Keys

**Get your API keys:**
- **Gemini**: https://makersuite.google.com/app/apikey
- **Qwen (DashScope)**: https://dashscope.console.aliyun.com/

**Set environment variables:**
```batch
set GEMINI_API_KEY=your_gemini_key_here
set DASHSCOPE_API_KEY=your_dashscope_key_here
```

### Run the Python SDK version

```bash
python gemini_vs_qwen.py "AI will replace programmers"
```

---

## Usage Examples

### Simple Debate (3 rounds, default)
```bash
debate_gemini_qwen.bat "Should universal basic income be implemented?"
```

### Custom Topic
```bash
python debate_cli.py "Is remote work better than office work?"
```

### Using the original interactive.py (supports all providers)
```bash
python interactive.py
# Select: gemini or qwen when prompted
# Enter topic and watch them debate!
```

---

## Files Created

| File | Description |
|------|-------------|
| `debate_gemini_qwen.bat` | **Windows batch script** - uses CLI tools directly |
| `debate_cli.py` | **Python script** - uses CLI tools via subprocess |
| `gemini_vs_qwen.py` | **Python SDK version** - requires API keys in code |
| `interactive.py` | **Original script** - now supports Gemini/Qwen with SDK |

---

## Approval Mode

Both CLI tools support different approval modes:

- `-y` or `--yolo`: Auto-approve all actions (used by default)
- `--approval-mode=plan`: Read-only mode
- `--approval-mode=auto-edit`: Auto-approve edits
- `--approval-mode=default`: Ask for each action

---

## Troubleshooting

### "gemini: command not found"
```bash
# Install Gemini CLI
npm install -g @google/gemini-cli
```

### "qwen: command not found"
```bash
# Install Qwen CLI  
npm install -g @anthropic/qwen-cli
```

### API Key Errors
Make sure your API keys are set:
```batch
set GEMINI_API_KEY=your_key
set DASHSCOPE_API_KEY=your_key
```

### Configuration Error
If you see `Invalid configuration in C:\Users\chokk\.gemini\settings.json`:
- Fix the MCP server configuration in that file
- Remove invalid keys like `disabled` or `autoApprove`

---

## Example Output

```
======================================================================
  GEMINI vs QWEN DEBATE
======================================================================

Topic: Should universal basic income be implemented?
Rounds: 3
----------------------------------------------------------------------

--- ROUND 1: Opening Statements ---

**Gemini (Affirmative):**

Universal Basic Income (UBI) provides economic security...

**Qwen (Negative):**

While UBI sounds appealing, it creates several problems...

--- ROUND 2: Rebuttals ---

**Gemini (rebutting Qwen):**

Qwen's concerns about cost are valid, but studies show...

...

======================================================================
  DEBATE COMPLETE!
======================================================================
```

---

## Advanced: Using Original MAD Framework

The original `interactive.py` now supports multiple providers:

```bash
python interactive.py
# Enter model provider: gemini
# Use preset model: y
# Enter debate topic: Your topic here
```

Supported providers:
- `openai` - GPT models
- `gemini` - Google Gemini
- `qwen` - Alibaba Qwen

---

## Enjoy the Debate! 🎭

Pick any topic and watch Gemini and Qwen discuss different perspectives!
