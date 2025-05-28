import transformers
import accelerate
import peft
from datasets import load_dataset

# print(f"Transformers version: {transformers.__version__}")
# print(f"Accelerate version: {accelerate.__version__}")
# print(f"PEFT version: {peft.__version__}")

model_checkpoint = "google/vit-base-patch16-224-in21k"

dataset = load_dataset("food101", split="train[:5000]")
