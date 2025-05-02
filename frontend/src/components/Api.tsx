import type { HRFormDataInput, CandidateFormDataInput } from "./Interfaces";

export default async function userRegister(data: HRFormDataInput | CandidateFormDataInput) {
    const response = await fetch('api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            
        },
        body: JSON.stringify(data),
    });

    if (response.ok) {
        const result = await response.json();
        
        console.log('Submission successful:', result);
        // Optionally reset the form fields after successful submission
        // setFormData({ name: '', email: '', password: '', message: '' });
    } else {
        const error = await response.json();
        console.error('Submission failed:', response.status, error);
    }
}