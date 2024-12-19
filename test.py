from layers import ProcessLayer, TranslateLayer, ShortenLayer, Sequential, MinguoLayer, ModernLayer, RewriteLayer, JSONLayer
from prompts import *
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List


class ProfessorLayer(ProcessLayer):
    def __init__(self, client: OpenAI):
        super().__init__(client)
        self.prompt_sys = prompt_sys_professor

class Chooser(BaseModel):
    reason: str
    best_translation_index: int

class ChooserLayer(JSONLayer):
    def __init__(self, client: OpenAI):
        super().__init__(client)
        self.prompt_sys = prompt_sys_chooser
        self.schema = Chooser
    
    def prepare_user_text(self, texts: List[str], original: str) -> str:
        # check if texts is a list
        if not isinstance(texts, list):
            raise ValueError(f"texts must be a list, but got: {type(texts)}")
        translations = "\n".join([f"翻译版本 {i}: {t}" for i, t in enumerate(texts)])
        return f"原文：{original}\n{translations}"

    def forward(self, texts: List[str], original: str, api_kwargs: dict = {}, **kwargs) -> str:
        if self.schema is None:
            raise ValueError("Schema is not set")
        
        print("[Chooser] user text:", self.prepare_user_text(texts, original=original))
        completion = self.client.beta.chat.completions.parse(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": self.prompt_sys},
                {"role": "user", "content": self.prepare_user_text(texts, original=original)},
            ],
            response_format=self.schema,
        )
        return self.get_reply_json(completion)

class CollabLayer(ProcessLayer):
    def __init__(self, client: OpenAI, n: int = 3):
        super().__init__(client)
        self.professor = ProfessorLayer(client)
        self.chooser = ChooserLayer(client)
        self.n = n
    
    def forward(self, text: str, original: str, **kwargs) -> str:
        # Pass original as part of kwargs
        texts = self.professor(text, n=self.n, **kwargs)
        print(f'professor:\n{texts}')
        choice = self.chooser(texts, original=original, **kwargs)
        print(f'chooser:\n{choice}')
        return texts[choice['best_translation_index']]


if __name__ == "__main__":
    load_dotenv()
    client = OpenAI()

    agent = Sequential(
        TranslateLayer(client),
        CollabLayer(client),
        CollabLayer(client),
        CollabLayer(client),
    )

    text = open("text.md", "r").read()
    result, process = agent(text, verbose=True, return_process=True, original=text)
    print(result)
    # save result to file
    with open("result.md", "w") as f:
        f.write(result)
        # add process to file
        for i, p in enumerate(process):
            f.write(f"\n## Step {i+1}:\n")
            f.write(p)
            f.write("\n")