from layers import TranslateLayer, ShortenLayer, Sequential, MinguoLayer, ModernLayer, RewriteLayer
from openai import OpenAI
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    client = OpenAI()

    agent = Sequential(
        TranslateLayer(client),
        RewriteLayer(client),
        RewriteLayer(client),
        RewriteLayer(client),
    )

    text = open("text.md", "r").read()
    result, process = agent(text, verbose=True, return_process=True)
    print(result)
    # save result to file
    with open("result.md", "w") as f:
        f.write(result)
        # add process to file
        for i, p in enumerate(process):
            f.write(f"\n## Step {i+1}:\n")
            f.write(p)
            f.write("\n")