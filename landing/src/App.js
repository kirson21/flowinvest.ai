import React from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import WhySection from './components/WhySection';
import HowItWorksSection from './components/HowItWorksSection';
import FeaturesSection from './components/FeaturesSection';
import MarketplaceSection from './components/MarketplaceSection';
import SecuritySection from './components/SecuritySection';
import CTASection from './components/CTASection';
import Footer from './components/Footer';

function App() {
  return (
    <div className="App">
      <Header />
      <HeroSection />
      <WhySection />
      <HowItWorksSection />
      <FeaturesSection />
      <MarketplaceSection />
      <SecuritySection />
      <CTASection />
      <Footer />
    </div>
  );
}

export default App;