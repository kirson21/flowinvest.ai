import React from 'react';

export const Button = ({ 
  children, 
  onClick, 
  disabled = false, 
  variant = 'default', 
  size = 'default', 
  className = '',
  ...props 
}) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0097B2] focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  
  const variants = {
    default: 'bg-[#0097B2] text-white hover:bg-[#007A93] active:bg-[#006580]',
    destructive: 'bg-red-600 text-white hover:bg-red-700 active:bg-red-800',
    outline: 'border border-[#0097B2] text-[#0097B2] hover:bg-[#0097B2] hover:text-white active:bg-[#007A93]',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 active:bg-gray-400 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600',
    ghost: 'text-[#0097B2] hover:bg-[#0097B2]/10 hover:text-[#007A93] active:bg-[#0097B2]/20',
    link: 'text-[#0097B2] underline-offset-4 hover:underline hover:text-[#007A93]'
  };
  
  const sizes = {
    default: 'h-10 py-2 px-4 text-sm',
    sm: 'h-9 px-3 rounded-md text-sm',
    lg: 'h-11 px-8 rounded-md text-base'
  };
  
  const variantClass = variants[variant] || variants.default;
  const sizeClass = sizes[size] || sizes.default;
  
  return (
    <button
      className={`${baseClasses} ${variantClass} ${sizeClass} ${className}`}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};