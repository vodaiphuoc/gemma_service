from llama_cpp import Llama

llm = Llama(
    model_path=".checkpoints\gemma-3-4b-it-q4_0.gguf",
    n_threads=1, # CPU cores
    n_batch=2, # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
    # n_gpu_layers=30, # The max for this model is 30 in a T4, If you use llama 2 70B, you'll need to put fewer layers on the GPU
    n_ctx=131072, # Context window,
)

prompt = "Example of linear regression in python"
prompt_template=f'''Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{prompt}

### Response:'''


stream = llm(
    prompt_template,
    max_tokens=16, # Number of new tokens to be generated, increase it for a longer response
    temperature=0.8,
    top_p=0.95,
    repeat_penalty=1.2,
    top_k=50,
    echo=False,
    stream=True,
    stop=["Instruction:", "Response:"] # Stop generation when such token appears
)

response = ''
for output in stream:
    text_output = output['choices'][0]['text'].replace('\r', '')
    print("\033[34m" + text_output + "\033[0m", end ='')
    response += text_output

print(response)