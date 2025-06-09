# pip install bitsandbytes accelerate xformers peft trl triton cut_cross_entropy unsloth_zoo sentencepiece protobuf huggingface_hub hf_transfer wandb python-dotenv unsloth kagglehub

from unsloth import FastVisionModel, is_bf16_supported
from unsloth.trainer import UnslothVisionDataCollator
import os
from dotenv import load_dotenv

load_dotenv()

WANDB_TOKEN = os.getenv("WANDB_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
VERSION = os.getenv("VERSION")
DIR = f"outputs/{VERSION}"

os.environ["WANDB_RUN_ID"] = VERSION
os.environ["WANDB_PROJECT"] = "7gr"
os.environ["WANDB_LOG_MODEL"] = 'false'
os.environ["WANDB_CONSOLE"] = 'off'

import torch
import kagglehub
import pandas as pd
from PIL import Image
from trl import SFTTrainer, SFTConfig
import wandb
from transformers import EarlyStoppingCallback

wandb.login(key=WANDB_TOKEN)

# 4bit pre quantized models we support for 4x faster downloading + no OOMs.
# fourbit_models = [
#     "unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit", # Llama 3.2 vision support
#     "unsloth/Llama-3.2-11B-Vision-bnb-4bit",
#     "unsloth/Llama-3.2-90B-Vision-Instruct-bnb-4bit", # Can fit in a 80GB card!
#     "unsloth/Llama-3.2-90B-Vision-bnb-4bit",
#
#     "unsloth/Pixtral-12B-2409-bnb-4bit",              # Pixtral fits in 16GB!
#     "unsloth/Pixtral-12B-Base-2409-bnb-4bit",         # Pixtral base model
#
#     "unsloth/Qwen2-VL-2B-Instruct-bnb-4bit",          # Qwen2 VL support
#     "unsloth/Qwen2-VL-7B-Instruct-bnb-4bit",
#     "unsloth/Qwen2-VL-72B-Instruct-bnb-4bit",
#
#     "unsloth/llava-v1.6-mistral-7b-hf-bnb-4bit",      # Any Llava variant works!
#     "unsloth/llava-1.5-7b-hf-bnb-4bit",
# ] # More models at https://huggingface.co/unsloth

model, tokenizer = FastVisionModel.from_pretrained(
    "unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit",
    load_in_4bit = True, # Use 4bit to reduce memory use. False for 16bit LoRA.
    use_gradient_checkpointing = "unsloth", # True or "unsloth" for long context
)

model = FastVisionModel.get_peft_model(
    model,
    finetune_vision_layers     = False,
    finetune_language_layers   = True,
    finetune_attention_modules = True,
    finetune_mlp_modules       = True,

    r = 16,
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
    # target_modules = "all-linear", # Optional now! Can specify a list if needed
)

path = kagglehub.dataset_download("fmena14/crowd-counting")
df = pd.read_csv(f"{path}/labels.csv")

dataset = []

for row in df.values:
#     with open(f"{path}/frames/frames/seq_{row[0]:06}.jpg", "rb") as f:
#         image_data = f.read()
    conversation = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"How many people are visible in the image? Count every person you can see clearly. Return only the number."
                },
                {
                    "type": "image",
                    "image": f"{path}/frames/frames/seq_{row[0]:06}.jpg"
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": row[1]
                }
            ]
        },
    ]

    dataset.append({"messages": conversation})

dataset_size = len(dataset)
train_dataset_size = dataset_size - 100
train_dataset = dataset[:train_dataset_size]
eval_dataset = dataset[train_dataset_size:]

FastVisionModel.for_training(model)

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    data_collator = UnslothVisionDataCollator(model, tokenizer),
    train_dataset = train_dataset,
    eval_dataset = eval_dataset,
    args = SFTConfig(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        per_device_eval_batch_size = 2,
        eval_accumulation_steps = 4,
        warmup_steps = 100,
        learning_rate = 0.00001,
        fp16 = not is_bf16_supported(),
        bf16 = is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = DIR,
        report_to = "wandb",

        remove_unused_columns = True,
        dataset_text_field = "",
        dataset_kwargs = {"skip_prepare_dataset": True},
        dataset_num_proc = 4,
        max_seq_length = 2048,

        save_steps = 10,
        save_strategy = "steps",
        save_total_limit = 10,
        eval_strategy = "steps",
        eval_steps = 10,

        run_name = VERSION,
        load_best_model_at_end = True
    ),
    callbacks = [
        EarlyStoppingCallback(early_stopping_patience=3),
    ]
)

trainer_stats = trainer.train()

# model.save_pretrained("lora_model")
# tokenizer.save_pretrained("lora_model")
# model.push_to_hub("lapaliv/7gr-model", token = HF_TOKEN)
# tokenizer.push_to_hub("lapaliv/7gr-tokenizer", token = HF_TOKEN)

model.save_pretrained_merged(DIR, tokenizer, "merged_16bit")
model.push_to_hub_merged(f"lapaliv/7gr-{VERSION}", tokenizer, "merged_16bit", token = HF_TOKEN)
