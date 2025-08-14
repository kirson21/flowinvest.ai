import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import { Canvas, useFrame } from '@react-three/fiber';
import { Sphere, MeshDistortMaterial } from '@react-three/drei';
import styled from 'styled-components';

const SectionContainer = styled.section`
  padding: 120px 0;
  background: linear-gradient(135deg, #3a3838 0%, #474545 50%, #3a3838 100%);
  position: relative;
  overflow: hidden;
`;

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
  text-align: center;
  position: relative;
  z-index: 2;
`;

const SectionTitle = styled(motion.h2)`
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #FAECEC 0%, #0097B2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;

  @media (max-width: 768px) {
    font-size: 2.5rem;
  }
`;

const SectionSubtitle = styled(motion.p)`
  font-size: 1.25rem;
  color: #FAECEC;
  opacity: 0.9;
  margin-bottom: 50px;
  line-height: 1.6;

  @media (max-width: 768px) {
    font-size: 1.1rem;
  }
`;

const ButtonGroup = styled(motion.div)`
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: center;
  }
`;

const PrimaryButton = styled(motion.button)`
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  color: #FAECEC;
  border: none;
  padding: 20px 40px;
  border-radius: 50px;
  font-family: 'Comfortaa', sans-serif;
  font-weight: 600;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 10px 30px rgba(0, 151, 178, 0.4);
  min-width: 200px;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 40px rgba(0, 151, 178, 0.5);
  }

  @media (max-width: 768px) {
    width: 100%;
    max-width: 300px;
  }
`;

const SecondaryButton = styled(motion.button)`
  background: transparent;
  color: #0097B2;
  border: 2px solid #0097B2;
  padding: 18px 38px;
  border-radius: 50px;
  font-family: 'Comfortaa', sans-serif;
  font-weight: 600;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 200px;

  &:hover {
    background: #0097B2;
    color: #FAECEC;
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(0, 151, 178, 0.3);
  }

  @media (max-width: 768px) {
    width: 100%;
    max-width: 300px;
  }
`;

const BackgroundCanvas = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  opacity: 0.3;
`;

const BackgroundOrbs = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 10%;
    left: 10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(0, 151, 178, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    animation: float 8s ease-in-out infinite;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: 10%;
    right: 10%;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(250, 236, 236, 0.05) 0%, transparent 70%);
    border-radius: 50%;
    animation: float 6s ease-in-out infinite reverse;
  }

  @keyframes float {
    0%, 100% {
      transform: translateY(0px) scale(1);
    }
    50% {
      transform: translateY(-30px) scale(1.1);
    }
  }
`;

// 3D Robot pointing at buttons
const PointingRobot = () => {
  const meshRef = useRef();

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.2;
      meshRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.1;
    }
  });

  return (
    <group position={[2, 0, 0]}>
      <Sphere ref={meshRef} args={[0.8, 32, 32]} scale={1.2}>
        <MeshDistortMaterial
          color="#0097B2"
          attach="material"
          distort={0.2}
          speed={1.5}
          roughness={0}
          transparent
          opacity={0.6}
        />
      </Sphere>
    </group>
  );
};

const CTASection = () => {
  const handleGetStarted = () => {
    window.location.href = '/app';
  };

  const handleExploreMarketplace = () => {
    window.location.href = '/app';
  };

  return (
    <SectionContainer>
      <BackgroundOrbs />
      
      <BackgroundCanvas>
        <Canvas camera={{ position: [0, 0, 5] }}>
          <ambientLight intensity={0.3} />
          <directionalLight position={[10, 10, 5]} intensity={0.5} />
          <PointingRobot />
        </Canvas>
      </BackgroundCanvas>

      <Container>
        <SectionTitle
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          Start Building Your Future Today
        </SectionTitle>
        
        <SectionSubtitle
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          viewport={{ once: true }}
        >
          Join thousands of investors who are already using AI to secure their financial freedom. Your journey starts with a single click.
        </SectionSubtitle>
        
        <ButtonGroup
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          viewport={{ once: true }}
        >
          <PrimaryButton
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleGetStarted}
          >
            Get Started Free
          </PrimaryButton>
          
          <SecondaryButton
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleExploreMarketplace}
          >
            Explore Marketplace
          </SecondaryButton>
        </ButtonGroup>
      </Container>
    </SectionContainer>
  );
};

export default CTASection;