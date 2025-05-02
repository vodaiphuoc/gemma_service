interface CandidateFormDataInput {
    name: string;
    email: string;
    phone: string;
    password: string
}


interface HRFormDataInput extends CandidateFormDataInput {
    companyName: string;
    companyLocation: string; 
}

interface UserType {
    value: "Candidate" | "Recruiter";
}


export type { CandidateFormDataInput };
export type { HRFormDataInput };
export type { UserType };