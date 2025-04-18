from google import genai
from google.genai import types
from pydantic import ValidationError
from common.schemas import ExtractModelResult, JobDescriptions, JobDescriptionsScoreOutput


PROMPT_TEMPLATE = """

**structed data of a candidate**
{{extracted_results}}

**structed data of job description**
{{jd}}

**`secret` bias**
{{secret_bias}}

**Task description and Rules**
- You are given a structed data of a candidate, structed data of job description and a `secret` bias
of a HR magager, do below tasks step-by-ste
- First, look though each requirement field in structed JD and analysize how well data of candidate is satisfied this 
requirement
- Second, for each analysise in First step, ranking score output of for each reuirement field in scaled of 10
- Third, if a requirement field exist in `secret` bias, the ranking score of this field must be plus 2 from
score in Second step.
"""

class RankingModel(object):
    def __init__(self, api_key: int):
        self._client = genai.Client(api_key=api_key)

    def forward(
            self, 
            extracted_results: ExtractModelResult, 
            jd: JobDescriptions,
            secret_bias: str
        )->str:
        r"""
        Perform ranking score given candidate profiles, JD and secret bias of HR
        Args:
            extracted_results (ExtractModelResult): a structed data of candidate
            jd (JobDescriptions): a structed JD from HR
            secret_bias (str): a secret message of HR in which factors are more
            preferred
        """
        
        response = self._client.models.generate_content(
            # model = 'gemini-1.5-flash',
            model = 'gemini-2.5-pro-exp-03-25',
            config = types.GenerateContentConfig(
                system_instruction = "You are a professtional HR manager for evaluating and ranking new candidate",
                max_output_tokens = 3000,
                temperature = 0.1,
                response_mime_type = 'application/json',
                response_schema = JobDescriptionsScoreOutput,
            ),
            contents = types.Content(
                role='user',
                parts=[
                    types.Part.from_text(
                        text=PROMPT_TEMPLATE.format(
                            extracted_results = extracted_results,
                            jd = jd,
                            secret_bias = secret_bias
                        )
                    )
                ]
            ),
        )
        # post processing
        response_text = response.text.replace("```.json", "").replace("```","")
        try:
            return {
                "status": True,
                "msg": "",
                "result": JobDescriptionsScoreOutput.model_validate_json(response_text)
            }
        
        except ValidationError as e:
            return {
                "status": False,
                "msg": e,
                "result": None
            }
