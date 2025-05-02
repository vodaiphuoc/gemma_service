from .tables import (
    CandidateEducation,
    CandidateResponsibility,
    CandidateProject,
    CandidateAward,
    CandidateExperience,
    CandidateTechStack,
    CandidateCertification,
    CandidateCV,

    UploadedCVs,
    ApplyTransaction,
    CandidateProfile,
    JobDescriptionsResponsibility,
    JobDescriptionsRequireSkill,
    JobDescriptionsPreferrSkill,
    JobDescriptions,
    HRProfile,
)    

from ..schemas import StructedCVOutput

from pydantic import BaseModel
import sqlmodel
import uuid
from typing import Union, Literal

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class ExtractAgentDB_Client(object):
    def __init__(self,
        user: str,
        pwd: str,
        host:str,
        port: int
        )->None:
        # DATABASE_URL = f"postgresql://{user}:{pwd}@{host}:{port}/postgres"
        
        DATABASE_URL = f"sqlite:///dummy.db"

        self.engine = sqlmodel.create_engine(DATABASE_URL, echo=False)
        sqlmodel.SQLModel.metadata.create_all(
            bind = self.engine, 
            tables = [
                CandidateEducation,
                CandidateResponsibility,
                CandidateProject,
                CandidateAward,
                CandidateExperience,
                CandidateTechStack,
                CandidateCertification,
                CandidateCV
        ])

    def insertCV(self, structed_model: BaseModel, user_id: uuid.UUID)->None:
        r"""
        This method called by agent (extract_service)
        Get ORMs from `StructedCVOutput`
        """
        assert isinstance(structed_model, StructedCVOutput)
        
        with sqlmodel.Session(self.engine) as session:
            logger.info('inside session')

            try:
                cv_orm = CandidateCV(
                    user_id = user_id,
                    name=structed_model.name,
                    email=structed_model.email, 
                    phone_number=structed_model.phone_number
                )
                session.add(cv_orm)
                session.commit()

                for _education in structed_model.educations:
                    session.add(
                        CandidateEducation(
                            cv_id = cv_orm.id,
                            **_education.model_dump()
                    ))
                session.commit()
                
                for _techstack in structed_model.techstacks:
                    session.add(
                        CandidateTechStack(
                            cv_id=cv_orm.id,
                            **_techstack.model_dump()
                    ))
                session.commit()

                for _cert in structed_model.certificates:
                    session.add(
                        CandidateCertification(
                            cv_id= cv_orm.id,
                            **_cert.model_dump()
                    ))
                session.commit()


                for _exp in structed_model.experiences:
                    exp_orm = CandidateExperience(
                        cv_id=cv_orm.id,
                        company_name = _exp.company_name,
                        job_position = _exp.job_position,
                        from_time = _exp.from_time,
                        to_time = _exp.to_time,
                        technologies = _exp.technologies
                    )
                    session.add(exp_orm)
                    session.commit()


                    for _respblt in _exp.responsibilities:
                        session.add(
                            CandidateResponsibility(
                                exp_id=exp_orm.id, 
                                value= _respblt.value
                        ))
                    session.commit()

                    for _project in _exp.projects:
                        session.add(
                            CandidateProject(
                                exp_id=exp_orm.id, 
                                project_description= _project.project_description
                        ))
                    session.commit()

                    for _award in _exp.awards:
                        session.add(
                            CandidateAward(
                                exp_id=exp_orm.id, 
                                award_description= _award.award_description
                        ))
                    session.commit()

            except Exception as e:
                logger.error('got error: {}'.format(e))
                session.rollback()

    def getCV(self, id: uuid.UUID, user_id: uuid.UUID)->Union[CandidateCV, None]:
        r"""
        This method called by agent (ranking_service)
        """
        logger.info('runing getCV')
        
        with sqlmodel.Session(self.engine) as session:
            try:
                statement = sqlmodel.select(CandidateCV).where(CandidateCV.id == id, CandidateCV.user_id == user_id)
                results = session.exec(statement).all()
                assert len(results)> 1
                return results
            
            except Exception as e:
                logger.error('got error: {}'.format(e))
                session.rollback()
                return None

class AppDB_Client(object):
    def __init__(self,
        user: str,
        pwd: str,
        host:str,
        port: int
        )->None:

        # DATABASE_URL = f"postgresql://{user}:{pwd}@{host}:{port}/postgres"
        
        DATABASE_URL = f"sqlite:///dummy.db"

        self.engine = sqlmodel.create_engine(DATABASE_URL, echo=False)
        sqlmodel.SQLModel.metadata.create_all(
            bind = self.engine, 
            tables = [
                UploadedCVs,
                ApplyTransaction,
                CandidateProfile,
                JobDescriptionsResponsibility,
                JobDescriptionsRequireSkill,
                JobDescriptionsPreferrSkill,
                JobDescriptions,
                HRProfile
        ])

    def insertProfile(
            self, 
            user_type: Literal['candidate','HR'], 
            **kwargs
        )->Union[uuid.UUID, None]:
        r"""
        Create profile for `CandidateProfile` or `HRProfile`.
        Args:
            user_type (Literal['candidate','HR']): type of profile to create
            kwargs: 
                arguments for create `CandidateProfile` or `HRProfile`.

                support kwargs:
                    - kwargs for CandidateProfile:
                        - name (str): user name
                        - email (str): user email
                        - phone_number (str): phone number

                    - kwargs for HRProfile:
                        - name (str)
                        - work_email (str)
                        - phone_number (str): phone number
                        - company_name (str)
                        - company_description (str)
                        - location (str)
        Returns:
            candidate_id or hr_id if success, else None
        """
        with sqlmodel.Session(self.engine) as session:
            logger.info('inside session')
            try:
                profile_orm = CandidateProfile(**kwargs) if user_type == "candidate" else HRProfile(**kwargs)
                session.add(profile_orm)
                session.commit()
                return profile_orm.id

            except Exception as e:
                session.rollback()
                return None

    # def insertJD(self, hr_id: uuid.UUID):
    #     r"""
    #     Insert a Job description by a HR
    #     """
    #     with sqlmodel.Session(self.engine) as session:
    #         logger.info('inside session')
    #         try:
    #             profile_orm = CandidateProfile(**kwargs) if user_type == "candidate" else HRProfile(**kwargs)
    #             session.add(profile_orm)
    #             session.commit()
    #             return profile_orm.id

    #         except Exception as e:
    #             session.rollback()
    #             return None




    #         class JobDescriptions(SQLModel, table = True):
    # id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="primary_key", index= True)
    # hr_id: uuid.UUID = Field(default=None, foreign_key = "hrprofile.id", description="foreign_key")

    # job_title: str
    # working_location: str
    # job_overview: str
    # require_experience_years: int
    # level: str
    # working_mode: WORKING_MODE_TYPE
    # contract_types: CONTRACT_TYPE
    # secret_bias: str



    # def insertTransaction(self):

    
    


    