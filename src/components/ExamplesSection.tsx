import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

const examples = [
  "Pourquoi les feuilles de mon monstera jaunissent-elles ?",
  "Quelle est la fréquence d'arrosage idéale pour un cactus ?",
  "Comment savoir si ma plante manque de lumière ?",
  "Quels sont les meilleurs engrais naturels pour plantes d'intérieur ?",
  "Comment bouturer un pothos facilement ?",
  "Ma plante a des taches brunes, que faire ?",
];

interface ExamplesSectionProps {
  title?: string;
  subtitle?: string;
}

export function ExamplesSection({
  title = "Exemples de questions",
  subtitle = "Voici quelques exemples de ce que vous pouvez demander à Floria",
}: ExamplesSectionProps) {
  return (
    <section className="py-20 md:py-28 bg-background">
      <div className="container">
        {/* Header */}
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
            {title}
          </h2>
          <p className="text-lg text-muted-foreground">
            {subtitle}
          </p>
        </div>

        {/* Examples Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto mb-12">
          {examples.map((example, index) => (
            <Link
              key={index}
              to={`/chat?q=${encodeURIComponent(example)}`}
              className="group p-5 rounded-xl bg-card border border-border hover:border-primary/50 hover:shadow-nature-card transition-all duration-300"
            >
              <p className="text-foreground group-hover:text-primary transition-colors">
                "{example}"
              </p>
              <ArrowRight className="h-4 w-4 mt-3 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
            </Link>
          ))}
        </div>

        {/* CTA */}
        <div className="text-center">
          <Link to="/chat">
            <Button variant="hero" size="lg">
              Posez votre première question
              <ArrowRight className="h-5 w-5" />
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}
