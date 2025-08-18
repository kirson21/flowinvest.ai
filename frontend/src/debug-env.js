// Debug environment variables
console.log('=== ENVIRONMENT VARIABLES DEBUG ===');
console.log('process.env.REACT_APP_BACKEND_URL:', process.env.REACT_APP_BACKEND_URL);
console.log('import.meta.env.REACT_APP_BACKEND_URL:', import.meta?.env?.REACT_APP_BACKEND_URL);
console.log('process.env.NODE_ENV:', process.env.NODE_ENV);
console.log('All process.env:', process.env);
console.log('All import.meta.env:', import.meta?.env);
console.log('=== END ENVIRONMENT VARIABLES DEBUG ===');

export default {};