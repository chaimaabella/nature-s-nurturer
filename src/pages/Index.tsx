import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { HeroSection } from "@/components/HeroSection";
import { HowItWorksSection } from "@/components/HowItWorksSection";
import { FeaturesSection } from "@/components/FeaturesSection";
import { ExamplesSection } from "@/components/ExamplesSection";
import { AboutSection } from "@/components/AboutSection";
import { ChatWidget } from "@/components/ChatWidget";

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1">
        <HeroSection />
        <HowItWorksSection />
        <FeaturesSection />
        <ExamplesSection />
        <AboutSection />
      </main>

      <Footer />
      <ChatWidget />
    </div>
  );
};

export default Index;
