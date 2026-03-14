import os
import json
import random
from code.utils.agent import Agent


# API Keys - Set your keys here or use environment variables
openai_api_key = os.getenv("OPENAI_API_KEY", "Your-OpenAI-Api-Key")
gemini_api_key = os.getenv("GEMINI_API_KEY", "Your-Gemini-Api-Key")
dashscope_api_key = os.getenv("DASHSCOPE_API_KEY", "Your-DashScope-Api-Key")

# Model presets
MODEL_PRESETS = {
    'gemini': 'gemini-2.0-flash-exp',
    'qwen': 'qwen2.5-72b-instruct',
    'openai': 'gpt-4o-mini',
}

NAME_LIST=[
    "Affirmative side",
    "Negative side",
    "Moderator",
]

class DebatePlayer(Agent):
    def __init__(self, model_name: str, name: str, temperature:float, 
                 openai_api_key: str = None, gemini_api_key: str = None, 
                 dashscope_api_key: str = None, sleep_time: float = 0) -> None:
        """Create a player in the debate

        Args:
            model_name(str): model name
            name (str): name of this player
            temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
            openai_api_key (str): OpenAI API key
            gemini_api_key (str): Gemini API key
            dashscope_api_key (str): DashScope API key for Qwen
            sleep_time (float): sleep because of rate limits
        """
        super(DebatePlayer, self).__init__(
            model_name, name, temperature, sleep_time,
            openai_api_key=openai_api_key,
            gemini_api_key=gemini_api_key,
            dashscope_api_key=dashscope_api_key
        )
        # Store keys for compatibility
        self.openai_api_key = openai_api_key


class Debate:
    def __init__(self,
            model_name: str='gpt-3.5-turbo',
            temperature: float=0,
            num_players: int=3,
            openai_api_key: str=None,
            gemini_api_key: str=None,
            dashscope_api_key: str=None,
            config: dict=None,
            max_round: int=3,
            sleep_time: float=0
        ) -> None:
        """Create a debate

        Args:
            model_name (str): model name (supports OpenAI, Gemini, Qwen)
            temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
            num_players (int): num of players
            openai_api_key (str): OpenAI API key
            gemini_api_key (str): Gemini API key
            dashscope_api_key (str): DashScope API key for Qwen
            max_round (int): maximum Rounds of Debate
            sleep_time (float): sleep because of rate limits
        """

        self.model_name = model_name
        self.temperature = temperature
        self.num_players = num_players
        self.openai_api_key = openai_api_key
        self.gemini_api_key = gemini_api_key
        self.dashscope_api_key = dashscope_api_key
        self.config = config
        self.max_round = max_round
        self.sleep_time = sleep_time

        # creat&init agents
        self.creat_agents()
        self.init_agents()


    def init_agents(self):
        # start: set meta prompt
        self.affirmative.set_meta_prompt(self.config['player_meta_prompt'])
        self.negative.set_meta_prompt(self.config['player_meta_prompt'])
        self.moderator.set_meta_prompt(self.config['moderator_meta_prompt'])
        
        # start: first round debate, state opinions
        print(f"===== Debate Round-1 =====\n")
        self.affirmative.add_event(self.config['affirmative_prompt'])
        self.aff_ans = self.affirmative.ask()
        self.affirmative.add_memory(self.aff_ans)

        self.negative.add_event(self.config['negative_prompt'].replace('##aff_ans##', self.aff_ans))
        self.neg_ans = self.negative.ask()
        self.negative.add_memory(self.neg_ans)

        self.moderator.add_event(self.config['moderator_prompt'].replace('##aff_ans##', self.aff_ans).replace('##neg_ans##', self.neg_ans).replace('##round##', 'first'))
        self.mod_ans = self.moderator.ask()
        self.moderator.add_memory(self.mod_ans)
        self.mod_ans = eval(self.mod_ans)

    def round_dct(self, num: int):
        dct = {
            1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth', 6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth', 10: 'tenth'
        }
        return dct[num]
            
    def broadcast(self, msg: str):
        """Broadcast a message to all players. 
        Typical use is for the host to announce public information

        Args:
            msg (str): the message
        """
        # print(msg)
        for player in self.players:
            player.add_event(msg)

    def speak(self, speaker: str, msg: str):
        """The speaker broadcast a message to all other players. 

        Args:
            speaker (str): name of the speaker
            msg (str): the message
        """
        if not msg.startswith(f"{speaker}: "):
            msg = f"{speaker}: {msg}"
        # print(msg)
        for player in self.players:
            if player.name != speaker:
                player.add_event(msg)

    def ask_and_speak(self, player: DebatePlayer):
        ans = player.ask()
        player.add_memory(ans)
        self.speak(player.name, ans)

    def print_answer(self):
        print(f"===== Debate Conclusion =====\n")
        print(f"Whether there is a preference: {self.config['Whether there is a preference']}")
        print(f"Supported Side: {self.config['Supported Side']}")
        print(f"Reason: {self.config['Reason']}")
        print(f"Final Answer: {self.config['debate_answer']}")
        print(f"\n===== Debate End =====\n")

    def creat_agents(self):
        # creates players
        self.players = [
            DebatePlayer(
                model_name=self.model_name, 
                name=name, 
                temperature=self.temperature, 
                openai_api_key=self.openai_api_key,
                gemini_api_key=self.gemini_api_key,
                dashscope_api_key=self.dashscope_api_key,
                sleep_time=self.sleep_time
            ) for name in NAME_LIST
        ]
        self.affirmative = self.players[0]
        self.negative = self.players[1]
        self.moderator = self.players[2]

    def run(self):

        for round in range(self.max_round - 1):

            if self.mod_ans["Whether there is a preference"] == 'Yes':
                break
            else:
                print(f"===== Debate Round-{round+2} =====\n")
                self.affirmative.add_event(self.config['debate_prompt'].replace('##oppo_ans##', self.neg_ans))
                self.aff_ans = self.affirmative.ask()
                self.affirmative.add_memory(self.aff_ans)

                self.negative.add_event(self.config['debate_prompt'].replace('##oppo_ans##', self.aff_ans))
                self.neg_ans = self.negative.ask()
                self.negative.add_memory(self.neg_ans)

                self.moderator.add_event(self.config['moderator_prompt'].replace('##aff_ans##', self.aff_ans).replace('##neg_ans##', self.neg_ans).replace('##round##', self.round_dct(round+2)))
                self.mod_ans = self.moderator.ask()
                self.moderator.add_memory(self.mod_ans)
                self.mod_ans = eval(self.mod_ans)

        if self.mod_ans["Whether there is a preference"] == 'Yes':
            self.config.update(self.mod_ans)
            self.config['success'] = True

        # ultimate deadly technique.
        else:
            judge_player = DebatePlayer(
                model_name=self.model_name, 
                name='Judge', 
                temperature=self.temperature, 
                openai_api_key=self.openai_api_key,
                gemini_api_key=self.gemini_api_key,
                dashscope_api_key=self.dashscope_api_key,
                sleep_time=self.sleep_time
            )
            aff_ans = self.affirmative.memory_lst[2]['content']
            neg_ans = self.negative.memory_lst[2]['content']

            judge_player.set_meta_prompt(self.config['moderator_meta_prompt'])

            # extract answer candidates
            judge_player.add_event(self.config['judge_prompt_last1'].replace('##aff_ans##', aff_ans).replace('##neg_ans##', neg_ans))
            ans = judge_player.ask()
            judge_player.add_memory(ans)

            # select one from the candidates
            judge_player.add_event(self.config['judge_prompt_last2'])
            ans = judge_player.ask()
            judge_player.add_memory(ans)
            
            ans = eval(ans)
            if ans["debate_answer"] != '':
                self.config['success'] = True
                # save file
            self.config.update(ans)
            self.players.append(judge_player)

        self.print_answer()


if __name__ == "__main__":

    current_script_path = os.path.abspath(__file__)
    MAD_path = current_script_path.rsplit(os.sep, 1)[0]

    print("=" * 60)
    print("  Multi-Agent Debate System")
    print("  Supported Models: OpenAI, Gemini, Qwen")
    print("=" * 60)
    
    # Model selection
    print("\nAvailable model providers:")
    print("  1. openai  - Use OpenAI GPT models")
    print("  2. gemini  - Use Google Gemini models")
    print("  3. qwen    - Use Alibaba Qwen models")
    
    provider = ""
    while provider not in ['openai', 'gemini', 'qwen', '1', '2', '3']:
        provider = input(f"\nEnter model provider (openai/gemini/qwen): ").lower().strip()
    
    # Map number to provider
    provider_map = {'1': 'openai', '2': 'gemini', '3': 'qwen'}
    provider = provider_map.get(provider, provider)
    
    # Get model name (use preset or custom)
    use_preset = input(f"Use preset model for {provider}? (y/n): ").lower().strip()
    if use_preset == 'y':
        model_name = MODEL_PRESETS[provider]
        print(f"Using model: {model_name}")
    else:
        model_name = input(f"Enter model name (e.g., {MODEL_PRESETS[provider]}): ").strip()
        if not model_name:
            model_name = MODEL_PRESETS[provider]
    
    # API key selection based on provider
    api_key_openai = openai_api_key if provider == 'openai' else None
    api_key_gemini = gemini_api_key if provider == 'gemini' else None
    api_key_dashscope = dashscope_api_key if provider == 'qwen' else None
    
    print(f"\nUsing provider: {provider.upper()}")
    print(f"Using model: {model_name}")
    print("-" * 60)

    while True:
        debate_topic = ""
        while debate_topic == "":
            debate_topic = input(f"\nEnter your debate topic: ")

        config = json.load(open(f"{MAD_path}/code/utils/config4all.json", "r"))
        config['debate_topic'] = debate_topic

        debate = Debate(
            model_name=model_name,
            num_players=3, 
            openai_api_key=api_key_openai,
            gemini_api_key=api_key_gemini,
            dashscope_api_key=api_key_dashscope,
            config=config, 
            temperature=0, 
            sleep_time=0
        )
        debate.run()
