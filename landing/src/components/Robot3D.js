import React, { useEffect, useRef } from 'react';

const Robot3D = ({ position = [0, 0, 0], scale = 1, bottom = false }) => {
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
          // Remove Spline logo and branding
          setTimeout(() => {
            const splineElements = document.querySelectorAll('spline-viewer');
            splineElements.forEach(element => {
              try {
                if (element.shadowRoot) {
                  // Hide the logo
                  const logo = element.shadowRoot.querySelector('#logo');
                  if (logo) {
                    logo.style.display = 'none';
                  }
                  
                  // Hide "built with spline" text
                  const builtWith = element.shadowRoot.querySelector('[class*="built"], [class*="spline"], [style*="built"]');
                  if (builtWith) {
                    builtWith.style.display = 'none';
                  }
                  
                  // Hide any watermark or branding text
                  const textElements = element.shadowRoot.querySelectorAll('div, span, p, a');
                  textElements.forEach(textEl => {
                    if (textEl.textContent && textEl.textContent.toLowerCase().includes('spline')) {
                      textEl.style.display = 'none';
                    }
                  });
                }
              } catch (e) {
                // Ignore shadow DOM access errors
                console.log('Spline branding removal skipped');
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
    top: bottom ? 'auto' : '50%',
    bottom: bottom ? '0' : 'auto',
    left: '50%',
    transform: bottom 
      ? `translateX(-50%) scale(${scale})` 
      : `translate(-50%, -50%) scale(${scale})`,
    width: '100%',
    height: bottom ? '80%' : '100%',
    zIndex: 3,
    mixBlendMode: 'normal',
    cursor: 'pointer',
    transition: 'transform 0.3s ease'
  };

  return (
    <div 
      style={containerStyle} 
      ref={splineRef}
      onMouseEnter={() => {
        if (splineRef.current) {
          splineRef.current.style.transform = bottom 
            ? `translateX(-50%) scale(${scale * 1.05})` 
            : `translate(-50%, -50%) scale(${scale * 1.05})`;
        }
      }}
      onMouseLeave={() => {
        if (splineRef.current) {
          splineRef.current.style.transform = bottom 
            ? `translateX(-50%) scale(${scale})` 
            : `translate(-50%, -50%) scale(${scale})`;
        }
      }}
    >
      <spline-viewer 
        url="https://prod.spline.design/AqtlWJlNbO-ZMkvz/scene.splinecode"
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
};

export default Robot3D;