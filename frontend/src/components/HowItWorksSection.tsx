import { MessageCircle, ClipboardList, Heart } from "lucide-react";

const steps = [
  {
    icon: MessageCircle,
    title: "Posez une question",
    description: "Décrivez votre plante ou votre problème. Notre assistant comprend le langage naturel.",
  },
  {
    icon: ClipboardList,
    title: "Obtenez un plan d'action",
    description: "Recevez des conseils structurés et un calendrier d'entretien personnalisé.",
  },
  {
    icon: Heart,
    title: "Suivez les conseils",
    description: "Appliquez les recommandations et regardez vos plantes s'épanouir.",
  },
];

interface HowItWorksSectionProps {
  title?: string;
  subtitle?: string;
}

export function HowItWorksSection({
  title = "Comment ça marche",
  subtitle = "Trois étapes simples pour des plantes en pleine santé",
}: HowItWorksSectionProps) {
  return (
    <section id="how-it-works" className="py-20 md:py-28 bg-background">
      <div className="container">
        {/* Header */}
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
            {title}
          </h2>
          <p className="text-lg text-muted-foreground">
            {subtitle}
          </p>
        </div>

        {/* Steps */}
        <div className="grid md:grid-cols-3 gap-8 md:gap-12">
          {steps.map((step, index) => (
            <div
              key={step.title}
              className="relative group"
            >
              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-12 left-[60%] w-[80%] h-0.5 bg-gradient-to-r from-border to-transparent" />
              )}

              <div className="text-center space-y-4">
                {/* Icon */}
                <div className="relative inline-flex">
                  <div className="h-24 w-24 rounded-2xl bg-accent flex items-center justify-center transition-transform group-hover:scale-105 shadow-nature">
                    <step.icon className="h-10 w-10 text-primary" />
                  </div>
                  <span className="absolute -top-2 -right-2 h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold">
                    {index + 1}
                  </span>
                </div>

                {/* Content */}
                <h3 className="font-display text-xl font-semibold text-foreground">
                  {step.title}
                </h3>
                <p className="text-muted-foreground max-w-xs mx-auto">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
