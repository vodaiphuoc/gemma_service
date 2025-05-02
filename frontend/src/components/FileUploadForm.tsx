// import React, { useState } from 'react';

// // FileUploadForm component for handling file uploads
// const FileUploadForm = () => {
//     // State to hold the selected file
//     const [selectedFile, setSelectedFile] = useState(null);
//     // State to manage loading state during submission (optional, but good practice)
//     const [isLoading, setIsLoading] = useState(false);
//     // State to hold any submission message (e.g., success or error)
//     const [message, setMessage] = useState('');

//     // Handler for when a file is selected
//     const handleFileChange = (event) => {
//         // Get the selected file from the input element
//         const file = event.target.files[0];
//         // Update the state with the selected file
//         setSelectedFile(file);
//         // Clear any previous messages
//         setMessage('');
//     };

//     // Handler for form submission
//     const handleSubmit = async (event) => {
//         // Prevent the default form submission behavior
//         event.preventDefault();

//         // Check if a file has been selected
//         if (!selectedFile) {
//         setMessage('Please select a file first.');
//         return;
//         }

//         // Set loading state to true
//         setIsLoading(true);
//         // Clear any previous messages
//         setMessage('');

//         // Create a FormData object to prepare the file for sending
//         // FormData is used to send form data, including files, via HTTP requests
//         const formData = new FormData();
//         // Append the selected file to the FormData object
//         // 'file' is the key that the server will use to access the file
//         formData.append('file', selectedFile);

//         // In a real application, you would send this formData to your backend API
//         // using fetch or a library like Axios.
//         // Example using fetch (replace with your actual upload endpoint):
//         /*
//         try {
//         const response = await fetch('/api/upload', { // Replace with your API endpoint
//             method: 'POST',
//             body: formData, // Send the FormData object
//         });

//         if (response.ok) {
//             const result = await response.json();
//             setMessage('File uploaded successfully!');
//             console.log('Upload successful:', result);
//         } else {
//             const error = await response.json();
//             setMessage(`Upload failed: ${error.message || response.statusText}`);
//             console.error('Upload failed:', response.status, error);
//         }
//         } catch (error) {
//         setMessage(`An error occurred: ${error.message}`);
//         console.error('An error occurred during upload:', error);
//         } finally {
//         setIsLoading(false); // Set loading state back to false
//         // Optionally clear the selected file after successful upload
//         // setSelectedFile(null);
//         }
//         */

//         // For demonstration purposes, we'll just log the file info and simulate a delay
//         console.log('Preparing to upload file:', selectedFile.name, selectedFile.type, selectedFile.size);

//         // Simulate an asynchronous upload process
//         setTimeout(() => {
//         setIsLoading(false); // Set loading state back to false
//         setMessage(`Simulated upload of "${selectedFile.name}" complete.`);
//         console.log('Simulated upload complete.');
//         // Optionally clear the selected file after simulated upload
//         // setSelectedFile(null);
//         }, 2000); // Simulate a 2-second upload time
//     };

//     return (
//         // Form element with Tailwind CSS classes for styling
//         <form onSubmit={handleSubmit} className="max-w-sm mx-auto p-6 bg-white rounded-lg shadow-md">
//         <h2 className="text-2xl font-bold mb-4 text-center text-gray-800">Upload File</h2>

//         {/* File input element */}
//         <div className="mb-4">
//             <label htmlFor="fileInput" className="block text-gray-700 text-sm font-semibold mb-2">
//             Choose File:
//             </label>
//             <input
//             type="file"
//             id="fileInput"
//             onChange={handleFileChange}
//             // Tailwind classes for styling the file input (can be tricky to style consistently across browsers)
//             className="block w-full text-sm text-gray-500
//                         file:mr-4 file:py-2 file:px-4
//                         file:rounded-full file:border-0
//                         file:text-sm file:font-semibold
//                         file:bg-blue-50 file:text-blue-700
//                         hover:file:bg-blue-100"
//             />
//         </div>

//         {/* Submit button */}
//         <button
//             type="submit"
//             disabled={!selectedFile || isLoading} // Disable button if no file is selected or loading
//             className={`w-full bg-blue-500 text-white font-bold py-2 px-4 rounded-md
//                     hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50
//                     ${(!selectedFile || isLoading) ? 'opacity-50 cursor-not-allowed' : ''}`}
//         >
//             {isLoading ? 'Uploading...' : 'Upload File'}
//         </button>

//         {/* Display messages */}
//         {message && (
//             <p className={`mt-4 text-center text-sm ${message.includes('failed') ? 'text-red-500' : 'text-green-500'}`}>
//             {message}
//             </p>
//         )}
//     </form>
//   );
// };

// export default FileUploadForm; // Export the component for use in your application
