"""
Simple Gemini vs Qwen Debate Script

Usage:
    python gemini_vs_qwen.py
    
Or set API keys via environment variables:
    set GEMINI_API_KEY=your_key
    set DASHSCOPE_API_KEY=your_key
    python gemini_vs_qwen.py
"""

import os
import sys

# Try to import required libraries
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Run: pip install google-generativeai")

try:
    import dashscope
    from dashscope import Generation
    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False
    print("Warning: dashscope not installed. Run: pip install dashscope")


class SimpleAgent:
    """Simple agent that can use Gemini or Qwen"""
    
    def __init__(self, name: str, provider: str, api_key: str = None, model: str = None):
        self.name = name
        self.provider = provider
        self.history = []
        
        if provider == 'gemini':
            if not GEMINI_AVAILABLE:
                raise ImportError("Google Generative AI not installed")
            self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
            if not self.api_key:
                raise ValueError("Gemini API key not provided")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model or 'gemini-2.0-flash-exp')

        elif provider == 'qwen':
            if not QWEN_AVAILABLE:
                raise ImportError("DashScope not installed")
            self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY", "")
            if not self.api_key:
                raise ValueError("DashScope API key not provided")
            dashscope.api_key = self.api_key
            self.model_name = model or 'qwen2.5-72b-instruct'
    
    def ask(self, question: str, system_prompt: str = "") -> str:
        """Ask the agent a question"""
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": question})
        
        if self.provider == 'gemini':
            return self._ask_gemini(messages)
        elif self.provider == 'qwen':
            return self._ask_qwen(messages)
    
    def _ask_gemini(self, messages: list) -> str:
        """Query Gemini"""
        # Convert to Gemini format
        system_prompt = ""
        user_msg = ""
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"] + "\n\n"
            elif msg["role"] == "user":
                user_msg = msg["content"]
        
        full_prompt = system_prompt + user_msg
        response = self.model.generate_content(full_prompt)
        return response.text
    
    def _ask_qwen(self, messages: list) -> str:
        """Query Qwen via DashScope"""
        response = Generation.call(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=2048
        )
        
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            raise Exception(f"Qwen API error: {response.code} - {response.message}")


def debate(topic: str, rounds: int = 3):
    """Run a debate between Gemini and Qwen"""
    
    print("\n" + "=" * 70)
    print("  GEMINI vs QWEN DEBATE")
    print("=" * 70)
    print(f"\nTopic: {topic}")
    print(f"Rounds: {rounds}")
    print("-" * 70)
    
    # Create agents
    gemini = SimpleAgent("Gemini", "gemini")
    qwen = SimpleAgent("Qwen", "qwen")
    
    # System prompts
    gemini_prompt = f"""You are debating the topic: "{topic}"
You are taking the AFFIRMATIVE side (supporting the topic).
Present logical arguments, use evidence and reasoning.
Be concise but persuasive. Keep responses under 200 words."""

    qwen_prompt = f"""You are debating the topic: "{topic}"
You are taking the NEGATIVE side (opposing the topic).
Present logical arguments, use evidence and reasoning.
Be concise but persuasive. Keep responses under 200 words."""
    
    # Opening statements
    print("\n--- ROUND 1: Opening Statements ---\n")
    
    print(f"**Gemini (Affirmative):**")
    gemini_arg = gemini.ask(gemini_prompt, "You are a debater.")
    print(gemini_arg)
    print()
    
    print(f"**Qwen (Negative):**")
    qwen_arg = qwen.ask(qwen_prompt, "You are a debater.")
    print(qwen_arg)
    print()
    
    # Debate rounds
    for round_num in range(2, rounds + 1):
        print(f"--- ROUND {round_num}: Rebuttals ---\n")
        
        # Gemini rebuts Qwen
        print(f"**Gemini (rebutting Qwen):**")
        gemini_rebuttal = gemini.ask(
            f"Previous argument by Qwen: {qwen_arg}\n\n" + gemini_prompt + 
            "\n\nRebut their points and strengthen your position.",
            "You are a debater."
        )
        print(gemini_rebuttal)
        print()
        
        # Qwen rebuts Gemini
        print(f"**Qwen (rebutting Gemini):**")
        qwen_rebuttal = qwen.ask(
            f"Previous argument by Gemini: {gemini_arg}\n\n" + qwen_prompt +
            "\n\nRebut their points and strengthen your position.",
            "You are a debater."
        )
        print(qwen_rebuttal)
        print()
        
        # Update for next round
        gemini_arg = gemini_rebuttal
        qwen_arg = qwen_rebuttal
    
    # Closing statements
    print("--- CLOSING STATEMENTS ---\n")
    
    print(f"**Gemini (Closing):**")
    gemini_closing = gemini.ask(
        gemini_prompt + "\n\nProvide a strong closing statement summarizing your key points.",
        "You are a debater."
    )
    print(gemini_closing)
    print()
    
    print(f"**Qwen (Closing):**")
    qwen_closing = qwen.ask(
        qwen_prompt + "\n\nProvide a strong closing statement summarizing your key points.",
        "You are a debater."
    )
    print(qwen_closing)
    print()
    
    print("=" * 70)
    print("  DEBATE COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    # Check if API keys are set
    if not os.getenv("GEMINI_API_KEY"):
        print("\n⚠️  GEMINI_API_KEY not set!")
        print("   Get your key from: https://makersuite.google.com/app/apikey")
        print("   Then run: set GEMINI_API_KEY=your_key\n")
    
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("\n⚠️  DASHSCOPE_API_KEY not set!")
        print("   Get your key from: https://dashscope.console.aliyun.com/")
        print("   Then run: set DASHSCOPE_API_KEY=your_key\n")
    
    # Get debate topic
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("\nEnter debate topic: ").strip()
        while not topic:
            topic = input("Enter debate topic: ").strip()
    
    # Get number of rounds
    rounds_input = input("Number of rounds (default 3): ").strip()
    rounds = int(rounds_input) if rounds_input.isdigit() else 3
    
    # Run the debate
    try:
        debate(topic, rounds)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. Installed required packages: pip install google-generativeai dashscope")
        print("  2. Set your API keys:")
        print("     set GEMINI_API_KEY=your_key")
        print("     set DASHSCOPE_API_KEY=your_key")
