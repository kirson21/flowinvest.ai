import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import { Bot, Shield, TrendingUp, Settings, Star, Globe } from 'lucide-react';

const SectionContainer = styled.section`
  padding: 120px 0;
  background: linear-gradient(180deg, #474545 0%, #3a3838 100%);
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

const FeaturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 40px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 30px;
  }
`;

const FeatureCard = styled(motion.div)`
  background: linear-gradient(135deg, rgba(0, 151, 178, 0.1) 0%, rgba(250, 236, 236, 0.05) 100%);
  border: 1px solid rgba(0, 151, 178, 0.2);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;

  &:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0, 151, 178, 0.2);
    border-color: rgba(0, 151, 178, 0.4);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #0097B2 0%, #007a94 100%);
  }

  /* Montek-style hover gradient overlay */
  &::after {
    content: '';
    position: absolute;
    left: -1px;
    top: -1px;
    right: -1px;
    bottom: -1px;
    opacity: 0;
    transform: scale(1, 0.2);
    transition: all 500ms ease;
    background: linear-gradient(to top, #0097B2 0%, #FAECEC 100%);
    z-index: -1;
    border-radius: 20px;
  }

  &:hover::after {
    opacity: 0.1;
    transform: scale(1, 1);
  }
`;

const IconWrapper = styled.div`
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  box-shadow: 0 8px 25px rgba(0, 151, 178, 0.3);
`;

const FeatureTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: 600;
  color: #FAECEC;
  margin-bottom: 16px;
`;

const FeatureDescription = styled.p`
  color: #FAECEC;
  opacity: 0.8;
  line-height: 1.6;
  font-size: 1rem;
`;

const Badge = styled.span`
  position: absolute;
  top: 20px;
  right: 20px;
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  color: #FAECEC;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
`;

const FeaturesSection = () => {
  const features = [
    {
      icon: <Bot size={32} color="#FAECEC" />,
      title: "AI Bot Constructor with GPT-5",
      description: "Revolutionary AI-powered bot creation using the latest GPT-5 technology. Create sophisticated trading strategies in minutes, not hours.",
      badge: "NEW"
    },
    {
      icon: <Shield size={32} color="#FAECEC" />,
      title: "Secure API Key Management",
      description: "Bank-level encryption for your exchange API keys. We never store your funds or have withdrawal access - you stay in complete control.",
      badge: null
    },
    {
      icon: <TrendingUp size={32} color="#FAECEC" />,
      title: "AI Smart Feed with Market Scores",
      description: "Real-time market analysis with AI-generated score ratings. Get instant insights on market conditions and trading opportunities.",
      badge: null
    },
    {
      icon: <Settings size={32} color="#FAECEC" />,
      title: "Manual Bot Settings for Pros",
      description: "Advanced users can fine-tune every parameter. Complete control over order types, risk management, and execution strategies.",
      badge: null
    },
    {
      icon: <Star size={32} color="#FAECEC" />,
      title: "Marketplace with Reviews & Ratings",
      description: "Browse verified trading strategies from successful traders. Community ratings and detailed performance metrics help you choose wisely.",
      badge: null
    },
    {
      icon: <Globe size={32} color="#FAECEC" />,
      title: "Multi-Exchange Support",
      description: "Currently supporting Bybit, with Binance, Crypto.com, and OKX integration coming soon. Trade across multiple platforms seamlessly.",
      badge: "EXPANDING"
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
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.8,
        ease: "easeOut"
      }
    }
  };

  return (
    <SectionContainer id="features">
      <Container>
        <SectionHeader>
          <SectionTitle
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            Powerful Features
          </SectionTitle>
        </SectionHeader>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <FeaturesGrid>
            {features.map((feature, index) => (
              <FeatureCard
                key={index}
                variants={itemVariants}
                whileHover={{ scale: 1.02 }}
              >
                {feature.badge && <Badge>{feature.badge}</Badge>}
                <IconWrapper>
                  {feature.icon}
                </IconWrapper>
                <FeatureTitle>{feature.title}</FeatureTitle>
                <FeatureDescription>{feature.description}</FeatureDescription>
              </FeatureCard>
            ))}
          </FeaturesGrid>
        </motion.div>
      </Container>
    </SectionContainer>
  );
};

export default FeaturesSection;