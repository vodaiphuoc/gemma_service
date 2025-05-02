from pydantic import Field, create_model
import sqlmodel
from typing import Dict, Type, Tuple, Any, List
import json

from common.orm.tables import (
    CandidateEducation,
    CandidateResponsibility,
    CandidateProject,
    CandidateAward,
    CandidateExperience,
    CandidateTechStack,
    CandidateCertification,
    CandidateCV
)

TYPE_CONVERSIONS = {
    'string':str,
    'integer':int,
    'number': float
}

def _build_properties(model: sqlmodel.SQLModel)->Dict[str, Tuple[Type, Any]]:
    print('run build properties')
    new_properties = {}
    for k,v in model.model_json_schema()['properties'].items():
        if v.get('description') is not None and 'key' in v.get('description'):
            continue
        else:
            if k != "id":
                _new_field = Field(**{k:v for k,v in v.items() if k not in ['type','$ref','items']})
                if v.get('type') is not None and v.get('$ref') is None:
                    _converted_type = TYPE_CONVERSIONS[v['type']]
                elif v.get('$ref') is not None:
                    _converted_type = eval(v['$ref'].replace('#/$defs/',''))
                else:
                    raise NotImplementedError(f"not recongize for k: {k}, v: {v}")

                new_properties[k] = (_converted_type, _new_field)
        
    return new_properties


# build schema for Gemma output
cv_properties = _build_properties(CandidateCV)

cv_properties['educations'] = (
    List[create_model("CandidateEducation", **_build_properties(CandidateEducation))], 
    Field(description= CandidateEducation.model_json_schema()['description'])
)

cv_properties['techstacks'] = (
    List[create_model("CandidateTechStack", **_build_properties(CandidateTechStack))], 
    Field(description= CandidateTechStack.model_json_schema()['description'])
)

cv_properties['certificates'] = (
    List[create_model("CandidateCertification", **_build_properties(CandidateCertification))], 
    Field(description= CandidateCertification.model_json_schema()['description'])
)


exp_properties = _build_properties(CandidateExperience)
exp_properties['responsibilities'] = (
    List[create_model("CandidateResponsibility", **_build_properties(CandidateResponsibility))], 
    Field(description= CandidateResponsibility.model_json_schema()['description'])
)

exp_properties['projects'] = (
    List[create_model("CandidateProject", **_build_properties(CandidateProject))], 
    Field(description= CandidateProject.model_json_schema()['description'])
)

exp_properties['awards'] = (
    List[create_model("CandidateAward", **_build_properties(CandidateAward))], 
    Field(description= CandidateAward.model_json_schema()['description'])
)

cv_properties['experiences'] = (
    List[create_model("Experience", **exp_properties)], 
    Field(description= CandidateExperience.model_json_schema()['description'])
)

def _get_schema_output()->str:
    schema_dict  = StructedCVOutput.model_json_schema(mode= "serialization")
    del schema_dict['type']
    schema_str = json.dumps(schema_dict, indent= 2)
    return schema_str

StructedCVOutput = create_model("StructedCVOutput", **cv_properties)
StructedCVOutputSchema = _get_schema_output()






# _Float_Field = {"job_overview", "responsibilities", "require_skills", "preferred_skills"}

# new_properties = {}
# for k,v in JobDescriptions.model_json_schema()['properties'].items():
#     _new_description = f'Ranking score for `{k}`'
#     if (_old_description := v.get('description')) is not None:
#         _new_description +=  f'where {k} is {_old_description}'

#     _new_field = Field(
#         title = v['title'],
#         description = _new_description
#     )
#     new_properties[k] = (bool, _new_field) if k in _Float_Field else (float, _new_field)


# JobDescriptionsScoreOutput = create_model("JobDescriptionsScoreOutput", **new_properties)
