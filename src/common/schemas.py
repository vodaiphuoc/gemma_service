from pydantic import BaseModel, Field, create_model
from typing import List, Literal
import json

class Education(BaseModel):
    r"""
    Represent education information of the candidate
    """
    university_name: str = Field(
        default="", 
        description="Name of university/school/college in which the candidate has graduated"
        )
    degree_type: str = Field(default="",description="Type of degree, it can be bachelor, master, PhD, etc...")
    major :str = Field(default="", description="Main major when studying in this university")
    from_time: str = Field(default="", description="Start time attent university of candidate, can be year or month/year")
    to_time: str = Field(default="", description="End time attent university of candidate, can be year or month/year")
    gpa: float|None = Field(default=None, description="Final GPA")

class Experience(BaseModel):
    r"""
    Represent of working experience in a company or specifiec role/job title
    """
    company_name: str = Field(description="Name of the company which the candidate has worked")
    job_position: str = Field(
        description="Position or title job or role of candidate in the company", 
        examples=["freelancer","web developer","software engineer"]
    )
    from_time: str = Field(description="Start time join the company of candidate, can be year or month/year")
    to_time: str = Field(description="Left time of candidate from the company, can be year or month/year")
    responsibilities: List[str] = Field(description="List of activities or tasks the candidate has done in the job")
    technologies: List[str] = Field(
        description="Tech stacks that the candidate has used or learned at the time work in the company",
        examples=["MongoDB","RabbitMQ", "RESTfullAPI","Java"])
    projects: List[str] = Field(default=[""], description="Some projects or domains or system that the candidate has joined to work on")
    awards: List[str] = Field(default=[""], description="Some awards the candidate has received from manages of company")

class ExtractModelResult(BaseModel):
    """
    Structure Output for information of candidate from Curriculum vitae
    """
    
    class Config:
        title = 'Result Output'

    name: str = Field(description="Full name of the candidate")
    email: str = Field(
        description="contact email of candidate",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["mywork@gmail.com"]
        )
    phone_number: str = Field(
        description= "contact phone number of candidate", 
        pattern=r"^\+?\(?\d{2,4}\)?[\s.-]?\d{2,4}[\s.-]?\d{2,4}$",
        examples=['(555) 123 4567','555-123-4567','555.123.4567']
    )
    education: List[Education] = Field(description="List of education information of candidate in CV")
    experiences: List[Experience] = Field(description="List of experiences of the candidate in CV")
    personal_projects: List[str] = Field(default=[""], description="Some personal projects like hobbies that candidate done in free time")
    tech_stacks: List[str] = Field(
        description="Tech stacks or programming languages or skills that the candidate in overal", 
        examples=["Python, JavaScripts, Bootsrap","PostgresSQL"]
    )
    certifications: List[str] = Field(description="List of certifications that candidate has acquired")

def get_schema_output()->str:
    schema_dict  = ExtractModelResult.model_json_schema(mode= "serialization")
    del schema_dict['type']
    schema_str = json.dumps(schema_dict, indent= 2)
    return schema_str


class JobDescriptions(BaseModel):
    job_title: str
    working_location: str
    job_overview: str
    require_experience_years: int
    level: str
    working_mode: Literal['hybrid','onsite','remote']
    contract_types: Literal['fulltime','parttime','freelancer']
    responsibilities: List[str] = Field(description="Responsibilities of job")
    require_skills: List[str]
    preferred_skills: List[str]



_Float_Field = {"job_overview", "responsibilities", "require_skills", "preferred_skills"}

new_properties = {}
for k,v in JobDescriptions.model_json_schema()['properties'].items():
    _new_description = f'Ranking score for `{k}`'
    if (_old_description := v.get('description')) is not None:
        _new_description +=  f'where {k} is {_old_description}'

    _new_field = Field(
        title = v['title'],
        description = _new_description
    )
    new_properties[k] = (bool, _new_field) if k in _Float_Field else (float, _new_field)


JobDescriptionsScoreOutput = create_model("JobDescriptionsScoreOutput", **new_properties)
