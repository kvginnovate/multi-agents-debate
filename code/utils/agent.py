import backoff
import time
import re

# Provider imports
try:
    import openai
    from openai.error import RateLimitError, APIError, ServiceUnavailableError, APIConnectionError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import dashscope
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False

# Model support mapping
SUPPORT_MODELS = {
    'openai': ['gpt-3.5-turbo', 'gpt-3.5-turbo-0301', 'gpt-4', 'gpt-4-0314', 'gpt-4o', 'gpt-4o-mini'],
    'gemini': ['gemini-pro', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-2.0-flash-exp'],
    'qwen': ['qwen-turbo', 'qwen-plus', 'qwen-max', 'qwen-max-longcontext', 'qwen2.5-72b-instruct', 'qwen2.5-coder-32b-instruct'],
}

# Context limits for different models
MODEL2MAX_CONTEXT = {
    # OpenAI
    'gpt-3.5-turbo': 4096,
    'gpt-3.5-turbo-0301': 4096,
    'gpt-4': 8192,
    'gpt-4-0314': 8192,
    'gpt-4o': 128000,
    'gpt-4o-mini': 128000,
    # Gemini
    'gemini-pro': 30720,
    'gemini-1.5-pro': 2097152,
    'gemini-1.5-flash': 1048576,
    'gemini-2.0-flash-exp': 1048576,
    # Qwen
    'qwen-turbo': 8192,
    'qwen-plus': 32768,
    'qwen-max': 32768,
    'qwen-max-longcontext': 32768,
    'qwen2.5-72b-instruct': 32768,
    'qwen2.5-coder-32b-instruct': 32768,
}


def get_provider_from_model(model_name: str) -> str:
    """Determine which provider to use based on model name"""
    model_name_lower = model_name.lower()
    if any(m in model_name_lower for m in ['gemini']):
        return 'gemini'
    elif any(m in model_name_lower for m in ['qwen']):
        return 'qwen'
    else:
        return 'openai'


def num_tokens_from_string(text: str, model_name: str = "gpt-3.5-turbo") -> int:
    """Estimate number of tokens in a string"""
    try:
        import tiktoken
        encoding = tiktoken.encoding_for_model(model_name)
        return len(encoding.encode(text))
    except:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4


class Agent:
    def __init__(self, model_name: str, name: str, temperature: float, sleep_time: float = 0,
                 openai_api_key: str = None, gemini_api_key: str = None, dashscope_api_key: str = None) -> None:
        """Create an agent

        Args:
            model_name (str): model name
            name (str): name of this agent
            temperature (float): higher values make the output more random, lower values make it more focused
            sleep_time (float): sleep time between requests to avoid rate limits
            openai_api_key (str): OpenAI API key
            gemini_api_key (str): Google Gemini API key
            dashscope_api_key (str): Alibaba DashScope API key for Qwen
        """
        self.model_name = model_name
        self.name = name
        self.temperature = temperature
        self.memory_lst = []
        self.sleep_time = sleep_time
        
        # API keys
        self.openai_api_key = openai_api_key
        self.gemini_api_key = gemini_api_key
        self.dashscope_api_key = dashscope_api_key
        
        # Determine provider
        self.provider = get_provider_from_model(model_name)
        
        # Initialize provider-specific clients
        self._init_provider()

    def _init_provider(self):
        """Initialize the appropriate provider"""
        if self.provider == 'openai':
            if OPENAI_AVAILABLE and self.openai_api_key:
                openai.api_key = self.openai_api_key
            else:
                raise ValueError("OpenAI not available or API key not provided")
                
        elif self.provider == 'gemini':
            if GEMINI_AVAILABLE and self.gemini_api_key:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel(self.model_name)
            else:
                raise ValueError("Gemini not available or API key not provided")
                
        elif self.provider == 'qwen':
            if DASHSCOPE_AVAILABLE and self.dashscope_api_key:
                dashscope.api_key = self.dashscope_api_key
            else:
                raise ValueError("DashScope not available or API key not provided")

    @backoff.on_exception(backoff.expo, Exception, max_tries=20)
    def query(self, messages: list, max_tokens: int, temperature: float) -> str:
        """Make a query to the LLM provider

        Args:
            messages (list): chat history
            max_tokens (int): max tokens in response
            temperature (float): sampling temperature

        Returns:
            str: generated response
        """
        time.sleep(self.sleep_time)
        
        if self.provider == 'openai':
            return self._query_openai(messages, max_tokens, temperature)
        elif self.provider == 'gemini':
            return self._query_gemini(messages, temperature)
        elif self.provider == 'qwen':
            return self._query_qwen(messages, temperature)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _query_openai(self, messages: list, max_tokens: int, temperature: float) -> str:
        """Query OpenAI API"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed")
        
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=self.openai_api_key,
        )
        return response['choices'][0]['message']['content']

    def _query_gemini(self, messages: list, temperature: float) -> str:
        """Query Google Gemini API"""
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI package not installed")
        
        # Convert OpenAI format to Gemini format
        # Gemini doesn't use system messages the same way, so we prepend it
        system_prompt = ""
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"] + "\n\n"
            elif msg["role"] == "user":
                chat_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                chat_messages.append({"role": "model", "parts": [msg["content"]]})
        
        # Prepend system prompt to first user message
        if chat_messages and chat_messages[0]["role"] == "user":
            chat_messages[0]["parts"][0] = system_prompt + chat_messages[0]["parts"][0]
        
        # Start chat with history
        chat = self.gemini_model.start_chat(history=chat_messages[:-1] if len(chat_messages) > 1 else [])
        
        # Generation config
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        # Send message and get response
        if len(chat_messages) > 0:
            last_message = chat_messages[-1]["parts"][0]
            response = chat.send_message(last_message, generation_config=generation_config)
        else:
            response = self.gemini_model.generate_content(system_prompt, generation_config=generation_config)
        
        return response.text

    def _query_qwen(self, messages: list, temperature: float) -> str:
        """Query Alibaba Qwen via DashScope"""
        if not DASHSCOPE_AVAILABLE:
            raise ImportError("DashScope package not installed")
        
        # Convert messages to DashScope format
        # DashScope uses the same format as OpenAI
        response = Generation.call(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=self.dashscope_api_key,
        )
        
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            raise Exception(f"Qwen API error: {response.code} - {response.message}")

    def set_meta_prompt(self, meta_prompt: str):
        """Set the meta prompt (system message)

        Args:
            meta_prompt (str): the meta prompt
        """
        self.memory_lst.append({"role": "system", "content": f"{meta_prompt}"})

    def add_event(self, event: str):
        """Add a new event to memory

        Args:
            event (str): string describing the event
        """
        self.memory_lst.append({"role": "user", "content": f"{event}"})

    def add_memory(self, memory: str):
        """Add model's own response to memory

        Args:
            memory (str): string generated by the model in the last round
        """
        self.memory_lst.append({"role": "assistant", "content": f"{memory}"})
        print(f"----- {self.name} -----\n{memory}\n")

    def ask(self, temperature: float = None):
        """Query for answer

        Returns:
            str: generated response
        """
        # Calculate context length
        num_context_token = sum([num_tokens_from_string(m["content"], self.model_name) for m in self.memory_lst])
        max_context = MODEL2MAX_CONTEXT.get(self.model_name, 8192)
        max_token = max_context - num_context_token
        
        # Ensure max_token is positive
        max_token = max(100, min(max_token, 4096))
        
        return self.query(
            self.memory_lst,
            max_token,
            temperature=temperature if temperature else self.temperature
        )
