import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export default function Confidentialite() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        <section className="container py-12 md:py-16 space-y-10">
          <header className="space-y-3">
            <h1 className="font-display text-3xl md:text-4xl font-bold text-foreground">
              Politique de confidentialité
            </h1>
            <p className="text-muted-foreground max-w-2xl">
              Floria est un projet d&apos;école mené à EPITECH Marseille. Cette
              politique explique comment les données sont traitées dans le cadre
              du prototype et des démonstrations.
            </p>
          </header>

          <div className="space-y-8 text-foreground">
            <section className="space-y-3">
              <h2 className="text-xl font-semibold">Données collectées</h2>
              <p className="text-muted-foreground">
                Le site ne collecte pas de données personnelles sensibles. Les
                informations partagées dans le chatbot sont utilisées uniquement
                pour répondre aux questions et ne sont pas revendues.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-xl font-semibold">Finalités du traitement</h2>
              <p className="text-muted-foreground">
                Les données sont utilisées pour améliorer l&apos;expérience
                utilisateur, analyser les besoins des visiteurs et présenter un
                prototype cohérent dans un contexte pédagogique.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-xl font-semibold">Durée de conservation</h2>
              <p className="text-muted-foreground">
                Les données issues des démonstrations sont conservées pour une
                durée limitée, nécessaire à l&apos;évaluation du projet. Elles sont
                ensuite supprimées ou anonymisées.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-xl font-semibold">Cookies</h2>
              <p className="text-muted-foreground">
                Floria n&apos;utilise pas de cookies publicitaires. Seuls des cookies
                techniques peuvent être nécessaires au bon fonctionnement du
                site.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-xl font-semibold">Vos droits</h2>
              <p className="text-muted-foreground">
                Vous pouvez demander l&apos;accès, la rectification ou la suppression
                de vos informations en nous contactant à contact@floria.app.
              </p>
            </section>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
