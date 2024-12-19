from tqdm import tqdm
from prompts import *
from openai import OpenAI
from openai.types.completion import Completion

class ProcessLayer:
    def __init__(self, client: OpenAI):
        self.client = client
        self.prompt_sys = ""

    def forward(self, text: str, api_kwargs: dict = {}, **kwargs) -> str:
        completion = self.client.beta.chat.completions.parse(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": self.prompt_sys},
                {"role": "user", "content": text},
            ],
            **api_kwargs,
        )
        return self.get_reply_text(completion)
    
    def __call__(self, text: str, api_kwargs: dict = {}, **kwargs) -> str:
        return self.forward(text, api_kwargs=api_kwargs, **kwargs)
    
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

class ShortenLayer(ProcessLayer):
    def __init__(self, client: OpenAI):
        super().__init__(client)
        self.prompt_sys = prompt_sys_shorten

class MinguoLayer(ProcessLayer):
    def __init__(self, client: OpenAI):
        super().__init__(client)
        self.prompt_sys = prompt_sys_minguo

class ModernLayer(ProcessLayer):
    def __init__(self, client: OpenAI):
        super().__init__(client)
        self.prompt_sys = prompt_sys_modern

class RewriteLayer(ProcessLayer):
    def __init__(self, client: OpenAI):
        super().__init__(client)
        self.prompt_sys = prompt_sys_rewrite

class Sequential(ProcessLayer):
    def __init__(self, *layers: ProcessLayer):
        self.layers = layers

    def forward(self, text: str, verbose: bool = False, return_process: bool = False, **kwargs) -> str:
        if return_process:
            process = []
        for layer in tqdm(self.layers, desc="Processing layers", disable=not verbose):
            text = layer(text, **kwargs)
            if return_process:
                process.append(text)
        if return_process:
            return text, process
        return text