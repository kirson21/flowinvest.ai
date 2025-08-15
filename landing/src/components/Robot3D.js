import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere, Box, Cylinder } from '@react-three/drei';
import * as THREE from 'three';

const Robot3D = ({ position = [0, 0, 0], scale = 1 }) => {
  const robotRef = useRef();
  const headRef = useRef();
  const leftArmRef = useRef();
  const rightArmRef = useRef();
  const leftEyeRef = useRef();
  const rightEyeRef = useRef();
  const antennaRef = useRef();

  // Robot materials
  const robotMaterial = useMemo(() => 
    new THREE.MeshStandardMaterial({ 
      color: '#0097B2',
      metalness: 0.7,
      roughness: 0.3,
      emissive: '#004d5a',
      emissiveIntensity: 0.1
    }), []
  );

  const glowMaterial = useMemo(() => 
    new THREE.MeshStandardMaterial({ 
      color: '#00ffff',
      emissive: '#00ffff',
      emissiveIntensity: 0.5,
      transparent: true,
      opacity: 0.8
    }), []
  );

  const eyeMaterial = useMemo(() => 
    new THREE.MeshStandardMaterial({ 
      color: '#ffffff',
      emissive: '#00ffff',
      emissiveIntensity: 0.8,
      transparent: true,
      opacity: 0.9
    }), []
  );

  // Animation loop
  useFrame((state) => {
    const time = state.clock.elapsedTime;
    
    // Gentle floating animation
    if (robotRef.current) {
      robotRef.current.position.y = Math.sin(time) * 0.1;
    }
    
    // Head rotation
    if (headRef.current) {
      headRef.current.rotation.y = Math.sin(time * 0.5) * 0.2;
    }
    
    // Arm movements
    if (leftArmRef.current) {
      leftArmRef.current.rotation.z = Math.sin(time * 1.2) * 0.3 + 0.3;
    }
    if (rightArmRef.current) {
      rightArmRef.current.rotation.z = -Math.sin(time * 1.2) * 0.3 - 0.3;
    }
    
    // Eye glow pulsing
    if (leftEyeRef.current && rightEyeRef.current) {
      const intensity = 0.8 + Math.sin(time * 2) * 0.3;
      leftEyeRef.current.material.emissiveIntensity = intensity;
      rightEyeRef.current.material.emissiveIntensity = intensity;
    }
    
    // Antenna rotation
    if (antennaRef.current) {
      antennaRef.current.rotation.z = Math.sin(time * 3) * 0.1;
    }
  });

  return (
    <group ref={robotRef} position={position} scale={scale}>
      {/* Body */}
      <Box args={[1.2, 1.8, 0.8]} position={[0, 0, 0]} material={robotMaterial}>
        <meshStandardMaterial attach="material" {...robotMaterial} />
      </Box>
      
      {/* Chest Light */}
      <Sphere args={[0.15]} position={[0, 0.3, 0.41]} material={glowMaterial}>
        <meshStandardMaterial attach="material" {...glowMaterial} />
      </Sphere>
      
      {/* Head */}
      <group ref={headRef} position={[0, 1.4, 0]}>
        <Box args={[0.9, 0.8, 0.7]} material={robotMaterial}>
          <meshStandardMaterial attach="material" {...robotMaterial} />
        </Box>
        
        {/* Eyes */}
        <Sphere 
          ref={leftEyeRef} 
          args={[0.12]} 
          position={[-0.25, 0.1, 0.36]} 
          material={eyeMaterial}
        >
          <meshStandardMaterial attach="material" {...eyeMaterial} />
        </Sphere>
        <Sphere 
          ref={rightEyeRef} 
          args={[0.12]} 
          position={[0.25, 0.1, 0.36]} 
          material={eyeMaterial}
        >
          <meshStandardMaterial attach="material" {...eyeMaterial} />
        </Sphere>
        
        {/* Antenna */}
        <group ref={antennaRef} position={[0, 0.5, 0]}>
          <Cylinder args={[0.02, 0.02, 0.4]} material={robotMaterial}>
            <meshStandardMaterial attach="material" {...robotMaterial} />
          </Cylinder>
          <Sphere args={[0.08]} position={[0, 0.25, 0]} material={glowMaterial}>
            <meshStandardMaterial attach="material" {...glowMaterial} />
          </Sphere>
        </group>
      </group>
      
      {/* Left Arm */}
      <group ref={leftArmRef} position={[-0.8, 0.6, 0]}>
        <Cylinder args={[0.15, 0.15, 1.2]} rotation={[0, 0, Math.PI / 2]} material={robotMaterial}>
          <meshStandardMaterial attach="material" {...robotMaterial} />
        </Cylinder>
        {/* Hand */}
        <Sphere args={[0.2]} position={[-0.7, 0, 0]} material={robotMaterial}>
          <meshStandardMaterial attach="material" {...robotMaterial} />
        </Sphere>
      </group>
      
      {/* Right Arm */}
      <group ref={rightArmRef} position={[0.8, 0.6, 0]}>
        <Cylinder args={[0.15, 0.15, 1.2]} rotation={[0, 0, Math.PI / 2]} material={robotMaterial}>
          <meshStandardMaterial attach="material" {...robotMaterial} />
        </Cylinder>
        {/* Hand */}
        <Sphere args={[0.2]} position={[0.7, 0, 0]} material={robotMaterial}>
          <meshStandardMaterial attach="material" {...robotMaterial} />
        </Sphere>
      </group>
      
      {/* Legs */}
      <Cylinder args={[0.2, 0.18, 1.5]} position={[-0.3, -1.65, 0]} material={robotMaterial}>
        <meshStandardMaterial attach="material" {...robotMaterial} />
      </Cylinder>
      <Cylinder args={[0.2, 0.18, 1.5]} position={[0.3, -1.65, 0]} material={robotMaterial}>
        <meshStandardMaterial attach="material" {...robotMaterial} />
      </Cylinder>
      
      {/* Feet */}
      <Box args={[0.5, 0.15, 0.8]} position={[-0.3, -2.5, 0.2]} material={robotMaterial}>
        <meshStandardMaterial attach="material" {...robotMaterial} />
      </Box>
      <Box args={[0.5, 0.15, 0.8]} position={[0.3, -2.5, 0.2]} material={robotMaterial}>
        <meshStandardMaterial attach="material" {...robotMaterial} />
      </Box>
      
      {/* Ambient light for the robot */}
      <pointLight position={[0, 2, 2]} intensity={0.5} color="#00ffff" />
    </group>
  );
};

export default Robot3D;