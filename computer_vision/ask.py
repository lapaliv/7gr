# !pip install torch transformers pillow accelerate --root-user-action ignore

import requests
import torch
from PIL import Image
from transformers import MllamaForConditionalGeneration, AutoProcessor

MODEL_NAME = os.getenv("MODEL_NAME")
VERSION = os.getenv("VERSION")
MODEL_ID = f"{MODEL_NAME}-{VERSION}"

def get_number_of_people(image_url):
    model = MllamaForConditionalGeneration.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    ).to("cuda")
    processor = AutoProcessor.from_pretrained(model_id)

    image = Image.open(requests.get(image_url, stream=True).raw)

    messages = [
        {"role": "user", "content": [
            {"type": "image"},
            {"type": "text", "text": "How many people are visible in the image? Count every person you can see clearly. Return only the number in integer format. Just reply with the number, no explanation."}
        ]}
    ]
    input_text = processor.apply_chat_template(messages, add_generation_prompt=True)

    inputs = processor(
        image,
        input_text,
        add_special_tokens=False,
        return_tensors="pt"
    ).to(model.device)

    output = model.generate(**inputs, max_new_tokens=30)
    answer = processor.decode(output[0])
    answer = answer.replace(input_text, "")
    answer = answer.replace(processor.tokenizer.eos_token, "")

    return int(answer)
