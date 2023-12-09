from typing import List
import argparse
import json
import random
import openai

from datasets import Dataset, load_dataset

from multi_token.constants import ROLE_ASSISTANT, ROLE_USER

PROMPT = """
You are helping train a chat vision assistant that can take several image inputs and output text.

Here are the images you can see:
{captions}

{question}
"""

QUESTIONS = [
    "Using the images and their captions above, ask a complex question about the relationship between the images.",
    "Ask a question that reasons about ALL of the images, for example, asking about how they are related or how one might lead to the other.",
    "Ask a question that reasons about ALL of the images, for example, asking about the relationship between objects in the images, asking about the location of objects in the images, etc.",
    "Ask a complex question that is relevant to the content some of images, for example, asking about background knowledge of the objects in the images, asking to discuss about events happening in the images, etc. Do not ask about uncertain details.",
    "Ask about the similarities among the provided images.",
    "Ask about the differences among the provided images.",
    "Ask about the last image.",
    "Ask about the first image.",
    "Ask about your thoughts on the images.",
    "Ask about how to use the items in the images.",
    "Ask a question that relates to the order of the images.",
    "Ask a question that relates to the numbering of the images.",
]

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_chat",
            "description": "Create a training example",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                    },
                    "answer": {
                        "type": "string",
                    },
                },
                "required": ["question", "answer"],
            },
        },
    }
]


def _build_convo(pretrain_examples) -> List:
    client = openai.Client()

    captions = [e["messages"][1]["content"] for e in pretrain_examples]
    paths = [e["images"][0] for e in pretrain_examples]

    captions_text = "\n".join(
        [f"Image {i+1} - {cap}" for i, cap in enumerate(captions)]
    )
    prompt = PROMPT.format(
        captions=captions_text, question=random.choice(QUESTIONS)
    ).strip()

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{"role": "system", "content": prompt}],
        tools=OPENAI_TOOLS,
        tool_choice={"type": "function", "function": {"name": "create_chat"}},
    )
    resp = json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
    q = resp["question"]
    a = resp["answer"]

    if random.choice([True, False]):
        q = "<image>" * len(captions) + " " + q
    else:
        q = q + " " + "<image>" * len(captions)

    example = {
        "images": paths,
        "messages": [
            {
                "role": ROLE_USER,
                "content": q,
            },
            {
                "role": ROLE_ASSISTANT,
                "content": a,
            },
        ],
    }
    return example


def main(args):
    data = load_dataset("sshh12/llava-pretrain", split="train", data_files="*.arrow")

    idxs = list(range(len(data)))

    def gen():
        for _ in range(args.num_examples):
            k = random.randint(1, args.max_images)
            selected_idxs = random.sample(idxs, k=k)
            selected_examples = [data[i] for i in selected_idxs]
            try:
                yield _build_convo(selected_examples)
            except Exception as e:
                print(e)
                continue

    ds = Dataset.from_generator(gen)
    ds.save_to_disk(args.output_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output_folder",
        type=str,
        default="/data/llava-gpt-multi-image-finetune",
    )
    parser.add_argument("-n", "--num_examples", type=int, default=200_000)
    parser.add_argument("-m", "--max_images", type=int, default=6)
    args = parser.parse_args()
    main(args)
