import React from 'react';

export const Label = React.forwardRef(({ 
  className = '',
  ...props 
}, ref) => {
  return (
    <label
      ref={ref}
      className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-700 dark:text-gray-300 ${className}`}
      {...props}
    />
  );
});

Label.displayName = 'Label';