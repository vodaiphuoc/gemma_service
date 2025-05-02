from typing import List, Optional
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship
import uuid


######################### TABLES FOR AGENT DATABASE #########################
### Allow to use Relationship (lazy loading)
class CandidateEducation(SQLModel, table = True):
    r"""
    Represent education information of the candidate
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key")
    cv_id: uuid.UUID = Field(default=None, foreign_key = "candidatecv.id", description="foreign_key")

    university_name: str = Field(
        default="", 
        description="Name of university/school/college in which the candidate has graduated"
        )
    degree_type: str = Field(default="",description="Type of degree, it can be bachelor, master, PhD, etc...")
    major: str = Field(default="", description="Main major when studying in this university")
    from_time: str = Field(default="", description="Start time attent university of candidate, can be year or month/year")
    to_time: str = Field(default="", description="End time attent university of candidate, can be year or month/year")
    gpa: float = Field(default=0.0, description="Final GPA")

    candidate_cv: "CandidateCV" = Relationship(back_populates="educations")

class CandidateResponsibility(SQLModel, table = True):
    r"""Responsibilities of a job inside a company at a position"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key")
    exp_id: uuid.UUID = Field(default=None, foreign_key = "candidateexperience.id", description="foreign_key")
    value: str

    exp_responsblt: "CandidateExperience" = Relationship(back_populates="responsibilities")

class CandidateProject(SQLModel, table = True):
    r"""Big/Significant Project that candidate has performed in the company"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key")
    exp_id: uuid.UUID = Field(default=None, foreign_key = "candidateexperience.id", description="foreign_key")
    
    project_description: str

    exp_project: "CandidateExperience" = Relationship(back_populates="projects")

class CandidateAward(SQLModel, table = True):
    r"""Award of the candidate has received from managers of company"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key")
    exp_id: uuid.UUID = Field(default=None, foreign_key = "candidateexperience.id", description="foreign_key")
    
    award_description: str

    exp_award: "CandidateExperience" = Relationship(back_populates="awards")

class CandidateExperience(SQLModel, table = True):
    r"""
    Represent of working experience in a company or specifiec role/job title
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key")
    cv_id: uuid.UUID = Field(default=None, foreign_key = "candidatecv.id", description="foreign_key")

    company_name: str = Field(description="Name of the company which the candidate has worked")
    job_position: str = Field(
        description="Position or title job or role of candidate in the company, examples: freelancer, web developer, software engineer"
    )
    from_time: str = Field(description="Start time join the company of candidate, can be year or month/year")
    to_time: str = Field(description="Left time of candidate from the company, can be year or month/year")
    technologies: str = Field(
        description="""Tech stacks that the candidate has used or learned at the time work in the company, 
        examples= MongoDB, NodeJS , RabbitMQ, FastAPI, RESTfullAPI, gPRC, Java, SpringBoot"""
        )
    
    responsibilities: List[CandidateResponsibility] = Relationship(back_populates="exp_responsblt")
    projects: List[CandidateProject] = Relationship(back_populates="exp_project")
    awards: List[CandidateAward] = Relationship(back_populates="exp_award")

    candidate_exp: "CandidateCV" = Relationship(back_populates="experiences")
    
class CandidateTechStack(SQLModel, table = True):
    r"""
    Tech stacks or programming languages or skills that the candidate in overal
    Examples:
        Python, JavaScripts, Bootsrap, PostgresSQL
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key")
    cv_id: uuid.UUID = Field(default=None, foreign_key = "candidatecv.id", description="foreign_key")

    technology_name:str

    candidate_techstack: "CandidateCV" = Relationship(back_populates="techstacks")

class CandidateCertification(SQLModel, table = True):
    r"""
    A certification about technology, education, englis, etc.. that candidate has acquired
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key")
    cv_id: uuid.UUID = Field(default=None, foreign_key = "candidatecv.id", description="foreign_key")

    certificate_description:str

    candidate_certificate: "CandidateCV" = Relationship(back_populates="certificates")

class CandidateCV(SQLModel, table = True):
    """
    Structure Output for information of candidate from Curriculum vitae
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key", index= True)

    user_id: uuid.UUID = Field(description="foreign_key")
    name: str = Field(description="Full name of the candidate")
    email: str = Field(description="contact email of candidate, examples='mywork@gmail.com'")
    phone_number: str = Field(description= "contact phone number of candidate, examples=['(555) 123 4567','555-123-4567','555.123.4567']")
    
    educations: List[CandidateEducation] = Relationship(back_populates="candidate_cv")
    techstacks: List[CandidateTechStack] = Relationship(back_populates="candidate_techstack")
    certificates: List[CandidateCertification] = Relationship(back_populates="candidate_certificate")
    experiences: List[CandidateExperience] = Relationship(back_populates="candidate_exp")

######################### TABLES FOR APP DATABASE #########################
### Dont user Relationship for this database, use only select + join
### USER TABLES 
class UploadedCVs(SQLModel, table = True):
    r"""
    List of uploaded CV from object storage
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key", index= True)

    created_data: str = Field(description="Date time of upload file")
    bucket_name: str = Field(description="Bucket name of upload file")
    blob_name: str = Field(description="Specific blob name upload file")

class ApplyTransaction(SQLModel, table = True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key", index= True)

    jobdescription_id: uuid.UUID = Field(foreign_key = "jobdescriptions.id", description="foreign_key")
    candidate_id: uuid.UUID = Field(foreign_key = "candidateprofile.id", description="foreign_key")
    candidate_cv_id: uuid.UUID = Field(foreign_key = "uploadedcvs.id", description="foreign_key")

class CandidateProfile(SQLModel, table = True):
    r"""
    Candidate Personal Profile.

    Columns:
        - id (uuid.UUID): primary key 
        - name (str): user name
        - email (str): user email
        - phone_number (str): phone number
        
    Relationship:
        - apply_history (List[ApplyTransaction]): apply history of the user
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key", index= True)

    name: str = Field(description="Full name of the candidate")
    email: str = Field(description="contact email of candidate, examples='mywork@gmail.com'")
    phone_number: str = Field(description= "contact phone number of candidate, examples=['(555) 123 4567','555-123-4567','555.123.4567']")
    location: str = Field(description= "Current location")
    password: str = Field(description= "Account password")

### HR TABLES 
class WORKING_MODE_TYPE(Enum):
    hybrid = "hybrid"
    onsite = "onsite"
    remote = "remote"

class CONTRACT_TYPE(Enum):
    fulltime = "fulltime"
    parttime = "parttime"
    freelancer = "freelancer"

class JobDescriptionsResponsibility(SQLModel, table = True):
    r"""Responsibilities of the job in JD post"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key", index= True)
    jd_id: uuid.UUID = Field(default=None, foreign_key = "jobdescriptions.id", description="foreign_key")
    
    reponsibility_description: str

class JobDescriptionsRequireSkill(SQLModel, table = True):
    r"""A single required skill description of a job"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key", index= True)
    jd_id: uuid.UUID = Field(default=None, foreign_key = "jobdescriptions.id", description="foreign_key")
    
    skill_description: str

class JobDescriptionsPreferrSkill(SQLModel, table = True):
    r"""A single preferred skill that company want candidates must have"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key", index= True)
    jd_id: uuid.UUID = Field(default=None, foreign_key = "jobdescriptions.id", description="foreign_key")
    
    skill_description: str

class JobDescriptions(SQLModel, table = True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key", index= True)
    hr_id: uuid.UUID = Field(default=None, foreign_key = "hrprofile.id", description="foreign_key")

    job_title: str
    working_location: str
    job_overview: str
    require_experience_years: int
    level: str
    working_mode: WORKING_MODE_TYPE
    contract_types: CONTRACT_TYPE
    secret_bias: str

class HRProfile(SQLModel, table = True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key", index= True)

    name: str
    work_email:str
    phone_number: str = Field(description= "contact phone number of candidate, examples=['(555) 123 4567','555-123-4567','555.123.4567']")
    company_name: str
    company_description:str
    location: str
    password: str