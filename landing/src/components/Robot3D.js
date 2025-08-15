import React, { useEffect, useRef } from 'react';

const Robot3D = ({ position = [0, 0, 0], scale = 1 }) => {
  const splineRef = useRef();

  useEffect(() => {
    // Load the Spline viewer script if not already loaded
    if (!window.customElements.get('spline-viewer')) {
      const script = document.createElement('script');
      script.type = 'module';
      script.src = 'https://unpkg.com/@splinetool/viewer@1.3.5/build/spline-viewer.js';
      document.head.appendChild(script);
      
      script.onload = () => {
        // Remove the logo from Spline viewer after it loads
        setTimeout(() => {
          const splineElements = document.querySelectorAll('spline-viewer');
          splineElements.forEach(element => {
            if (element.shadowRoot) {
              const logo = element.shadowRoot.querySelector('#logo');
              if (logo) {
                logo.remove();
              }
            }
          });
        }, 2000);
      };
    }

    // Clean up on unmount
    return () => {
      // No cleanup needed for this implementation
    };
  }, []);

  const containerStyle = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: `translate(-50%, -50%) scale(${scale})`,
    width: '100%',
    height: '100%',
    zIndex: 3,
    mixBlendMode: 'exclusion'
  };

  return (
    <div style={containerStyle} ref={splineRef}>
      <spline-viewer url="https://prod.spline.design/AqtlWJlNbO-ZMkvz/scene.splinecode" />
    </div>
  );
};

export default Robot3D;