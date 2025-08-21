import React from 'react';

export const Badge = ({ 
  children, 
  variant = 'default', 
  className = '',
  ...props 
}) => {
  const baseClasses = 'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-[#0097B2] focus:ring-offset-2';
  
  const variants = {
    default: 'border-transparent bg-[#0097B2] text-white hover:bg-[#007A93]',
    secondary: 'border-transparent bg-gray-200 text-gray-900 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600',
    destructive: 'border-transparent bg-red-600 text-white hover:bg-red-700',
    outline: 'border-[#0097B2] text-[#0097B2] hover:bg-[#0097B2]/10'
  };
  
  const variantClass = variants[variant] || variants.default;
  
  return (
    <div
      className={`${baseClasses} ${variantClass} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};