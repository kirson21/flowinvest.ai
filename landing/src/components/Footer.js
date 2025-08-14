import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import { Twitter, Github, Linkedin, Mail } from 'lucide-react';

const FooterContainer = styled.footer`
  background: linear-gradient(180deg, #474545 0%, #2d2b2b 100%);
  padding: 60px 0 30px;
  border-top: 1px solid rgba(0, 151, 178, 0.1);
`;

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
`;

const FooterContent = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 60px;
  margin-bottom: 40px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
  }
`;

const BrandSection = styled.div``;

const Logo = styled.h3`
  font-size: 2rem;
  font-weight: 700;
  color: #0097B2;
  margin-bottom: 16px;
`;

const BrandDescription = styled.p`
  color: #FAECEC;
  opacity: 0.8;
  line-height: 1.6;
  margin-bottom: 24px;
`;

const SocialLinks = styled.div`
  display: flex;
  gap: 16px;

  @media (max-width: 768px) {
    justify-content: center;
  }
`;

const SocialLink = styled(motion.a)`
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, rgba(0, 151, 178, 0.2) 0%, rgba(250, 236, 236, 0.1) 100%);
  border: 1px solid rgba(0, 151, 178, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;

  &:hover {
    background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 151, 178, 0.3);
  }
`;

const FooterSection = styled.div``;

const SectionTitle = styled.h4`
  font-size: 1.1rem;
  font-weight: 600;
  color: #FAECEC;
  margin-bottom: 20px;
`;

const FooterLink = styled(motion.a)`
  display: block;
  color: #FAECEC;
  opacity: 0.8;
  text-decoration: none;
  margin-bottom: 12px;
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    opacity: 1;
    color: #0097B2;
    transform: translateX(5px);
  }
`;

const FooterBottom = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 30px;
  border-top: 1px solid rgba(0, 151, 178, 0.1);

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
`;

const Copyright = styled.p`
  color: #FAECEC;
  opacity: 0.6;
  font-size: 0.9rem;
`;

const LegalLinks = styled.div`
  display: flex;
  gap: 24px;

  @media (max-width: 768px) {
    flex-wrap: wrap;
    justify-content: center;
  }
`;

const LegalLink = styled.a`
  color: #FAECEC;
  opacity: 0.6;
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.3s ease;

  &:hover {
    opacity: 1;
    color: #0097B2;
  }
`;

const Footer = () => {
  const handleLinkClick = (section) => {
    if (section === 'app') {
      window.location.href = '/login';
    } else {
      const element = document.getElementById(section);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  return (
    <FooterContainer>
      <Container>
        <FooterContent>
          <BrandSection>
            <Logo>f01i.ai</Logo>
            <BrandDescription>
              Future-Oriented Life & Investments AI Tools. Empowering everyone to achieve financial freedom through intelligent automation and AI-powered trading strategies.
            </BrandDescription>
            <SocialLinks>
              <SocialLink
                href="#"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Twitter size={18} color="#FAECEC" />
              </SocialLink>
              <SocialLink
                href="#"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Github size={18} color="#FAECEC" />
              </SocialLink>
              <SocialLink
                href="#"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Linkedin size={18} color="#FAECEC" />
              </SocialLink>
              <SocialLink
                href="#"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Mail size={18} color="#FAECEC" />
              </SocialLink>
            </SocialLinks>
          </BrandSection>

          <FooterSection>
            <SectionTitle>Platform</SectionTitle>
            <FooterLink
              whileHover={{ x: 5 }}
              onClick={() => handleLinkClick('why')}
            >
              Why f01i.ai
            </FooterLink>
            <FooterLink
              whileHover={{ x: 5 }}
              onClick={() => handleLinkClick('how-it-works')}
            >
              How It Works
            </FooterLink>
            <FooterLink
              whileHover={{ x: 5 }}
              onClick={() => handleLinkClick('features')}
            >
              Features
            </FooterLink>
            <FooterLink
              whileHover={{ x: 5 }}
              onClick={() => handleLinkClick('marketplace')}
            >
              Marketplace
            </FooterLink>
          </FooterSection>

          <FooterSection>
            <SectionTitle>Resources</SectionTitle>
            <FooterLink whileHover={{ x: 5 }}>Documentation</FooterLink>
            <FooterLink whileHover={{ x: 5 }}>API Reference</FooterLink>
            <FooterLink whileHover={{ x: 5 }}>Tutorials</FooterLink>
            <FooterLink whileHover={{ x: 5 }}>Community</FooterLink>
          </FooterSection>

          <FooterSection>
            <SectionTitle>Company</SectionTitle>
            <FooterLink whileHover={{ x: 5 }}>About Us</FooterLink>
            <FooterLink whileHover={{ x: 5 }}>Careers</FooterLink>
            <FooterLink whileHover={{ x: 5 }}>Contact</FooterLink>
            <FooterLink
              whileHover={{ x: 5 }}
              onClick={() => handleLinkClick('app')}
            >
              Launch App
            </FooterLink>
          </FooterSection>
        </FooterContent>

        <FooterBottom>
          <Copyright>
            © 2025 f01i.ai. All rights reserved.
          </Copyright>
          
          <LegalLinks>
            <LegalLink href="#">Privacy Policy</LegalLink>
            <LegalLink href="#">Terms of Service</LegalLink>
            <LegalLink href="#">Cookie Policy</LegalLink>
          </LegalLinks>
        </FooterBottom>
      </Container>
    </FooterContainer>
  );
};

export default Footer;