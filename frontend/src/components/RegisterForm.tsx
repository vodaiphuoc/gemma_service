import React, { useState } from 'react';

import userRegister from './Api';
import type { 
    HRFormDataInput, 
    CandidateFormDataInput 
} from "./Interfaces";

import {
    Button,
    Flex,
    Box,
    Heading,
    Input,
    FormControl,
    FormLabel,
    InputGroup,
    InputRightElement,
    CircularProgress,
    FormErrorMessage,
    FormHelperText
} from '@chakra-ui/react'


const phonePattern: RegExp = /(84|0[3|5|7|8|9])+([0-9]{8})\b/g;

export function HrRegisterForm() {      
    const [formData, setFormData] = useState<HRFormDataInput>({
        name: '',
        email: '',
        phone: '',
        companyName: '',
        companyLocation: '',
        password: ''
    });

    // for password
    const [pwdShow, setPwdShow] = useState(false);
    const handleClick = () => setPwdShow(!pwdShow)

    // for submit button
    const [isLoading, setIsLoading] = useState(false);

    // submit handling
    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setIsLoading(true);
        try {
            await userRegister(formData);
            setIsLoading(false);
        } catch (error) {
            setIsLoading(false);
        }
    };

    const [phoneError, setPhoneError] = useState(false);
    
    const checkPhoneNumer = (event: React.ChangeEvent<HTMLInputElement>) => {
        const onBlurPhoneNum: boolean = !phonePattern.test(event.currentTarget.value);
        setPhoneError(onBlurPhoneNum);
        
        if (!phoneError) {
            setFormData({
                ...formData,
                phone: event.currentTarget.value
            });
        }
    }

    return (
        <Flex width="full" align="center" justifyContent="center">
          <Box p={2}>
            <Box textAlign="center">
                <Heading>Login</Heading>
            </Box>
            <Box my={4} textAlign="left">
                <form onSubmit ={handleSubmit}>
                    <FormControl isRequired>
                        <FormLabel>Full name</FormLabel>
                        <Input 
                            placeholder="Your full name" 
                            type='name' 
                            onChange={event => 
                                setFormData({
                                ...formData,
                                name: event.currentTarget.value
                            })}
                        />
                    </FormControl>

                    <FormControl isRequired>
                        <FormLabel>Email address</FormLabel>
                        <Input 
                            placeholder="myemail@mail.com" 
                            type='email'
                            value={formData.email}
                            onChange={event => 
                                setFormData({
                                ...formData,
                                email: event.currentTarget.value
                            })}
                        />
                        <FormHelperText>Your working or personal email</FormHelperText>
                    </FormControl>
                    
                    <FormControl isRequired isInvalid={phoneError}>
                        <FormLabel>Phone number</FormLabel>
                        <Input
                            placeholder="84..."
                            type='tel'
                            onBlur={checkPhoneNumer}
                        />
                        { phoneError ? (
                            <FormErrorMessage>Phone must be numbers</FormErrorMessage>
                        ) : (
                            <FormHelperText>Your working phone number</FormHelperText>
                        )}
                    </FormControl>
                    
                    <FormControl isRequired>
                        <FormLabel>Company name</FormLabel>
                        <Input 
                            type='name' 
                            onChange={event => setFormData({
                                ...formData,
                                companyName: event.currentTarget.value
                            })}
                        />
                    </FormControl>

                    <FormControl isRequired>
                        <FormLabel>Company Location</FormLabel>
                        <Input
                            type='name' 
                            onChange={event => setFormData({
                                ...formData,
                                companyLocation: event.currentTarget.value
                            })}
                        />
                    </FormControl>

                    <FormControl isRequired>
                        <FormLabel>Your password</FormLabel>
                        <InputGroup size='md'>
                            <Input
                                pr='4.5rem'
                                type={pwdShow ? 'text' : 'password'}
                                placeholder='Enter password'
                                onChange={event => setFormData({
                                    ...formData,
                                    password: event.currentTarget.value
                                })}
                            />
                            <InputRightElement width='4.5rem'>
                                <Button h='1.75rem' size='sm' onClick={handleClick}>
                                {pwdShow ? 'Hide' : 'Show'}
                                </Button>
                            </InputRightElement>
                        </InputGroup>
                    </FormControl>
                    
                    <Button width="full" mt={4} type="submit">
                        {isLoading ? (
                            <CircularProgress isIndeterminate size="24px" color="teal" />
                        ) : (
                            'Register'
                        )}
                    </Button>
                </form>
            </Box>
          </Box>
        </Flex>
    );
    
}

export function CandidateRegisterForm() {      
    const [formData, setFormData] = useState<CandidateFormDataInput>({
        name: '',
        email: '',
        phone: '',
        password: ''
    });

    // for password
    const [pwdShow, setPwdShow] = useState(false);
    const handleClick = () => setPwdShow(!pwdShow)

    // for submit button
    const [isLoading, setIsLoading] = useState(false);

    // submit handling
    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setIsLoading(true);
        try {
            await userRegister(formData);
            setIsLoading(false);
        } catch (error) {
            setIsLoading(false);
        }
    };

    const [phoneError, setPhoneError] = useState(false);

    const checkPhoneNumer = (event: React.ChangeEvent<HTMLInputElement>) => {
        const onBlurPhoneNum: boolean = !phonePattern.test(event.currentTarget.value);
        setPhoneError(onBlurPhoneNum);
        
        if (!phoneError) {
            setFormData({
                ...formData,
                phone: event.currentTarget.value
            });
        }
    }

    return (
        <Flex width="full" align="center" justifyContent="center">
          <Box p={2}>
            <Box textAlign="center">
                <Heading>Login</Heading>
            </Box>
            <Box my={4} textAlign="left">
                <form onSubmit ={handleSubmit}>
                    <FormControl isRequired>
                        <FormLabel>Full name</FormLabel>
                        <Input 
                            placeholder="Your full name" 
                            type='name' 
                            onChange={event => 
                                setFormData({
                                ...formData,
                                name: event.currentTarget.value
                            })}
                        />
                    </FormControl>

                    <FormControl isRequired>
                        <FormLabel>Email address</FormLabel>
                        <Input 
                            placeholder="myemail@mail.com" 
                            type='email'
                            value={formData.email}
                            onChange={event => 
                                setFormData({
                                ...formData,
                                email: event.currentTarget.value
                            })}
                        />
                        <FormHelperText>Your working or personal email</FormHelperText>
                    </FormControl>
                    
                    <FormControl isRequired isInvalid={phoneError}>
                        <FormLabel>Phone number</FormLabel>
                        <Input
                            placeholder="84..."
                            type='tel'
                            onBlur={checkPhoneNumer}
                        />
                        { phoneError ? (
                            <FormErrorMessage>Phone must be numbers</FormErrorMessage>
                        ) : (
                            <FormHelperText>Your working phone number</FormHelperText>
                        )}
                    </FormControl>

                    <FormControl isRequired>
                        <FormLabel>Your password</FormLabel>
                        <InputGroup size='md'>
                            <Input
                                pr='4.5rem'
                                type={pwdShow ? 'text' : 'password'}
                                placeholder='Enter password'
                                onChange={event => setFormData({
                                    ...formData,
                                    password: event.currentTarget.value
                                })}
                            />
                            <InputRightElement width='4.5rem'>
                                <Button h='1.75rem' size='sm' onClick={handleClick}>
                                {pwdShow ? 'Hide' : 'Show'}
                                </Button>
                            </InputRightElement>
                        </InputGroup>
                    </FormControl>
                    
                    <Button width="full" mt={4} type="submit">
                        {isLoading ? (
                            <CircularProgress isIndeterminate size="24px" color="teal" />
                        ) : (
                            'Register'
                        )}
                    </Button>
                </form>
            </Box>
          </Box>
        </Flex>
    );
    
}

