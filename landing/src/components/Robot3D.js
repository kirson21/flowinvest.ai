import React, { useEffect, useRef } from 'react';

const Robot3D = ({ position = [0, 0, 0], scale = 1 }) => {
  const splineRef = useRef();

  useEffect(() => {
    // Load the Spline viewer script
    const loadSplineViewer = () => {
      if (!window.customElements.get('spline-viewer')) {
        const script = document.createElement('script');
        script.type = 'module';
        script.src = 'https://unpkg.com/@splinetool/viewer@1.9.0/build/spline-viewer.js';
        document.head.appendChild(script);
        
        script.onload = () => {
          // Optional: Remove Spline logo
          setTimeout(() => {
            const splineElements = document.querySelectorAll('spline-viewer');
            splineElements.forEach(element => {
              try {
                if (element.shadowRoot) {
                  const logo = element.shadowRoot.querySelector('#logo');
                  if (logo) {
                    logo.style.display = 'none';
                  }
                }
              } catch (e) {
                // Ignore shadow DOM access errors
                console.log('Spline logo removal skipped');
              }
            });
          }, 3000);
        };
      }
    };

    loadSplineViewer();
  }, []);

  const containerStyle = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: `translate(-50%, -50%) scale(${scale})`,
    width: '100%',
    height: '100%',
    zIndex: 3,
    mixBlendMode: 'normal'
  };

  return (
    <div style={containerStyle} ref={splineRef}>
      <spline-viewer 
        url="https://prod.spline.design/AqtlWJlNbO-ZMkvz/scene.splinecode"
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
};

export default Robot3D;