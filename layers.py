from tqdm import tqdm
from prompts import *
from openai import OpenAI
from openai.types.completion import Completion

class ProcessLayer:
    def __init__(self, client: OpenAI):
        self.client = client

    def forward(self, text: str, **kwargs) -> str:
        pass
    
    def __call__(self, text: str, **kwargs) -> str:
        return self.forward(text, **kwargs)
    
    @staticmethod
    def get_reply_text(completion: "Completion") -> str:
        if len(completion.choices) == 1:
            return completion.choices[0].message.content
        else:
            return [choice.message.content for choice in completion.choices]

class TranslateLayer(ProcessLayer):
    def __init__(self, client: OpenAI):
        super().__init__(client)
        self.prompt_sys = prompt_sys_translate

    def forward(self, text: str, **kwargs) -> str:
        completion = self.client.beta.chat.completions.parse(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": self.prompt_sys},
                {"role": "user", "content": text},
            ],
            **kwargs,
        )

        return self.get_reply_text(completion)

class ShortenLayer(ProcessLayer):
    def __init__(self, client: OpenAI):
        super().__init__(client)
        self.prompt_sys = prompt_sys_shorten

    def forward(self, text: str, **kwargs) -> str:
        completion = self.client.beta.chat.completions.parse(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": self.prompt_sys},
                {"role": "user", "content": text},
            ],
            **kwargs,
        )
        return self.get_reply_text(completion)


class Sequential(ProcessLayer):
    def __init__(self, *layers: ProcessLayer):
        self.layers = layers

    def forward(self, text: str, verbose: bool = False, **kwargs) -> str:
        for layer in tqdm(self.layers, desc="Processing layers", disable=not verbose):
            text = layer(text, **kwargs)
        return text