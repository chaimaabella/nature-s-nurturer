import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { MessageCircle, Sparkles } from "lucide-react";
import heroImage from "@/assets/hero-plants.jpg";

interface HeroSectionProps {
  title?: string;
  subtitle?: string;
  ctaText?: string;
}

export function HeroSection({
  title = "Votre assistant intelligent pour entretenir vos plantes",
  subtitle = "Posez vos questions, obtenez des conseils personnalisés et créez des plans d'entretien adaptés à chaque plante de votre collection.",
  ctaText = "Posez une question",
}: HeroSectionProps) {
  return (
    <section className="relative min-h-[85vh] flex items-center nature-gradient overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/4 -right-1/4 w-1/2 h-1/2 bg-nature-sage/20 rounded-full blur-3xl" />
        <div className="absolute -bottom-1/4 -left-1/4 w-1/2 h-1/2 bg-accent/30 rounded-full blur-3xl" />
      </div>

      <div className="container relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div className="space-y-8 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/50 text-accent-foreground text-sm font-medium animate-fade-in">
              <Sparkles className="h-4 w-4" />
              Assistant IA pour vos plantes
            </div>
            
            <h1 
              className="font-display text-4xl md:text-5xl lg:text-6xl font-bold text-foreground leading-tight text-balance animate-slide-up"
              style={{ animationDelay: "0.1s" }}
            >
              {title}
            </h1>
            
            <p 
              className="text-lg md:text-xl text-muted-foreground max-w-xl mx-auto lg:mx-0 animate-slide-up"
              style={{ animationDelay: "0.2s" }}
            >
              {subtitle}
            </p>

            <div 
              className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start animate-slide-up"
              style={{ animationDelay: "0.3s" }}
            >
              <Link to="/chat">
                <Button variant="hero" size="xl" className="w-full sm:w-auto">
                  <MessageCircle className="h-5 w-5" />
                  {ctaText}
                </Button>
              </Link>
              <a href="#how-it-works">
                <Button variant="outline" size="xl" className="w-full sm:w-auto">
                  Découvrir comment ça marche
                </Button>
              </a>
            </div>
          </div>

          {/* Image */}
          <div 
            className="relative animate-slide-up lg:block"
            style={{ animationDelay: "0.4s" }}
          >
            <div className="relative rounded-2xl overflow-hidden shadow-nature-elevated">
              <img
                src={heroImage}
                alt="Collection de plantes d'intérieur"
                className="w-full h-auto object-cover animate-float"
                style={{ animationDuration: "6s" }}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-background/20 to-transparent" />
            </div>
            
            {/* Floating card */}
            <div className="absolute -bottom-6 -left-6 p-4 bg-card rounded-xl shadow-nature-card border border-border animate-fade-in hidden md:block" style={{ animationDelay: "0.6s" }}>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center">
                  <MessageCircle className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">+2,500</p>
                  <p className="text-xs text-muted-foreground">Questions répondues</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
