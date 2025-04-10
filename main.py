from llama_cpp import Llama
import os
import base64


prompt = "Example of linear regression in python"


llm = Llama(
    model_path=os.path.join(os.path.dirname(__file__), ".checkpoints","gemma-3-4b-it-q4_0.gguf"),
    n_threads=1,
    n_batch=2,
    n_ctx=4096,
)

prompt_template="""
<start_of_turn>user
{user_prompt}<end_of_turn>
<start_of_turn>model
"""

def image_to_base64_data_uri(file_path: str):
    with open(file_path, "rb") as img_file:
        base64_data = base64.b64encode(img_file.read()).decode('utf-8')
        return f"data:image/png;base64,{base64_data}"

response = llm.create_chat_completion(
    messages = [
        {"role": "system", "content": "You are an assistant who perfectly describes images."},
        {
            "role": "user",
            "content": [
                {"type" : "text", "text": prompt_template.format(user_prompt = prompt)},
                {"type": "image_url",
                 "image_url": {
                    "url": image_to_base64_data_uri("testimg.jpg") 
                    }
                }
            ]
        }
    ],
    response_format={
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {"object_name": {"type": "string"}},
            "required": ["object_name"],
        },
    },
    temperature=0.7,
)

print(response)