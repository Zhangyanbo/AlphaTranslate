from tqdm import tqdm
from .prompts import *
from openai import OpenAI
from openai.types.completion import Completion
import json

class ProcessLayer:
    def __init__(self, client: OpenAI):
        self.client = client
        self.prompt_sys = ""
    
    def prepare_user_text(self, text: str, **kwargs) -> str:
        return f"{text}"

    def forward(self, text: str, api_kwargs: dict = {}, n=1, **kwargs) -> str:
        # print self name
        print(f'[{self.__class__.__name__}] system prompt:\n', self.prompt_sys, '\n')
        print(f'[{self.__class__.__name__}] user prompt:\n', self.prepare_user_text(text, **kwargs), '\n')
        completion = self.client.beta.chat.completions.parse(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": self.prompt_sys},
                {"role": "user", "content": self.prepare_user_text(text, **kwargs)},
            ],
            n=n,
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


class JSONLayer:
    def __init__(self, client: OpenAI):
        self.client = client
        self.prompt_sys = ""
        self.schema = None
    
    def prepare_user_text(self, text: str, **kwargs) -> str:
        return text

    def forward(self, text: str, api_kwargs: dict = {}, **kwargs) -> str:
        if self.schema is None:
            raise ValueError("Schema is not set")
        print(f'[{self.__class__.__name__}] system prompt:\n', self.prompt_sys, '\n')
        print(f'[{self.__class__.__name__}] user prompt:\n', self.prepare_user_text(text, **kwargs), '\n')
        completion = self.client.beta.chat.completions.parse(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": self.prompt_sys},
                {"role": "user", "content": self.prepare_user_text(text, **kwargs)},
            ],
            response_format=self.schema,
            **api_kwargs,
        )
        return self.get_reply_json(completion)
    
    def __call__(self, text: str, api_kwargs: dict = {}, **kwargs) -> str:
        return self.forward(text, api_kwargs=api_kwargs, **kwargs)
    
    @staticmethod
    def get_reply_json(completion: "Completion") -> dict:
        if len(completion.choices) == 1:
            return json.loads(completion.choices[0].message.content)
        else:
            return [json.loads(choice.message.content) for choice in completion.choices]

class TranslateLayer(ProcessLayer):
    def __init__(self, client: OpenAI, reference: str):
        super().__init__(client)
        self.prompt_sys = prompt_sys_translate.format(reference=reference)

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