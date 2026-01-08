import { Link } from "react-router-dom";
import { Leaf, Mail, Instagram, Twitter } from "lucide-react";

export function Footer() {
  return (
    <footer id="contact" className="border-t border-border bg-card">
      <div className="container py-12 md:py-16">
        <div className="grid gap-8 md:grid-cols-4">
          {/* Brand */}
          <div className="md:col-span-2">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
                <Leaf className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="font-display text-xl font-semibold text-foreground">
                Flore
              </span>
            </Link>
            <p className="text-muted-foreground max-w-sm">
              Votre assistant intelligent pour prendre soin de vos plantes. 
              Des conseils personnalisés pour un jardin intérieur florissant.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-display text-lg font-semibold mb-4 text-foreground">
              Navigation
            </h4>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Accueil
                </Link>
              </li>
              <li>
                <a href="/#features" className="text-muted-foreground hover:text-primary transition-colors">
                  Fonctionnalités
                </a>
              </li>
              <li>
                <Link to="/chat" className="text-muted-foreground hover:text-primary transition-colors">
                  Chatbot
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-display text-lg font-semibold mb-4 text-foreground">
              Contact
            </h4>
            <ul className="space-y-3">
              <li>
                <a 
                  href="mailto:contact@flore.app" 
                  className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors"
                >
                  <Mail className="h-4 w-4" />
                  contact@flore.app
                </a>
              </li>
              <li className="flex gap-3 pt-2">
                <a 
                  href="#" 
                  className="flex h-9 w-9 items-center justify-center rounded-full bg-secondary text-secondary-foreground hover:bg-primary hover:text-primary-foreground transition-colors"
                  aria-label="Instagram"
                >
                  <Instagram className="h-4 w-4" />
                </a>
                <a 
                  href="#" 
                  className="flex h-9 w-9 items-center justify-center rounded-full bg-secondary text-secondary-foreground hover:bg-primary hover:text-primary-foreground transition-colors"
                  aria-label="Twitter"
                >
                  <Twitter className="h-4 w-4" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-12 pt-8 border-t border-border flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-muted-foreground">
            © 2026 Flore. Tous droits réservés.
          </p>
          <div className="flex gap-6">
            <a href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">
              Mentions légales
            </a>
            <a href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">
              Confidentialité
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
