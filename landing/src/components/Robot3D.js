import React from 'react';
import Spline from '@splinetool/react-spline';

const Robot3D = ({ position = [0, 0, 0], scale = 1 }) => {
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
    <div style={containerStyle}>
      <Spline 
        scene="https://prod.spline.design/AqtlWJlNbO-ZMkvz/scene.splinecode"
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
};

export default Robot3D;