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
          // Enhanced branding removal - multiple attempts
          const removeBranding = () => {
            const splineElements = document.querySelectorAll('spline-viewer');
            splineElements.forEach(element => {
              try {
                if (element.shadowRoot) {
                  // Hide the logo
                  const logo = element.shadowRoot.querySelector('#logo');
                  if (logo) {
                    logo.style.display = 'none';
                    logo.style.visibility = 'hidden';
                    logo.style.opacity = '0';
                  }
                  
                  // Hide any branding containers
                  const brandingSelectors = [
                    '[class*="built"]', 
                    '[class*="spline"]', 
                    '[id*="logo"]',
                    '[class*="watermark"]',
                    '[class*="badge"]',
                    'a[href*="spline"]',
                    'div[style*="position: absolute"][style*="bottom"]'
                  ];
                  
                  brandingSelectors.forEach(selector => {
                    const elements = element.shadowRoot.querySelectorAll(selector);
                    elements.forEach(el => {
                      el.style.display = 'none';
                      el.style.visibility = 'hidden';
                      el.style.opacity = '0';
                    });
                  });

                  // Hide text containing "spline"
                  const allTextElements = element.shadowRoot.querySelectorAll('*');
                  allTextElements.forEach(textEl => {
                    if (textEl.textContent && textEl.textContent.toLowerCase().includes('spline')) {
                      textEl.style.display = 'none';
                    }
                  });
                }

                // Also try to hide any external branding on the element itself
                const style = document.createElement('style');
                style.textContent = `
                  spline-viewer::part(logo) { display: none !important; }
                  spline-viewer [class*="logo"] { display: none !important; }
                  spline-viewer [class*="watermark"] { display: none !important; }
                `;
                document.head.appendChild(style);
                
              } catch (e) {
                // Ignore shadow DOM access errors
                console.log('Advanced branding removal attempted');
              }
            });
          };

          // Remove branding multiple times with delays
          setTimeout(removeBranding, 1000);
          setTimeout(removeBranding, 3000);
          setTimeout(removeBranding, 5000);
        };
      }
    };

    loadSplineViewer();
  }, []);

  const containerStyle = {
    position: 'absolute',
    top: bottom ? 'auto' : '50%',
    bottom: bottom ? '-10%' : 'auto', // Move even lower - into negative territory
    left: '50%',
    transform: bottom 
      ? `translateX(-50%) scale(${scale})` 
      : `translate(-50%, -50%) scale(${scale})`,
    width: '100%',
    height: bottom ? '90%' : '100%',
    zIndex: 3,
    mixBlendMode: 'normal',
    cursor: 'pointer',
    transition: 'transform 0.3s ease',
    opacity: 0.7 // 70% transparency as requested
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
        style={{ 
          width: '100%', 
          height: '100%',
          cursor: 'pointer',
          pointerEvents: 'auto'
        }}
      />
    </div>
  );
};

export default Robot3D;