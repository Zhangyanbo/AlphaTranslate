import json
from openai import OpenAI
from dotenv import load_dotenv
from alphatranslate import Sequential, TranslateLayer, CollabLayer

def split_article_by_section(article: str) -> list[str]:
    parts = article.split('## ')
    return ['## ' + part if i > 0 else part for i, part in enumerate(parts)]

def split_by_length(article: str, max_length: int=2048) -> list[str]:
    parts = article.split('\n')
    cutted_parts = []

    while len(parts) > 0:
        temp = ''
        while len(temp) < max_length and len(parts) > 0:
            temp += parts.pop(0) + '\n'
        cutted_parts.append(temp)
    return cutted_parts

if __name__ == "__main__":
    with open('./data/article.md', 'r') as f:
        article = f.read()
    parts = split_by_length(article)
    # save to json
    with open('./data/items.json', 'w') as f:
        json.dump(parts, f, indent=4)

    # load from json
    with open('./data/items.json', 'r') as f:
        items = json.load(f)
    
    load_dotenv()
    client = OpenAI()

    # load reference
    with open('./data/reference.md', 'r') as f:
        reference = f.read()

    # load init
    with open('./data/init.md', 'r') as f:
        init = f.read()

    agent = Sequential(
        TranslateLayer(client, reference),
        CollabLayer(client, n=8, reference=reference),
        CollabLayer(client, n=8, reference=reference),
        CollabLayer(client, n=8, reference=reference),
    )

    results = []
    processes = []  

    for i, item in enumerate(items):
        print(f'Processing {i+1} / {len(items)}')
        if init != "":
            result = init
            process = []
        else:
            result, process = agent(item, verbose=True, return_process=True, original=item)

        results.append(result)
        processes.append(process)
        init = ""
        
        # Save intermediate results in real time
        current_result = '\n\n'.join(results)
        with open('./data/final_result.md', 'w') as f:
            f.write(current_result)
    
    # save finalprocess to json
    with open('./data/final_process.json', 'w') as f:
        json.dump(processes, f, indent=4, ensure_ascii=False)
