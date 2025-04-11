# pip install git+https://github.com/kossum/llama-cpp-python.git@main

from llama_cpp import Llama
from llama_cpp.llama_chat_format import Gemma3ChatHandler
import huggingface_hub
from dotenv import load_dotenv

import os
import base64

prompt = "What are objects in the image?"

def get_checkpoint():
    os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = "true"
    load_dotenv()

    huggingface_hub.login(os.environ['HUGGINGFACE'])

    model_path = huggingface_hub.snapshot_download(
        repo_id="google/gemma-3-4b-it-qat-q4_0-gguf",
        local_dir= os.path.join(os.path.dirname(__file__), ".checkpoints")
    )

    print(model_path)

if __name__ == "__main__":
    get_checkpoint()

    chat_handler = Gemma3ChatHandler(
        clip_model_path=os.path.join(os.path.dirname(__file__), ".checkpoints","mmproj-model-f16-4B.gguf")
    )

    llm = Llama(
        model_path=os.path.join(os.path.dirname(__file__), ".checkpoints","gemma-3-4b-it-q4_0.gguf"),
        n_threads=1,
        # n_batch=2,
        n_ctx = 2048+1024,
        verbose= False,
        chat_handler = chat_handler
        # chat_format="gemma",
    )


    def image_to_base64_data_uri(file_path: str):
        with open(file_path, "rb") as img_file:
            base64_data = base64.b64encode(img_file.read()).decode('utf-8')
            return f"data:image/png;base64,{base64_data}"

    response = llm.create_chat_completion(
        messages = [
            {"role": "system", "content": "You are a helpfull assistant"},
            {
                "role": "user",
                "content": [
                    {"type" : "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_to_base64_data_uri("page-2.png")}
                    }
                ]
            }
        ],
        response_format={
            "type": "json_object",
        },
        # response_format={
        #     "type": "json_object",
        #     "schema": {
        #         "type": "object",
        #         "properties": {
        #             "object_name": {"type": "string"},
        #             "number of objects": {"type": "integer"}
        #         },
        #         "required": ["object_name"],
        #     },
        # },
        stop=['<end_of_turn>', '<eos>'],
        temperature=0.1,
    )

    print(response)