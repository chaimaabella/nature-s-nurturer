import { Leaf, Target, Heart } from "lucide-react";

const values = [
  {
    icon: Leaf,
    title: "Écologique",
    description: "Nous promouvons des méthodes de jardinage respectueuses de l'environnement.",
  },
  {
    icon: Target,
    title: "Précis",
    description: "Des conseils basés sur des recherches botaniques et l'expertise horticole.",
  },
  {
    icon: Heart,
    title: "Accessible",
    description: "Un langage simple pour que tout le monde puisse prendre soin de ses plantes.",
  },
];

interface AboutSectionProps {
  title?: string;
  description?: string;
}

export function AboutSection({
  title = "Notre mission",
  description = "Flore est né d'une passion simple : rendre le soin des plantes accessible à tous. Notre assistant IA combine les dernières avancées en intelligence artificielle avec des connaissances botaniques approfondies pour vous accompagner dans votre aventure végétale.",
}: AboutSectionProps) {
  return (
    <section id="about" className="py-20 md:py-28 bg-accent/30">
      <div className="container">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-6">
              {title}
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              {description}
            </p>
          </div>

          {/* Values */}
          <div className="grid md:grid-cols-3 gap-8">
            {values.map((value) => (
              <div
                key={value.title}
                className="text-center"
              >
                <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 mb-4">
                  <value.icon className="h-8 w-8 text-primary" />
                </div>
                <h3 className="font-display text-xl font-semibold text-foreground mb-2">
                  {value.title}
                </h3>
                <p className="text-muted-foreground">
                  {value.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
