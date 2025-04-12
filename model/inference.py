import onnxruntime_genai as og

import huggingface_hub
from dotenv import load_dotenv
import os



def get_checkpoint():
    os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = "true"
    load_dotenv()

    huggingface_hub.login(os.environ['HUGGINGFACE'])

    model_path = huggingface_hub.snapshot_download(
        repo_id = os.environ['REPO_ID'],
        allow_patterns= [f"{os.environ['PATTERN']}/*"],
        local_dir= os.path.dirname(__file__).replace("model","checkpoints")
    )
    print(model_path)

class Model_Handler(object):
    def __init__(self, 
                 checkpoint_path:str = os.path.dirname(__file__).replace("model","checkpoints",os.environ['PATTERN']), 
                 max_length: int = 7680
        )->None:
        get_checkpoint()
        print(checkpoint_path)
        self.max_length = max_length
        config = og.Config(checkpoint_path)
        config.clear_providers()
        config.append_provider('cuda')

        self.model = og.Model(config)
        self.processor = self.model.create_multimodal_processor()
        self.tokenizer_stream = self.processor.create_stream()

    def forward(self, 
                image_path: str,
                input_prompt: str,
                audios = None
        )->str:
        prompt = f"<|user|>\n<|image_{1}|>\n{input_prompt}<|end|>\n<|assistant|>\n"
        images = og.Images.open(image_path)

        inputs = self.processor(prompt, images=images, audios=audios)

        params = og.GeneratorParams(self.model)
        params.set_inputs(inputs)
        params.set_search_options(max_length=self.max_length)

        generator = og.Generator(self.model, params)

        outputs = ""
        while not generator.is_done():
            generator.generate_next_token()

            new_token = generator.get_next_tokens()[0]
            outputs += self.tokenizer_stream.decode(new_token)
        
        return outputs
