from layers import ProcessLayer, TranslateLayer, ShortenLayer, Sequential, MinguoLayer, ModernLayer, RewriteLayer
from prompts import prompt_sys_revise, prompt_sys_professor
from openai import OpenAI
from dotenv import load_dotenv

class ReviseLayer(ProcessLayer):
    def __init__(self, client: OpenAI):
        super().__init__(client)
        self.prompt_sys = prompt_sys_revise
    
    def forward(self, text: str, original: str, api_kwargs: dict = {}, **kwargs) -> str:
        input = f"原文：{original}\n翻译：{text}"
        completion = self.client.beta.chat.completions.parse(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": self.prompt_sys},
                {"role": "user", "content": input},
            ],
            **api_kwargs,
        )
        return self.get_reply_text(completion)

class ProfessorLayer(ProcessLayer):
    def __init__(self, client: OpenAI):
        super().__init__(client)
        self.prompt_sys = prompt_sys_professor

class CollabLayer(ProcessLayer):
    def __init__(self, client: OpenAI):
        super().__init__(client)
        self.revise = ReviseLayer(client)
        self.professor = ProfessorLayer(client)
    
    def forward(self, text: str, original: str, **kwargs) -> str:
        # Pass original as part of kwargs
        text = self.professor(text, **kwargs)
        print(f'professor:\n{text}')
        text = self.revise(text, original=original, **kwargs)
        print(f'revise:\n{text}')
        return text


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