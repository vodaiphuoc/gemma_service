import huggingface_hub
from dotenv import load_dotenv
import os


def get_checkpoint():
    load_dotenv()

    huggingface_hub.login(os.environ['HUGGINGFACE'])


    model_path = huggingface_hub.hf_hub_download(
        repo_id="google/gemma-3-4b-it-qat-q4_0-gguf",
        filename="gemma-3-4b-it-q4_0.gguf",
        local_dir= '.checkpoints'
    )

    print(model_path)

if __name__ == "__main__":
    get_checkpoint()