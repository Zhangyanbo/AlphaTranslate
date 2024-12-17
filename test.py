from layers import TranslateLayer, ShortenLayer, Sequential
from openai import OpenAI
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    client = OpenAI()

    agent = Sequential(
        TranslateLayer(client),
        ShortenLayer(client)
    )

    text = open("text.md", "r").read()
    result = agent(text, verbose=True)
    print(result)
    # save result to file
    with open("result.md", "w") as f:
        f.write(result)
