import  HomePage from './pages/Home';
import  RegisterPage  from './pages/Register';


import React from 'react';
import {
    ChakraProvider
} from '@chakra-ui/react';

import {ChevronDownIcon } from '@chakra-ui/icons';
import {BrowserRouter, Routes, Route, Navigate, Link } from 'react-router';

function App() {
    return (
        <ChakraProvider>
            <BrowserRouter>
                <Routes>
                    <Route path="/" element = {<HomePage />} />
                    <Route path="/register" element={<RegisterPage/>}/>
                </Routes>
                
            </BrowserRouter>
        </ChakraProvider>    
    );
}

export default App;



// App.js (using react-router-dom)
// import React, { useState, useContext, createContext } from 'react';
// import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
// import LoginForm from './LoginForm';
// import HomePage from './HomePage';


// Create an Auth Context
// const AuthContext = createContext(null);

// Auth Provider component (optional but good practice)
// const AuthProvider = ({ children }) => {
//     const [user, setUser] = useState(null); // null means not logged in

//     const login = (userData) => {
//         setUser(userData);
//         // Store token etc.
//     };

//     const logout = () => {
//         setUser(null);
//         // Remove token etc.
//     };

//     // Provide user and login/logout functions to children
//     return (
//         <AuthContext.Provider value={{ user, login, logout }}>
//         {children}
//         </AuthContext.Provider>
//     );
// };

// Custom hook to use auth context
// const useAuth = () => {
//     return useContext(AuthContext);
// };

// Protected Route Component
// const ProtectedRoute = ({ children }) => {
//     const auth = useAuth();
//     // If user is not logged in, redirect to login page
//     if (!auth.user) {
//         return <Navigate to="/login" replace />;
//     }
//     // If logged in, render the requested component
//     return children;
// };


// function App() {
//     return (
//         <BrowserRouter>
//             <AuthProvider>
//                 <Routes>
//                     <Route path="/" element={<HomePage />} />
//                     <Route path="/login" element={<LoginForm />} /> {/* Login form page */}

//                     {/* Protected Routes */}
//                     <Route
//                         path="/dashboard"
//                         element={
//                             <ProtectedRoute>
//                                 <Dashboard />
//                             </ProtectedRoute>
//                         }
//                     />

//                     {/* Redirect to login if trying to access protected route without auth */}
//                     <Route path="*" element={<Navigate to="/login" replace />} />
//                 </Routes>
//             </AuthProvider>
//         </BrowserRouter>
//     );
// }

// export default App;

// --- Example Usage in LoginForm.jsx with React Router ---
// Update LoginForm to use the context and redirect
// import { useNavigate } from 'react-router-dom';
// import { useAuth } from './App'; // Import the hook from App or auth file

// function LoginForm() {
//   // ... existing state and handleSubmit logic ...
//   const auth = useAuth(); // Get auth context
//   const navigate = useNavigate(); // Hook for navigation

//   const handleSubmit = async (event) => {
//      // ... login logic ...
//      try {
//         // ... API call simulation ...
//         const userData = { name: username, id: 'user123' };
//         auth.login(userData); // Update auth context state
//         navigate('/dashboard'); // Redirect on success
//      } catch (err) {
//         // ... handle error ...
//      } finally {
//        // ...
//      }
//   }
//   // ... rest of LoginForm JSX ...
// }