import json
import statistics

ingpt = "./src/pipeline/Baseline_29July2024.json"
inllava = "./src/pipeline/LLaVA_1August2024.json"
insamgpt = "./src/pipeline/gpt4o+samsafetyscore.json"
insamllava = "./src/pipeline/samllava_2August2024.json"


def getlen(filepath, name):
    data = []
    with open(filepath, 'r') as f:
        data = json.load(f)

    count = 0

    for i in range(10):
        pred = data[i]["Model Predictions"]

        for j in pred:
            if '(' in j:
                count += 1
    print(name + ":")
    print("Count: " + str(count))

getlen(ingpt, "GPT-4o")

getlen(inllava, "Video-LLaVA")

getlen(insamgpt, "SAM + GPT-4o")

getlen(insamllava, "SAM + Video-LLaVA")

