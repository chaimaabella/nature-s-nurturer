import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export default function MentionsLegales() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        <section className="container py-12 md:py-16 space-y-10">
          <header className="space-y-3">
            <h1 className="font-display text-3xl md:text-4xl font-bold text-foreground">
              Mentions légales
            </h1>
            <p className="text-muted-foreground max-w-2xl">
              Floria est un projet d&apos;école réalisé dans le cadre d&apos;EPITECH
              Marseille. Les informations ci-dessous sont fournies à titre indicatif
              pour une présentation complète du projet.
            </p>
          </header>

          <div className="space-y-8 text-foreground">
            <section className="space-y-3">
              <h2 className="text-xl font-semibold">Éditeur du site</h2>
              <p className="text-muted-foreground">
                Floria — projet pédagogique porté par des étudiants d&apos;EPITECH
                Marseille.
              </p>
              <ul className="text-muted-foreground space-y-1">
                <li>Adresse : 270 Avenue de Mazargues, 13008 Marseille</li>
                <li>Contact : contact@floria.app</li>
              </ul>
            </section>

            <section className="space-y-3">
              <h2 className="text-xl font-semibold">Responsable de publication</h2>
              <p className="text-muted-foreground">
                L&apos;équipe pédagogique Floria (EPITECH Marseille).
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-xl font-semibold">Hébergement</h2>
              <p className="text-muted-foreground">
                Hébergeur : à préciser lors de la mise en production. En phase de
                démonstration, le site peut être hébergé sur une infrastructure de
                test interne.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-xl font-semibold">Propriété intellectuelle</h2>
              <p className="text-muted-foreground">
                Les contenus (textes, visuels, interfaces) sont créés dans le cadre
                du projet Floria. Toute reproduction ou réutilisation sans
                autorisation préalable est interdite.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-xl font-semibold">Crédits</h2>
              <p className="text-muted-foreground">
                Icônes et composants d&apos;interface issus de bibliothèques
                open-source, utilisés conformément à leurs licences respectives.
              </p>
            </section>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
