import { Bot, CalendarDays, Stethoscope, Lightbulb, Droplets, Sun } from "lucide-react";

const features = [
  {
    icon: Bot,
    title: "Chatbot IA intelligent",
    description: "Posez n'importe quelle question sur vos plantes et recevez une réponse instantanée.",
  },
  {
    icon: CalendarDays,
    title: "Plans d'entretien",
    description: "Obtenez des calendriers d'arrosage et de soins adaptés à chaque plante.",
  },
  {
    icon: Stethoscope,
    title: "Diagnostic guidé",
    description: "Identifiez les problèmes de vos plantes grâce à un diagnostic interactif.",
  },
  {
    icon: Lightbulb,
    title: "Conseils personnalisés",
    description: "Des recommandations basées sur votre environnement et niveau d'expérience.",
  },
  {
    icon: Droplets,
    title: "Rappels d'arrosage",
    description: "Ne manquez plus jamais un arrosage avec nos suggestions de fréquence.",
  },
  {
    icon: Sun,
    title: "Guide lumière",
    description: "Apprenez où placer vos plantes selon leurs besoins en luminosité.",
  },
];

interface FeaturesSectionProps {
  title?: string;
  subtitle?: string;
}

export function FeaturesSection({
  title = "Fonctionnalités clés",
  subtitle = "Tout ce dont vous avez besoin pour des plantes en pleine santé",
}: FeaturesSectionProps) {
  return (
    <section id="features" className="py-20 md:py-28 bg-card">
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

        {/* Features Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group p-6 md:p-8 rounded-2xl bg-background border border-border shadow-nature hover:shadow-nature-card transition-all duration-300 hover:-translate-y-1"
            >
              <div className="h-14 w-14 rounded-xl bg-accent flex items-center justify-center mb-5 transition-colors group-hover:bg-primary">
                <feature.icon className="h-7 w-7 text-primary group-hover:text-primary-foreground transition-colors" />
              </div>
              
              <h3 className="font-display text-xl font-semibold text-foreground mb-2">
                {feature.title}
              </h3>
              <p className="text-muted-foreground">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
