import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import { UserPlus, Settings, TestTube, BarChart3 } from 'lucide-react';

const SectionContainer = styled.section`
  padding: 120px 0;
  background: linear-gradient(180deg, #3a3838 0%, #474545 100%);
`;

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
`;

const SectionHeader = styled.div`
  text-align: center;
  margin-bottom: 80px;
`;

const SectionTitle = styled(motion.h2)`
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #FAECEC 0%, #0097B2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;

  @media (max-width: 768px) {
    font-size: 2rem;
  }
`;

const StepsContainer = styled.div`
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 60px;

  @media (min-width: 768px) {
    gap: 80px;
  }
`;

const StepCard = styled(motion.div)`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;

  &:nth-child(even) {
    .step-content {
      order: 2;
    }
    .step-visual {
      order: 1;
    }
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 30px;
    text-align: center;

    &:nth-child(even) {
      .step-content {
        order: 1;
      }
      .step-visual {
        order: 2;
      }
    }
  }
`;

const StepContent = styled.div`
  padding: 20px;
`;

const StepNumber = styled.div`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  border-radius: 50%;
  font-size: 1.5rem;
  font-weight: 700;
  color: #FAECEC;
  margin-bottom: 24px;
  box-shadow: 0 8px 25px rgba(0, 151, 178, 0.3);

  @media (max-width: 768px) {
    margin: 0 auto 24px;
  }
`;

const StepTitle = styled.h3`
  font-size: 2rem;
  font-weight: 600;
  color: #FAECEC;
  margin-bottom: 16px;

  @media (max-width: 768px) {
    font-size: 1.5rem;
  }
`;

const StepDescription = styled.p`
  color: #FAECEC;
  opacity: 0.8;
  line-height: 1.6;
  font-size: 1.1rem;
`;

const StepVisual = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  background: linear-gradient(135deg, rgba(0, 151, 178, 0.1) 0%, rgba(250, 236, 236, 0.05) 100%);
  border: 1px solid rgba(0, 151, 178, 0.2);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100px;
    height: 100px;
    background: radial-gradient(circle, rgba(0, 151, 178, 0.2) 0%, transparent 70%);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    animation: pulse 3s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% {
      transform: translate(-50%, -50%) scale(1);
    }
    50% {
      transform: translate(-50%, -50%) scale(1.2);
    }
  }
`;

const IconWrapper = styled.div`
  z-index: 2;
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  padding: 20px;
  border-radius: 50%;
  box-shadow: 0 8px 25px rgba(0, 151, 178, 0.3);
`;

const ConnectorLine = styled.div`
  position: absolute;
  left: 50%;
  top: 50%;
  width: 2px;
  height: 60px;
  background: linear-gradient(to bottom, #0097B2, transparent);
  transform: translateX(-50%);
  z-index: 1;

  @media (max-width: 768px) {
    display: none;
  }
`;

const HowItWorksSection = () => {
  const steps = [
    {
      number: "1",
      title: "Sign Up & Connect Your Exchange",
      description: "Securely link Bybit (and soon Binance, OKX, Crypto.com). Your API keys are encrypted and never used to withdraw funds.",
      icon: <UserPlus size={40} color="#FAECEC" />
    },
    {
      number: "2",
      title: "Build Your Bot",
      description: "Use our AI constructor powered by GPT-5 for instant setup, or configure every detail manually for complete control.",
      icon: <Settings size={40} color="#FAECEC" />
    },
    {
      number: "3",
      title: "Test & Optimize",
      description: "Run comprehensive simulations with historical data before going live. Refine your strategy risk-free.",
      icon: <TestTube size={40} color="#FAECEC" />
    },
    {
      number: "4",
      title: "Invest & Track",
      description: "Deploy your bot and monitor performance with real-time analytics, profit tracking, and automated reporting.",
      icon: <BarChart3 size={40} color="#FAECEC" />
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.4
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -50 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.8,
        ease: "easeOut"
      }
    }
  };

  return (
    <SectionContainer id="how-it-works">
      <Container>
        <SectionHeader>
          <SectionTitle
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            How It Works
          </SectionTitle>
        </SectionHeader>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <StepsContainer>
            {steps.map((step, index) => (
              <div key={index} style={{ position: 'relative' }}>
                <StepCard variants={itemVariants}>
                  <StepContent className="step-content">
                    <StepNumber>{step.number}</StepNumber>
                    <StepTitle>{step.title}</StepTitle>
                    <StepDescription>{step.description}</StepDescription>
                  </StepContent>
                  
                  <StepVisual className="step-visual">
                    <IconWrapper>
                      {step.icon}
                    </IconWrapper>
                  </StepVisual>
                </StepCard>
                
                {index < steps.length - 1 && <ConnectorLine />}
              </div>
            ))}
          </StepsContainer>
        </motion.div>
      </Container>
    </SectionContainer>
  );
};

export default HowItWorksSection;