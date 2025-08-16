import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import Robot3D from './Robot3D';

const HeroContainer = styled.section`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: linear-gradient(135deg, #474545 0%, #3a3838 50%, #474545 100%);
  overflow: hidden;
  padding-top: 80px;

  @media (max-width: 768px) {
    padding-top: 120px;
    min-height: calc(100vh - 40px);
  }
`;

const HeroContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  align-items: center;
  z-index: 2;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
    padding: 40px 20px 0;
  }
`;

const TextContent = styled.div`
  z-index: 2;
`;

const Title = styled(motion.h1)`
  font-size: 4rem;
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #FAECEC 0%, #0097B2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;

  @media (max-width: 768px) {
    font-size: 2.2rem;
    line-height: 1.2;
    margin-bottom: 20px;
  }
`;

const Subtitle = styled(motion.p)`
  font-size: 1.25rem;
  color: #FAECEC;
  margin-bottom: 40px;
  opacity: 0.9;
  line-height: 1.6;

  @media (max-width: 768px) {
    font-size: 1.1rem;
  }
`;

const ButtonGroup = styled(motion.div)`
  display: flex;
  gap: 20px;
  flex-wrap: wrap;

  @media (max-width: 768px) {
    justify-content: center;
  }
`;

const PrimaryButton = styled(motion.a)`
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  color: #FAECEC;
  border: none;
  padding: 18px 36px;
  border-radius: 50px;
  font-family: 'Comfortaa', sans-serif;
  font-weight: 600;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(0, 151, 178, 0.3);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(0, 151, 178, 0.4);
    color: #FAECEC;
  }
`;

const SecondaryButton = styled(motion.button)`
  background: transparent;
  color: #0097B2;
  border: 2px solid #0097B2;
  padding: 16px 34px;
  border-radius: 50px;
  font-family: 'Comfortaa', sans-serif;
  font-weight: 600;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #0097B2;
    color: #FAECEC;
    transform: translateY(-3px);
  }
`;

const CanvasContainer = styled.div`
  height: 600px;
  position: relative;

  @media (max-width: 768px) {
    height: 400px;
  }
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
    top: 20%;
    left: 10%;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(0, 151, 178, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    animation: float 6s ease-in-out infinite;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: 20%;
    right: 15%;
    width: 150px;
    height: 150px;
    background: radial-gradient(circle, rgba(250, 236, 236, 0.05) 0%, transparent 70%);
    border-radius: 50%;
    animation: float 8s ease-in-out infinite reverse;
  }

  @keyframes float {
    0%, 100% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-20px);
    }
  }
`;

// Enhanced floating particles around the robot - more circles
const FloatingParticles = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 2;
  overflow: hidden;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 6px;
    height: 6px;
    background: #0097B2;
    border-radius: 50%;
    opacity: 0.8;
    animation: float-particle 8s ease-in-out infinite;
  }

  &::before {
    top: 15%;
    left: 15%;
    animation-delay: 0s;
  }

  &::after {
    top: 70%;
    right: 20%;
    animation-delay: 4s;
  }

  /* Additional particles using pseudo-elements */
  .particle-1,
  .particle-2,
  .particle-3,
  .particle-4,
  .particle-5 {
    position: absolute;
    width: 4px;
    height: 4px;
    background: #FAECEC;
    border-radius: 50%;
    opacity: 0.6;
    animation: float-particle 6s ease-in-out infinite;
  }

  .particle-1 {
    top: 25%;
    right: 15%;
    animation-delay: 1s;
  }

  .particle-2 {
    bottom: 20%;
    left: 25%;
    animation-delay: 2s;
  }

  .particle-3 {
    top: 45%;
    left: 10%;
    animation-delay: 3s;
  }

  .particle-4 {
    top: 60%;
    right: 35%;
    animation-delay: 5s;
  }

  .particle-5 {
    bottom: 35%;
    right: 10%;
    animation-delay: 6s;
  }

  @keyframes float-particle {
    0%, 100% {
      transform: translateY(0px) translateX(0px) scale(1);
      opacity: 0.6;
    }
    25% {
      transform: translateY(-30px) translateX(15px) scale(1.2);
      opacity: 1;
    }
    50% {
      transform: translateY(-15px) translateX(-20px) scale(0.8);
      opacity: 0.8;
    }
    75% {
      transform: translateY(-40px) translateX(10px) scale(1.1);
      opacity: 0.9;
    }
  }
`;

const HeroSection = () => {
  const handleSeeHowItWorks = () => {
    document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <HeroContainer>
      <BackgroundOrbs />
      <HeroContent>
        <TextContent>
          <Title
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            Your AI-Powered Shortcut to Financial Freedom
          </Title>
          
          <Subtitle
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
          >
            The future of investing is here. Create your own AI tools that work 24/7 — earning while you live your life.
          </Subtitle>
          
          <ButtonGroup
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
          >
            <PrimaryButton
              as="a"
              href="https://f01i.app/login"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Get Started
            </PrimaryButton>
            
            <SecondaryButton
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSeeHowItWorks}
            >
              See How It Works
            </SecondaryButton>
          </ButtonGroup>
        </TextContent>

        <CanvasContainer>
          <Robot3D position={[0, -1, 0]} scale={1.2} bottom={true} />
          <FloatingParticles>
            <div className="particle-1"></div>
            <div className="particle-2"></div>
            <div className="particle-3"></div>
            <div className="particle-4"></div>
            <div className="particle-5"></div>
          </FloatingParticles>
        </CanvasContainer>
      </HeroContent>
    </HeroContainer>
  );
};

export default HeroSection;