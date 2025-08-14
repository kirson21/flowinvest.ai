import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import { Shield, Lock, Key, Eye } from 'lucide-react';

const SectionContainer = styled.section`
  padding: 120px 0;
  background: linear-gradient(180deg, #474545 0%, #3a3838 100%);
`;

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
`;

const ContentWrapper = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
  }
`;

const TextContent = styled.div``;

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

const SectionSubtitle = styled(motion.p)`
  font-size: 1.25rem;
  color: #FAECEC;
  opacity: 0.9;
  margin-bottom: 40px;
  line-height: 1.6;

  @media (max-width: 768px) {
    font-size: 1.1rem;
  }
`;

const SecurityFeatures = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const SecurityFeature = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(0, 151, 178, 0.1) 0%, rgba(250, 236, 236, 0.05) 100%);
  border-radius: 15px;
  border: 1px solid rgba(0, 151, 178, 0.2);
  backdrop-filter: blur(10px);
`;

const FeatureIcon = styled.div`
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(0, 151, 178, 0.3);
  flex-shrink: 0;
`;

const FeatureText = styled.div`
  flex: 1;
`;

const FeatureTitle = styled.h4`
  font-size: 1.1rem;
  font-weight: 600;
  color: #FAECEC;
  margin-bottom: 4px;
`;

const FeatureDescription = styled.p`
  font-size: 0.9rem;
  color: #FAECEC;
  opacity: 0.8;
  line-height: 1.4;
`;

const VisualContent = styled.div`
  position: relative;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const SecurityVisual = styled.div`
  position: relative;
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, rgba(0, 151, 178, 0.1) 0%, rgba(250, 236, 236, 0.05) 100%);
  border: 2px solid rgba(0, 151, 178, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(20px);

  &::before {
    content: '';
    position: absolute;
    top: -20px;
    left: -20px;
    right: -20px;
    bottom: -20px;
    border: 1px solid rgba(0, 151, 178, 0.2);
    border-radius: 50%;
    animation: rotate 20s linear infinite;
  }

  &::after {
    content: '';
    position: absolute;
    top: -40px;
    left: -40px;
    right: -40px;
    bottom: -40px;
    border: 1px solid rgba(0, 151, 178, 0.1);
    border-radius: 50%;
    animation: rotate 30s linear infinite reverse;
  }

  @keyframes rotate {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
`;

const CentralIcon = styled.div`
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20px 40px rgba(0, 151, 178, 0.4);
  z-index: 2;
`;

const OrbitingElements = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200px;
  height: 200px;
  transform: translate(-50%, -50%);
  animation: orbit 15s linear infinite;

  @keyframes orbit {
    from {
      transform: translate(-50%, -50%) rotate(0deg);
    }
    to {
      transform: translate(-50%, -50%) rotate(360deg);
    }
  }
`;

const OrbitElement = styled.div`
  position: absolute;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(0, 151, 178, 0.3);

  &:nth-child(1) {
    top: 0;
    left: 50%;
    transform: translateX(-50%);
  }

  &:nth-child(2) {
    top: 50%;
    right: 0;
    transform: translateY(-50%);
  }

  &:nth-child(3) {
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
  }

  &:nth-child(4) {
    top: 50%;
    left: 0;
    transform: translateY(-50%);
  }
`;

const SecuritySection = () => {
  const securityFeatures = [
    {
      icon: <Key size={20} color="#FAECEC" />,
      title: "Encrypted API Keys",
      description: "Military-grade encryption protects your exchange API keys"
    },
    {
      icon: <Eye size={20} color="#FAECEC" />,
      title: "Read-Only Access",
      description: "We can only read your data, never withdraw or transfer funds"
    },
    {
      icon: <Lock size={20} color="#FAECEC" />,
      title: "Secure Infrastructure",
      description: "Enterprise-level security with regular audits and monitoring"
    },
    {
      icon: <Shield size={20} color="#FAECEC" />,
      title: "Your Control",
      description: "You maintain full control over your funds at all times"
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
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
    <SectionContainer id="security">
      <Container>
        <ContentWrapper>
          <TextContent>
            <SectionTitle
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              Your Keys. Your Funds. Your Control.
            </SectionTitle>
            
            <SectionSubtitle
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              viewport={{ once: true }}
            >
              We never store or access your funds. All API keys are encrypted and managed securely — you stay in control.
            </SectionSubtitle>

            <motion.div
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <SecurityFeatures>
                {securityFeatures.map((feature, index) => (
                  <SecurityFeature key={index} variants={itemVariants}>
                    <FeatureIcon>
                      {feature.icon}
                    </FeatureIcon>
                    <FeatureText>
                      <FeatureTitle>{feature.title}</FeatureTitle>
                      <FeatureDescription>{feature.description}</FeatureDescription>
                    </FeatureText>
                  </SecurityFeature>
                ))}
              </SecurityFeatures>
            </motion.div>
          </TextContent>

          <VisualContent>
            <SecurityVisual>
              <CentralIcon>
                <Shield size={50} color="#FAECEC" />
              </CentralIcon>
              
              <OrbitingElements>
                <OrbitElement>
                  <Key size={16} color="#FAECEC" />
                </OrbitElement>
                <OrbitElement>
                  <Lock size={16} color="#FAECEC" />
                </OrbitElement>
                <OrbitElement>
                  <Eye size={16} color="#FAECEC" />
                </OrbitElement>
                <OrbitElement>
                  <Shield size={16} color="#FAECEC" />
                </OrbitElement>
              </OrbitingElements>
            </SecurityVisual>
          </VisualContent>
        </ContentWrapper>
      </Container>
    </SectionContainer>
  );
};

export default SecuritySection;