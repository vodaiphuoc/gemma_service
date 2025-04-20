from configparser import ConfigParser
from typing import Dict, Literal, List, Tuple, Union, Any
import psycopg2
from datetime import datetime, timedelta
from tqdm import tqdm
import random

class DB_Handling_Base(object):
    def __init__(self, 
                 config_file_path: str = "src/db.ini", 
                 section:str = "demo") -> None:
        self.config = self._get_DB_config(config_file_path = config_file_path, 
                                          section = section)

    def _get_DB_config(self, config_file_path:str, section:str)->Dict:
        parser = ConfigParser()
        parser.read(config_file_path)
        # get section, default to postgresql
        config = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                config[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, config_file_path))
        return config

    def _get_cursor_and_connection(self):
        try:
        # connecting to the PostgreSQL server
            conn = psycopg2.connect(**self.config)
        except (psycopg2.DatabaseError, Exception) as error:
            print(error)

        cur = conn.cursor()
        return conn, cur

class Query2MainDB(DB_Handling_Base):
    """For interacting with DB when training or inference"""
    def __init__(self, 
                 config_file_path: str = "src/db.ini", 
                 section: str = "local") -> None:
        super().__init__(config_file_path, section)
        self.jobpost_field_list = ["Job Title", "Job Description","Experience Required", 
                                    "Qualification Required", "Benefits",
                                    "Job Type", "CompanyName","City","Country"]
        
        self.resume_field_list = ["ApplyPosition", "Summary", "Achievements", 
                                    "Description","SkillDescription"]
        

    def _query_jobpost(self, 
                      jobpost_id:int,
                      )->Union[bool,str]:
        conn, cur = self._get_cursor_and_connection()
        
        # get jobpost information
        try:
            jobpost_query = """
                SELECT JP."JobTitle", JP."JobDescription",JP."ExperienceRequired", 
                        JP."QualificationRequired", JP."Benefits",
                        JT."Name", CPN."CompanyName",JL."City",JL."Country"
                FROM public."JobPosts" AS JP
                INNER JOIN public."JobTypes" as JT ON JP."JobTypeId" = JT."Id"
                INNER JOIN public."Companys" as CPN ON JP."CompanyId" = CPN."Id"
                INNER JOIN public."JobLocations" as JL ON JP."JobLocationId" = JL."Id"
                WHERE JP."Id" = '{}'
                """.format(jobpost_id)
            
            cur.execute(jobpost_query)
            jobpost_data = cur.fetchall()
            assert len(jobpost_data) == 1, f"Found length of {jobpost_data} = {len(jobpost_data)}"
        
        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't select for jobpost.Error: {error}")
            jobpost_data = None
        
        # get skill
        try:
            job_skill_query = """
                SELECT SKS."Name"
                FROM public."JobSkillSets" AS JSK
                INNER JOIN public."SkillSets" as SKS ON JSK."SkillSetId" = SKS."Id"
                WHERE JSK."JobPostId" = '{}'
                """.format(jobpost_id)
            cur.execute(job_skill_query)
            job_skill_data = cur.fetchall()
            str_job_skills = ",".join([skill[0] for skill in job_skill_data]) # flatten
        
        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't select for jobpost.Error: {error}")
            str_job_skills = None

        conn.commit()
        conn.close()
        cur.close()

        if jobpost_data is not None and str_job_skills is not None:
            job_post_dict = {}
            for ith, k in enumerate(self.jobpost_field_list):
                job_post_dict[k] = jobpost_data[0][ith]
            job_post_dict['Skills'] = str_job_skills

            # formating
            return '\n'.join([k+':\n'+v+'\n' for k, v in job_post_dict.items()])

        else:
            return False

    def _query_resume(self, 
                      user_id:int
                      )->Dict[str,str]:
        conn, cur = self._get_cursor_and_connection()

        # get other information
        try:
            resume_query = """
                SELECT PSA."ApplyPosition", PSA."Summary", PSA."Achievements", 
                        EDU."Description", SSK."SkillDescription"
                FROM public."Position_Summary_Achievements" AS PSA
                INNER JOIN public."TempEducationDetails" AS EDU ON PSA."UserId" = EDU."UserId"
                INNER JOIN public."SeekerSkillSets" AS SSK ON PSA."UserId" = SSK."UserId"
                WHERE PSA."UserId" = '{}'
                LIMIT 1
                """.format(user_id)
            
            cur.execute(resume_query)
            resume_data = cur.fetchall()
            assert len(resume_data) == 1, f"Found length {len(resume_data)}, UserId: {user_id}"
        
        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't select for resume. Error: {error}")
            resume_data = None

        # get experiments
        try:
            exp_query = """
                SELECT EXP."CompanyName", EXP."Position", EXP."Responsibilities"
                FROM public."Users" AS US
                INNER JOIN public."ExperienceDetails" AS EXP ON US."Id" = EXP."UserId"
                WHERE Us."Id" = '{}'
                """.format(user_id)
            
            cur.execute(exp_query)
            resume_exp = cur.fetchall()
            resume_exp = ",".join(["""CompanyName: {},\n
                                    Position: {},\n
                                    Responsibilities: {}\n
                                   """.format(each_[0].replace("\n",''),
                                              each_[1].replace("\n",''),
                                              each_[2].replace("\n",''))
                                   for each_ in resume_exp])
            resume_exp = " ".join([ele for ele in resume_exp.split(" ") if ele != ""])
        
        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't select for experience. Error: {error}")
            resume_exp = None

        conn.commit()
        conn.close()
        cur.close()

        if resume_data is not None and resume_exp is not None:
            resume_dict = {}
            for ith, k in enumerate(self.resume_field_list):
                resume_dict[k] = resume_data[0][ith]
            resume_dict['Experiences'] = resume_exp
            
            # formating
            return '\n'.join([k+':\n'+v+'\n' for k, v in resume_dict.items()])


        else:
            return False
    
    def query(self, jobpost_id:int, user_id: int)->Dict[str,str]:
        """Query a jobpost and a resume"""
        jobpost_data =  self._query_jobpost(jobpost_id= jobpost_id)
        resume_data = self._query_resume(user_id= user_id)

        return {'jobpost':jobpost_data,'resume':resume_data}
    

    def get_available_activity(self)->Union[bool, List[Dict[str,int]]]:
        conn, cur = self._get_cursor_and_connection()
        # get list available jobpost_id and user_id
        activity_query = """SELECT "Id", "UserId", "JobPostId" FROM public."JobPostActivitys" """
        try:
            cur.execute(activity_query)
            pair_id_list = cur.fetchall()
            pair_id_list = [{'Id': int(id[0]), 
                            'UserId':int(id[1]), 
                             'JobPostId': int(id[2])
                             } 
                             for id in pair_id_list
                             ]
            conn.commit()
            conn.close()
            cur.close()
            return pair_id_list
        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't select JobPostActivitys table in the database!", error)
            return False
        
    def update_score2table(self, update_data: List[Dict[str,Union[int,float]]]):
        conn, cur = self._get_cursor_and_connection()
        # get list available jobpost_id and user_id
        update_data = [(each_data_['Score'], each_data_['Id']) 
                       for each_data_ in update_data
                       ]
        
        update_query = """UPDATE public."JobPostActivitys" SET "Score" = %s WHERE "Id" = %s"""
        try:
            cur.executemany(update_query,update_data)
            conn.commit()
            conn.close()
            cur.close()
            return True
            
        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't update JobPostActivitys's score column in the database!", error)
            return False

class InsertDEMO2MainDB(DB_Handling_Base):
    def __init__(self,
                 config_file_path: str = "src/db.ini", 
                 section: str = "local"
                 ) -> None:
        super().__init__(config_file_path, section)

    # related to jobposts
    def insertBussinessStream(self, input_data: List[str])->None:
        """
        Insert many into 'BusinessStreams' table
        Arg:
            - input_data: List of Tuple of str
        Exmaple: [BusinessStreamName, ...]
        """
        conn, cur = self._get_cursor_and_connection()
        try:
            query = f'INSERT INTO public."BusinessStreams" \
                ("BusinessStreamName", "Description", "IsDeleted") \
                    VALUES (%s, %s, %s);'
            input_data = tuple([(data,"empty","false") for data in input_data])
            cur.executemany(query, input_data)
        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't insert many into BusinessStreams table\
                   in the database!.Error: {error}")
        
        conn.commit()
        conn.close()
        cur.close()
        print("Done insertBussinessStream")
        return None

    def insertCompanys(self, input_data: List[Dict[str,Any]])->None:
        """
        Insert many into 'Companys' table
        Arg:
            - input_data: List of Dict with key is str, value is Any dtype
        Exmaple: [{'Industry':...,'Company Name':...}, ...]
        """
        conn, cur = self._get_cursor_and_connection()
        try:
            for data in input_data:
                for k,v in data.items():
                    if isinstance(v,str):
                        if "'" in v:
                            data[k] = v.replace("'","''")
                query = """INSERT INTO public."Companys" ("CompanyName", "CompanyDescription", 
                                                            "WebsiteURL", "EstablishedYear", 
                                                            "Country", "City", 
                                                            "Address", "NumberOfEmployees",
                                                            "BusinessStreamId", "IsDeleted")
                        VALUES ('{}', 'empty','{}', 2010,'{}','{}', 'empty', '{}',
                                (SELECT "Id" FROM public."BusinessStreams" 
                                WHERE public."BusinessStreams"."BusinessStreamName" = '{}'
                                LIMIT 1)
                                ,'f');""".format(data["company_name"], data["Website"],
                                        data["State"],data["City"],
                                        data["Company Size"],data["Industry"])

                cur.execute(query)
        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't insert many into Companys table in the database! Error: ",error)
        
        conn.commit()
        conn.close()
        cur.close()
        print("Done insertCompanys")
        return None


    def insertJobLocation(self, input_data: List[Dict[str, Any]])->None:
        """
        Insert many into 'JobLocation' table
        Arg:
            - input_data: List of Tuple of str
        Exmaple: [{'location':..., 'Country':...}, ...]
        Note: location means city
        """
        conn, cur = self._get_cursor_and_connection()

        try:
            input_data = [("empty", data["location"], "empty", "empty", data["Country"], "empty", "f") 
                          for data in input_data]
            query = f'INSERT INTO public."JobLocations" ("District", "City", \
                                                        "PostCode", "State", \
                                                        "Country", "StressAddress",\
                                                        "IsDeleted") \
                    VALUES (%s, %s, %s, %s,%s, %s, %s);'
            cur.executemany(query, input_data)
        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't insert many into JobLocations table in the database!", error)
        
        conn.commit()
        conn.close()
        cur.close()
        print("Done insertJobLocation")
        return None

    def insertJobTypes(self)->None:
        """
        Insert many into 'JobTypes' table (parent table)
        Possible for JobType is: 'Intern', 'Temporary', 'Full-Time', 
        'Contract', 'Part-Time'
        """
        conn, cur = self._get_cursor_and_connection()

        input_data = [('Intern','This position is mainly for undergraduate or recently graduate student',), 
                      ('Temporary','Only work for a short and determined period of time',),
                      ('Full-Time','This position work mainly 8 hours a day and 40 hours per week',), 
                      ('Contract','There is a contract between jobseeker and the company', ), 
                      ('Part-Time','Worker can work with 4-hour shift and many shifts in a week',)
                      ]
        
        try:
            query = f'INSERT INTO public."JobTypes" ("Name", "Description") VALUES (%s, %s);'
            cur.executemany(query, input_data)
        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't insert many into JobTypes table in the database!", error)
        
        conn.commit()
        conn.close()
        cur.close()
        print("Done insertJobTypes")
        return None

    def insertSkillSets(self, input_data: List[str])->None:
        """
        Insert many into 'SkillSets' table (parent table)
        Arg:
            - input_data: List of Tuple of str
        Exmaple: [(skill_1), (skill_2), ...]
        """
        conn, cur = self._get_cursor_and_connection()
        try:
            input_data = [(data,data,"empty","f") for data in input_data]
            query = f'INSERT INTO public."SkillSets" ("Name", "Shorthand", \
                                                    "Description", "IsDeleted") \
                        VALUES (%s,%s,%s,%s);'
            cur.executemany(query, input_data)
        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't insert many into SkillSets table in the database!", error)
        
        conn.commit()
        conn.close()
        cur.close()
        print("Done insertSkillSets")
        return None

    def insertJobPosts(self, input_data: List[Dict[str,Any]])->None:
        """
        Insert many into 'JobPosts' table (child table)
        Arg:
            - input_data: List of Tuple of str
        Exmaple: [{'JobTitle':..., 'JobDescription':..., 'Salary':..., 'PostingDate':..., 
                    'ExperienceRequired':..., 'QualificationRequired':..., 'Benefits'...,  
                    }, 
                  (JobTitle_2,..,), 
                  ...
                  ]
        """
        conn, cur = self._get_cursor_and_connection()
        
        # prepare Ids state
        for data in input_data:
            for k,v in data.items():
                if isinstance(v,str):
                    if "'" in v:
                        data[k] = v.replace("'","''")

        
        for data in input_data:
            try:
                # insert state
                insert_query = """INSERT INTO public."JobPosts" ("JobTitle", "JobDescription", 
                                                            "Salary", "PostingDate", "ExpiryDate",
                                                            "ExperienceRequired", "QualificationRequired", 
                                                            "SkillLevelRequired", "Benefits", "IsActive",
                                                            "JobTypeId", "CompanyId", "JobLocationId",
                                                            "IsDeleted")
                        VALUES ('{}','{}','{}', '{}','{}','{}','{}', 3,'{}','t',
                                (SELECT "Id" FROM public."JobTypes" AS JT
                                WHERE JT."Name" = '{}'),
                                (SELECT "Id" FROM public."Companys" AS CO
                                WHERE CO."CompanyName" = '{}'),
                                (SELECT "Id" FROM public."JobLocations" AS JL
                                WHERE JL."City" = '{}'
                                AND JL."Country" = '{}'
                                ),'f');
                                """.format(data["Job Title"], data["Job Description"],
                                        data["Salary Range"],
                                        datetime.strptime(data["Job Posting Date"], "%Y-%m-%d"),
                                        datetime.now() + timedelta(days= 45),
                                        data["Experience"],data["Qualifications"], data["Benefits"],
                                        data["Work Type"], 
                                        data["Company"], 
                                        data["location"],data["Country"]
                                        )

                cur.execute(insert_query)
            except (psycopg2.DatabaseError, Exception) as error:
                print(f"Can't insert many into JobPosts table in the database! Error: ",error)
                break
            
        conn.commit()
        conn.close()
        cur.close()
        print("Done insertJobPosts")
        return None

        

    def insertJobSkillSet(self, input_data: List[Tuple[str]]):
        """
        Insert many into 'JobSkillSets' table
        Arg:
            - input_data: List of Tuple of str
        Exmaple: [(JobPostId_1,SkillSetId_1), (JobPostId_2,SkillSetId_2), ...]
        """
        conn, cur = self._get_cursor_and_connection()
        for data in tqdm(input_data, total=len(input_data)):
            try:
                query = """INSERT INTO public."JobSkillSets" ("JobPostId", "SkillSetId","IsDeleted") \
                            VALUES (
                            (SELECT "Id" FROM public."JobPosts" 
                            WHERE  public."JobPosts"."Id" = '{}'),
                            (SELECT "Id" FROM public."SkillSets" 
                            WHERE  public."SkillSets"."Id" = '{}'),
                            'f');""".format(data["JobPostId"], data["SkillSetId"])
                cur.execute(query)
            except (psycopg2.DatabaseError, Exception) as error:
                print(f"Can't insert many into JobSkillSets table in the database!", error)
                break
        
        conn.commit()
        conn.close()
        cur.close()
        print("Done insertJobSkillSet")
        return None


    # related to Resume
    def insertUsers(self, input_data: List[str]):
        """
        Role value is equal 2 for who post CV
        """
        conn, cur = self._get_cursor_and_connection()

        try:
            input_data = [(name,2,"f") for name in input_data]
            query = 'INSERT INTO public."Users" ("UserName","Role","IsDeleted") VALUES (%s,%s,%s);'
            cur.executemany(query, input_data)
            conn.commit()
            conn.close()
            cur.close()
            print("Done insertUsers")

        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't insert many into Users table in the database!", error)
        return None


    def insertEducationDetail(self,input_data: List[Dict[str, Any]]):
        """For demo only, will use TempEducationDetails table"""
        conn, cur = self._get_cursor_and_connection()
        for data in input_data:
            try:
                query = """INSERT INTO public."TempEducationDetails" ("Description","UserId","IsDeleted") 
                            VALUES (
                            ('{}'),
                            (SELECT "Id" FROM public."Users"
                            WHERE public."Users"."Id" = '{}'),
                            'f');""".format(data["Description"].replace("'","''") 
                                            if isinstance(data["Description"],str) 
                                            else data["Description"]
                                            ,data["UserId"])
                cur.execute(query)

            except (psycopg2.DatabaseError, Exception) as error:
                print(f"Can't insert many into TempEducationDetails table in the database!", error)
                break
        
        conn.commit()
        conn.close()
        cur.close()
        print("Done insertEducationDetail")
        return None

    def insertExperienceDetail(self,input_data: List[Dict[str, Any]]):
        conn, cur = self._get_cursor_and_connection()

        for data in input_data:
            for k,v in data.items():
                if isinstance(v,str):
                    if "'" in v:
                        data[k] = v.replace("'","''")

        for data in input_data:
            try:
                query = """INSERT INTO public."ExperienceDetails" ("CompanyName","Position",
                                                                    "StartDate","EndDate", 
                                                                    "Responsibilities", "Achievements",
                                                                    "UserId","IsDeleted")
                                        VALUES ('{}','{}','{}','{}','{}','{}',
                                        (SELECT "Id" FROM public."Users"
                                        WHERE public."Users"."Id" = '{}'),
                                        'f');""".format(data["CompanyName"], data["Position"],
                                                          data["StartDate"], data["EndDate"],
                                                          data["Responsibilities"], data["Achievements"],
                                                          data["UserId"]
                                                          )
                cur.execute(query)

            except (psycopg2.DatabaseError, Exception) as error:
                print(f"Can't insert many into ExperienceDetails table in the database!", error)
                break
        
        conn.commit()
        conn.close()
        cur.close()
        print("Done insertExperienceDetail")
        return None


    def insertSeekerSkillSet(self, input_data: List[Dict[str, Any]]):
        conn, cur = self._get_cursor_and_connection()

        for data in input_data:
            for k,v in data.items():
                if isinstance(v,str):
                    if "'" in v:
                        data[k] = v.replace("'","''")

        for data in input_data:
            try:
                query = """INSERT INTO public."SeekerSkillSets" ("ProficiencyLevel","UserId",
                                                                    "SkillDescription","IsDeleted")
                                        VALUES (1,
                                        (SELECT "Id" FROM public."Users"
                                        WHERE public."Users"."Id" = '{}'),
                                        '{}',
                                        'f');""".format(data["UserId"], 
                                                        data["SkillDescription"]
                                                        )
                cur.execute(query)
                
            except (psycopg2.DatabaseError, Exception) as error:
                print(f"Can't insert many into SeekerSkillSets table in the database!", error)
                break

        conn.commit()
        conn.close()
        cur.close()
        print("Done SeekerSkillSets")
        return None
    
    def insertPositionSummaryAchievements(self, input_data:List[Dict[str,Any]]):
        conn, cur = self._get_cursor_and_connection()

        for data in input_data:
            for k,v in data.items():
                if isinstance(v,str):
                    if "'" in v:
                        data[k] = v.replace("'","''")

        for data in input_data:
            try:
                query = """INSERT INTO public."Position_Summary_Achievements" ("ApplyPosition","Summary",
                                                                                "Achievements", "UserId", 
                                                                                "IsDeleted") 
                                        VALUES ('{}','{}','{}',
                                        (SELECT "Id" FROM public."Users"
                                        WHERE public."Users"."Id" = '{}'),
                                        'f');""".format(data["ApplyPosition"],data["Summary"],
                                                        data["Achievements"], data["UserId"])
                cur.execute(query)
                
            except (psycopg2.DatabaseError, Exception) as error:
                print(f"Can't insert many into Position_Summary_Achievements table \
                      in the database!", error)
                break
            
        conn.commit()
        conn.close()
        cur.close()
        print("Done insertPositionSummaryAchievements")
        return None

    def _get_Post_User(self, 
                       post_return_ratio:float = 0.3, 
                       user_return_ratio: float = 1.0
                       )->Tuple[List[int]]:
        conn, cur = self._get_cursor_and_connection()
        # get list available jobpost_id and user_id
        ini_query = """SELECT "Id" FROM public."{}" """

        ID_dict = {}
        for tabel_name in ["JobPosts", "Users"]:
            try:
                cur.execute(ini_query.format(tabel_name))
                id_list = cur.fetchall()
                ID_dict[tabel_name] = [id[0] for id in id_list]

            except (psycopg2.DatabaseError, Exception) as error:
                print(f"Can't select {tabel_name} table in the database!", error)
                break
        conn.commit()
        conn.close()
        cur.close()

        jobpost_ids = random.sample(ID_dict['JobPosts'], 
                                    k= int(len(ID_dict['JobPosts'])*post_return_ratio))
        
        user_ids = random.sample(ID_dict['Users'], 
                                k= int(len(ID_dict['Users'])*user_return_ratio))

        return jobpost_ids, user_ids


    def insertJobPostActivitys(self, num_connections: int = 100):
        """
        Simulate the number conneciton between jobposts and users
        with 'num_connections'
        """
        jobpost_ids, user_ids = self._get_Post_User()

        user_post = [(datetime.now() + timedelta(days= 45),
                      3,
                      random.choice(user_ids), 
                      random.choice(jobpost_ids),
                      'f') 
                    for _ in range(num_connections)
        ]

        # insert
        conn, cur = self._get_cursor_and_connection()
        try:
            query = """INSERT INTO public."JobPostActivitys" ("ApplicationDate","Status",
                                                                            "UserId", "JobPostId",
                                                                            "IsDeleted")
                                    VALUES (%s,%s,%s,%s,%s);"""
            cur.executemany(query, user_post)
            conn.commit()
            conn.close()
            cur.close()
            print("Done insertJobPostActivitys")

        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Can't insert many into Position_Summary_Achievements table in the database!", error)
        return None