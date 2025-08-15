import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import { TrendingUp, Bot, Award } from 'lucide-react';

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

const SectionSubtitle = styled(motion.p)`
  font-size: 1.25rem;
  color: #FAECEC;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;

  @media (max-width: 768px) {
    font-size: 1.1rem;
  }
`;

const BenefitsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 40px;
  margin-top: 60px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 30px;
  }
`;

const BenefitCard = styled(motion.div)`
  background: linear-gradient(135deg, rgba(0, 151, 178, 0.1) 0%, rgba(250, 236, 236, 0.05) 100%);
  border: 1px solid rgba(0, 151, 178, 0.2);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  backdrop-filter: blur(10px);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(0, 151, 178, 0.2) 0%, rgba(250, 236, 236, 0.1) 100%);
    transition: left 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: -1;
  }

  &:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0, 151, 178, 0.3);
    border-color: rgba(0, 151, 178, 0.6);
    background: linear-gradient(135deg, rgba(0, 151, 178, 0.15) 0%, rgba(250, 236, 236, 0.1) 100%);
  }

  &:hover::before {
    left: 0%;
  }

  &:nth-child(1):hover {
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.15) 0%, rgba(0, 151, 178, 0.1) 100%);
    border-color: rgba(255, 107, 107, 0.4);
    box-shadow: 0 20px 40px rgba(255, 107, 107, 0.2);
  }

  &:nth-child(2):hover {
    background: linear-gradient(135deg, rgba(72, 187, 120, 0.15) 0%, rgba(0, 151, 178, 0.1) 100%);
    border-color: rgba(72, 187, 120, 0.4);
    box-shadow: 0 20px 40px rgba(72, 187, 120, 0.2);
  }

  &:nth-child(3):hover {
    background: linear-gradient(135deg, rgba(126, 58, 242, 0.15) 0%, rgba(0, 151, 178, 0.1) 100%);
    border-color: rgba(126, 58, 242, 0.4);
    box-shadow: 0 20px 40px rgba(126, 58, 242, 0.2);
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

const BenefitTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: 600;
  color: #FAECEC;
  margin-bottom: 16px;
`;

const BenefitDescription = styled.p`
  color: #FAECEC;
  opacity: 0.8;
  line-height: 1.6;
  font-size: 1rem;
`;

const WhySection = () => {
  const benefits = [
    {
      icon: <TrendingUp size={32} color="#FAECEC" />,
      title: "AI Smart Feed",
      description: "Get real-time market insights with clear score ratings. Our AI analyzes thousands of data points to give you actionable intelligence."
    },
    {
      icon: <Bot size={32} color="#FAECEC" />,
      title: "Custom AI Trading Bots",
      description: "Design your personal money-making machine. Build with GPT-5 in minutes or fine-tune every detail manually."
    },
    {
      icon: <Award size={32} color="#FAECEC" />,
      title: "Verified Marketplace",
      description: "Explore and invest in strategies proven by real traders. Only verified and rated products make it here."
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.3
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
    <SectionContainer id="why">
      <Container>
        <SectionHeader>
          <SectionTitle
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            Because Everyone Deserves Financial Freedom
          </SectionTitle>
          
          <SectionSubtitle
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            viewport={{ once: true }}
          >
            You don't need Wall Street connections or years of trading experience. With f01i.ai, the power of AI trading is in your hands — easy to use, fully automated, and built to generate results.
          </SectionSubtitle>
        </SectionHeader>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <BenefitsGrid>
            {benefits.map((benefit, index) => (
              <BenefitCard
                key={index}
                variants={itemVariants}
                whileHover={{ scale: 1.02 }}
              >
                <IconWrapper>
                  {benefit.icon}
                </IconWrapper>
                <BenefitTitle>{benefit.title}</BenefitTitle>
                <BenefitDescription>{benefit.description}</BenefitDescription>
              </BenefitCard>
            ))}
          </BenefitsGrid>
        </motion.div>
      </Container>
    </SectionContainer>
  );
};

export default WhySection;