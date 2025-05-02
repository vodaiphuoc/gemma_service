import { HrRegisterForm, CandidateRegisterForm } from '../components/RegisterForm';
import type { UserType } from '../components/Interfaces';

import { useLocation } from 'react-router'

export default function RegisterPage() {
    let location = useLocation();
    const selectedUserType: UserType = location.state.userType
    return (
        <>
            {selectedUserType.value === 'Candidate' ? (
                <CandidateRegisterForm/>
            ) : (
                <HrRegisterForm/>
            )
            }
        </>
    )
}