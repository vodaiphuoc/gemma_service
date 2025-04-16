from pydantic import BaseModel, Field
from typing import List
import json


class Education(BaseModel):
    university_name: str = Field(default="", description="Name of university in which the candidate has graduated")
    from_time: str = Field(default="", description="Start time attent university of candidate, can be year or month/year")
    to_time: str = Field(default="", description="End time attent university of candidate, can be year or month/year")
    gpa: float = Field(default=0.0, description="Final GPA")

class Experience(BaseModel):
    company_name: str = Field(description="Name of the company which the candidate has worked")
    position: str = Field(description="Position or title job of candidate in the company")
    from_time: str = Field(description="Start time join the company of candidate, can be year or month/year")
    to_time: str = Field(description="Left time of candidate from the company, can be year or month/year")
    responsibilites: List[str] = Field(description="List of activities or tasks the candidate has done in the job")
    technologies: List[str] = Field(description="Tech stacks that the candidate has used or learned at the time work in the company")
    projects: List[str] = Field(default=[""], description="Some projects or domains or system that the candidate has joined to work on")
    awards: List[str] = Field(default=[""], description="Some awards the candidate has received from manages of company")

class ModelResult(BaseModel):
    """
    Structure Output for information of candidate from Curriculum vitae
    """
    
    class Config:
        title = 'Model Result Output'

    email: str = Field(description="contact email of candidate")
    phone_number: int = Field(description= "contact phone number of candidate")
    education: Education = Field(description="Education of candidate in CV")
    experiences: List[Experience] = Field(description="List of experience of the candidate in CV")
    personal_projects: List[str] = Field(default=[""], description="Some personal projects like hobbies that candidate done in free time")
    total_skills: List[str] = Field(description="Tech stacks or programming languages or skills that the candidate in overal")

def get_schema_output()->str:
    schema_dict  = ModelResult.model_json_schema(mode= "serialization")
    del schema_dict['type']
    schema_str = json.dumps(schema_dict, indent= 2)
    return schema_str

