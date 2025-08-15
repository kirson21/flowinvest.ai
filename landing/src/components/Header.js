import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';

const HeaderContainer = styled(motion.header)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 20px 0;
  background: rgba(71, 69, 69, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 151, 178, 0.1);
  transition: all 0.3s ease;

  &.scrolled {
    padding: 15px 0;
    background: rgba(71, 69, 69, 0.98);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }
`;

const Nav = styled.nav`
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
`;

const Logo = styled(motion.div)`
  font-size: 28px;
  font-weight: 700;
  color: #0097B2;
  cursor: pointer;
`;

const NavLinks = styled.div`
  display: flex;
  gap: 40px;
  align-items: center;

  @media (max-width: 768px) {
    display: none;
  }
`;

const NavLink = styled(motion.a)`
  color: #FAECEC;
  font-weight: 500;
  font-size: 16px;
  cursor: pointer;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 0;
    height: 2px;
    background: #0097B2;
    transition: width 0.3s ease;
  }

  &:hover::after {
    width: 100%;
  }
`;

const CTAButton = styled(motion.a)`
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  color: #FAECEC;
  border: none;
  padding: 12px 24px;
  border-radius: 50px;
  font-family: 'Comfortaa', sans-serif;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 151, 178, 0.3);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 151, 178, 0.4);
    color: #FAECEC;
  }

  @media (max-width: 768px) {
    display: none;
  }
`;

const MobileMenu = styled(motion.div)`
  position: fixed;
  top: 80px;
  left: 0;
  right: 0;
  background: rgba(71, 69, 69, 0.98);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 151, 178, 0.1);
  padding: 20px;
  z-index: 1001;
  display: none;

  @media (max-width: 768px) {
    display: block;
  }

  &.mobile-menu-hidden {
    display: none;
  }

  &.mobile-menu-visible {
    display: block;
  }
`;

const MobileNavLink = styled(motion.div)`
  color: #FAECEC;
  font-weight: 500;
  font-size: 18px;
  cursor: pointer;
  padding: 15px 0;
  border-bottom: 1px solid rgba(0, 151, 178, 0.1);
  
  &:last-child {
    border-bottom: none;
  }

  &:hover {
    color: #0097B2;
  }
`;

const MobileCTAButton = styled(motion.a)`
  background: linear-gradient(135deg, #0097B2 0%, #007a94 100%);
  color: #FAECEC;
  border: none;
  padding: 15px 30px;
  border-radius: 50px;
  font-family: 'Comfortaa', sans-serif;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 151, 178, 0.3);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
  width: 100%;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 151, 178, 0.4);
    color: #FAECEC;
  }
`;

const MobileMenuButton = styled(motion.button)`
  display: none;
  background: none;
  border: none;
  color: #FAECEC;
  font-size: 24px;
  cursor: pointer;

  @media (max-width: 768px) {
    display: block;
  }
`;

const Header = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMobileMenuOpen(false); // Close mobile menu after navigation
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <HeaderContainer
      className={isScrolled ? 'scrolled' : ''}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      <Nav>
        <Logo
          whileHover={{ scale: 1.05 }}
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        >
          f01i.ai
        </Logo>
        
        <NavLinks>
          <NavLink
            whileHover={{ y: -2 }}
            onClick={() => scrollToSection('why')}
          >
            Why f01i.ai
          </NavLink>
          <NavLink
            whileHover={{ y: -2 }}
            onClick={() => scrollToSection('how-it-works')}
          >
            How It Works
          </NavLink>
          <NavLink
            whileHover={{ y: -2 }}
            onClick={() => scrollToSection('features')}
          >
            Features
          </NavLink>
          <NavLink
            whileHover={{ y: -2 }}
            onClick={() => scrollToSection('marketplace')}
          >
            Marketplace
          </NavLink>
        </NavLinks>

        <CTAButton
          as="a"
          href="https://f01i.app/login"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Get Started Free
        </CTAButton>

        <MobileMenuButton whileTap={{ scale: 0.95 }} onClick={toggleMobileMenu}>
          {isMobileMenuOpen ? '✕' : '☰'}
        </MobileMenuButton>
      </Nav>

      <MobileMenu 
        isOpen={isMobileMenuOpen}
        initial={{ opacity: 0, y: -20 }}
        animate={{ 
          opacity: isMobileMenuOpen ? 1 : 0, 
          y: isMobileMenuOpen ? 0 : -20 
        }}
        transition={{ duration: 0.3 }}
      >
        <MobileNavLink
          whileTap={{ scale: 0.95 }}
          onClick={() => scrollToSection('why')}
        >
          Why f01i.ai
        </MobileNavLink>
        <MobileNavLink
          whileTap={{ scale: 0.95 }}
          onClick={() => scrollToSection('how-it-works')}
        >
          How It Works
        </MobileNavLink>
        <MobileNavLink
          whileTap={{ scale: 0.95 }}
          onClick={() => scrollToSection('features')}
        >
          Features
        </MobileNavLink>
        <MobileNavLink
          whileTap={{ scale: 0.95 }}
          onClick={() => scrollToSection('marketplace')}
        >
          Marketplace
        </MobileNavLink>
        
        <MobileCTAButton
          as="a"
          href="https://f01i.app/login"
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsMobileMenuOpen(false)}
        >
          Get Started Free
        </MobileCTAButton>
      </MobileMenu>
    </HeaderContainer>
  );
};

export default Header;