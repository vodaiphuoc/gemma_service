import { HrRegisterForm, CandidateRegisterForm } from '../components/RegisterForm';
import type { UserType } from '../components/Interfaces';

import { useState } from 'react';
import {
    ChakraProvider,
    VStack,
    Flex,
    Box,
    Button,
    Menu,
    MenuButton,
    MenuList,
    MenuItem,
    MenuItemOption,
    MenuGroup,
    MenuOptionGroup,
    MenuDivider,
} from '@chakra-ui/react';

import { ChevronDownIcon } from '@chakra-ui/icons';
import { Navigate, Link , useNavigate } from 'react-router';

export default function HomePage() {
    const [userType, setUserType] = useState<UserType>({value:'Candidate'});
    
    const [isSelected, setIsSelected] = useState<boolean>(false);

    let navigate = useNavigate();

    const handleRegisterSelect = () => {
        navigate('/register',{ state: { "userType": userType } });
    };

    return (
        <VStack width="full" align="center" justifyContent="center">
            <Box>
                <Menu closeOnSelect={true}>
                    <MenuButton as={Button} colorScheme='blue'>
                        Select User Type
                    </MenuButton>
                    <MenuList minWidth='240px'>
                        <MenuOptionGroup type='radio'>
                            <MenuItemOption 
                                onClick={() => {
                                    setIsSelected(true);
                                    setUserType({value:'Candidate'});
                                }}>
                            Candidate
                            </MenuItemOption>
                            <MenuItemOption 
                                onClick={() => {
                                    setIsSelected(true);
                                    setUserType({value:'Recruiter'})
                                }}>
                            Recruiter
                            </MenuItemOption>
                        </MenuOptionGroup>
                    </MenuList>
                </Menu>
            </Box>
            <Box>
                <Button type="button" onClick={handleRegisterSelect}>Register</Button>
            </Box>
        </VStack>
    );
}