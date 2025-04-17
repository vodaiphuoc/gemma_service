from pydantic import BaseModel, Field
from typing import List
import json

from .extract import pdf2imgs
from PIL import Image
import os

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

class ModelResult(BaseModel):
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
    education: List[Education] = Field(description="Education of candidate in CV")
    experiences: List[Experience] = Field(description="List of experiences of the candidate in CV")
    personal_projects: List[str] = Field(default=[""], description="Some personal projects like hobbies that candidate done in free time")
    tech_stacks: List[str] = Field(
        description="Tech stacks or programming languages or skills that the candidate in overal", 
        examples=["Python, JavaScripts, Bootsrap","PostgresSQL"]
    )
    certifications: List[str] = Field(description="List of certifications that candidate has acquired")

def get_schema_output()->str:
    schema_dict  = ModelResult.model_json_schema(mode= "serialization")
    del schema_dict['type']
    schema_str = json.dumps(schema_dict, indent= 2)
    return schema_str

# Example
_PROMPT_EXAMPLE = ModelResult(
    name = "Michael Seymour",
    email= "example@cvmaker.uk",
    phone_number="+441214960508",
    education= [
            Education(
                university_name = "Imperial College London, UK",
                degree_type = "Master",
                major = "Computer Science",
                from_time="",
                to_time="2017",
                gpa=None
            ),
            Education(
                university_name = "University of Manchester, UK",
                degree_type = "Bachelor",
                major = "Computer Science",
                from_time="",
                to_time="2014",
                gpa=None
            )
        ],
    experiences= [
        Experience(
            company_name="EZ Tech Solution",
            job_position="Senior Software Enginner",
            from_time="2020",
            to_time="present",
            responsibilities=[
                """Lead a development team using React and Python. Participate in Agile methods, contributing to
sprint planning, backlog grooming, and sprint retrospectives. Collaborate with cross-functional
teams to design and implement scalable microservices architecture. Conduct code reviews and
mentor junior developers, fostering continuous learning and code quality improvement""",
                """Successfully led a cutting-edge web application, revamping user interface, resulting in a
remarkable 65% increase in user engagement and a boost in customer satisfaction""",
                """Led team to design and implement a scalable microservices architecture, seamlessly
integrating cross-functional teams and achieving an impressive 30% reduction in system
downtime."""
            ],
            technologies=[""],
            projects=[""],
            awards=[""]
        ),
        Experience(
            company_name="FC Software Solutions",
            job_position="Software Enginner",
            from_time="2018",
            to_time="2020",
            responsibilities=[
                """Developed and maintained backend systems for a cloud-based SaaS platform, prioritising system
stability and efficiency to deliver a high-performance user experience. Collaborated closely with
UI/UX designers to build responsive web applications, ensuring seamless user experiences across
various devices and screen sizes""",
                """Improved system performance by optimising backend systems, achieving 15% reduction in
response time, leading to a more responsive and satisfying user experience.""",
                """Successfully implemented unit tests and automated integration tests, resulting in 20% increase
in code coverage and a significant reduction in production defects.""",
                """Enhanced the continuous integration and deployment pipeline, enabling faster and more
reliable releases, ensuring quicker updates and improved platform stability."""
            ],
            technologies=[""],
            projects=[""],
            awards=[""]
        )
    ],
    tech_stacks=[
        "Web Technologies: HTML, CSS, JavaScript, React", 
        "Database: MySQL, MongoDB",
        "Version Control: Git",
        "Cloud Services: Amazon Web Services (AWS), Microsoft Azure",
        "Operating Systems: Windows, Linux, macOS",
        "Software Development Tools: IntelliJ, Eclipse, Visual Studio Code",
        "Programming Languages: Python, Java, C++"
    ],
    personal_projects=[""],
    certifications = [
        "AWS Certified Developer - Associate",
        "Certified Scrum Master (CSM), LearningLean"
    ]
).model_dump_json(indent=2)

EXAMPLE_CONTENTS = [{
            "type": "text",
            "text": "\n<examples>Below is example of image input and its output:\n**Example input image**:\n"
}]
EXAMPLE_CONTENTS.extend([{
        "type": "image",
        "image": Image.open(_img_path).convert("RGB")
    }
    for _img_path in pdf2imgs(pdf_path=os.path.join(
        os.path.dirname(__file__).replace("components","examples"), 
        "example.pdf"
    )
    )
])
EXAMPLE_CONTENTS.append({
            "type": "text",
            "text": f"\n**Desire example Output**:\n{_PROMPT_EXAMPLE}"
        })
