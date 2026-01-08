import { Link } from "react-router-dom";
import { Leaf, Mail, Instagram } from "lucide-react";

export function Footer() {
  return (
    <footer id="contact" className="border-t border-border bg-card">
      <div className="container py-10 md:py-12">
        <div className="flex flex-col gap-8 md:flex-row md:items-center md:justify-between">
          <div className="space-y-4">
            <Link to="/" className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
                <Leaf className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="font-display text-xl font-semibold text-foreground">
                Flore
              </span>
            </Link>
            <p className="text-muted-foreground max-w-md">
              Votre assistant intelligent pour prendre soin de vos plantes.
            </p>
          </div>

          <div className="space-y-4">
            <a
              href="mailto:contact@flore.app"
              className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors"
            >
              <Mail className="h-4 w-4" />
              contact@flore.app
            </a>
            <div className="flex gap-3">
              <a
                href="https://www.instagram.com"
                target="_blank"
                rel="noreferrer"
                className="flex h-9 w-9 items-center justify-center rounded-full bg-secondary text-secondary-foreground hover:bg-primary hover:text-primary-foreground transition-colors"
                aria-label="Instagram"
              >
                <Instagram className="h-4 w-4" />
              </a>
              <a
                href="https://x.com"
                target="_blank"
                rel="noreferrer"
                className="flex h-9 w-9 items-center justify-center rounded-full bg-secondary text-secondary-foreground hover:bg-primary hover:text-primary-foreground transition-colors"
                aria-label="X"
              >
                <span className="text-sm font-semibold">X</span>
              </a>
            </div>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-border flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-muted-foreground">
            © 2026 Flore. Tous droits réservés.
          </p>
          <div className="flex gap-6">
            <Link
              to="/mentions-legales"
              className="text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              Mentions légales
            </Link>
            <Link
              to="/confidentialite"
              className="text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              Confidentialité
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
