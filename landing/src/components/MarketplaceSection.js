import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import { Star } from 'lucide-react';

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

const MarketplacePreview = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 60px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const BotCard = styled(motion.div)`
  background: linear-gradient(135deg, rgba(0, 151, 178, 0.1) 0%, rgba(250, 236, 236, 0.05) 100%);
  border: 1px solid rgba(0, 151, 178, 0.2);
  border-radius: 20px;
  padding: 30px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0, 151, 178, 0.2);
    border-color: rgba(0, 151, 178, 0.4);
  }
`;

const BotHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
`;

const BotAvatar = styled.div`
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  color: #FAECEC;
  box-shadow: 0 4px 15px rgba(0, 151, 178, 0.3);
`;

const RatingBadge = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(0, 151, 178, 0.2);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #FAECEC;
`;

const BotName = styled.h3`
  font-size: 1.3rem;
  font-weight: 600;
  color: #FAECEC;
  margin-bottom: 8px;
`;

const BotStrategy = styled.p`
  color: #0097B2;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 16px;
`;

const BotStats = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
`;

const StatItem = styled.div`
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 1.2rem;
  font-weight: 600;
  color: #0097B2;
`;

const StatLabel = styled.div`
  font-size: 0.8rem;
  color: #FAECEC;
  opacity: 0.7;
`;

const ViewButton = styled.button`
  width: 100%;
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  color: #FAECEC;
  border: none;
  padding: 12px;
  border-radius: 10px;
  font-family: 'Comfortaa', sans-serif;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 151, 178, 0.3);
  }
`;

const CTAContainer = styled.div`
  text-align: center;
`;

const CTAButton = styled(motion.button)`
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
  margin-right: 20px;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(0, 151, 178, 0.4);
  }

  @media (max-width: 768px) {
    margin-right: 0;
    margin-bottom: 20px;
    width: 100%;
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

  @media (max-width: 768px) {
    width: 100%;
  }
`;

const MarketplaceSection = () => {
  const sampleBots = [
    {
      name: "Crypto Scalper Pro",
      strategy: "High-Frequency Scalping",
      avatar: "CS",
      rating: 4.8,
      profit: "+342%",
      users: "1.2k"
    },
    {
      name: "DCA Master",
      strategy: "Dollar Cost Averaging",
      avatar: "DM",
      rating: 4.9,
      profit: "+186%",
      users: "2.8k"
    },
    {
      name: "Trend Follower",
      strategy: "Momentum Trading",
      avatar: "TF",
      rating: 4.7,
      profit: "+298%",
      users: "956"
    }
  ];

  const handleExploreMarketplace = () => {
    window.open('https://app.f01i.ai', '_blank');
  };

  const handleGetStarted = () => {
    window.open('https://app.f01i.ai', '_blank');
  };

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
    <SectionContainer id="marketplace">
      <Container>
        <SectionHeader>
          <SectionTitle
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            A Trading Strategy for Every Investor
          </SectionTitle>
          
          <SectionSubtitle
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            viewport={{ once: true }}
          >
            Browse, compare, and choose bots from verified traders. Check their ratings, reviews, and performance history before you invest.
          </SectionSubtitle>
        </SectionHeader>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <MarketplacePreview>
            {sampleBots.map((bot, index) => (
              <BotCard key={index} variants={itemVariants} whileHover={{ scale: 1.02 }}>
                <BotHeader>
                  <BotAvatar>{bot.avatar}</BotAvatar>
                  <RatingBadge>
                    <Star size={14} fill="#0097B2" color="#0097B2" />
                    {bot.rating}
                  </RatingBadge>
                </BotHeader>
                
                <BotName>{bot.name}</BotName>
                <BotStrategy>{bot.strategy}</BotStrategy>
                
                <BotStats>
                  <StatItem>
                    <StatValue>{bot.profit}</StatValue>
                    <StatLabel>Total Profit</StatLabel>
                  </StatItem>
                  <StatItem>
                    <StatValue>{bot.users}</StatValue>
                    <StatLabel>Active Users</StatLabel>
                  </StatItem>
                </BotStats>
                
                <ViewButton onClick={handleExploreMarketplace}>
                  View Details
                </ViewButton>
              </BotCard>
            ))}
          </MarketplacePreview>
        </motion.div>

        <CTAContainer>
          <CTAButton
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleGetStarted}
          >
            Get Started
          </CTAButton>
          
          <SecondaryButton
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleExploreMarketplace}
          >
            Explore Marketplace
          </SecondaryButton>
        </CTAContainer>
      </Container>
    </SectionContainer>
  );
};

export default MarketplaceSection;