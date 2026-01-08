import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Leaf, Menu, X } from "lucide-react";

const navLinks = [
  { label: "Accueil", href: "/" },
  { label: "Fonctionnalités", href: "/#features" },
  { label: "À propos", href: "/#about" },
  { label: "Contact", href: "/#contact" },
];

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const handleNavClick = (href: string) => {
    setIsMenuOpen(false);
    if (href.startsWith("/#")) {
      const id = href.replace("/#", "");
      const element = document.getElementById(id);
      if (element) {
        element.scrollIntoView({ behavior: "smooth" });
      }
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary transition-transform group-hover:scale-105">
            <Leaf className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="font-display text-xl font-semibold text-foreground">
            Flore
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={(e) => {
                if (link.href.startsWith("/#")) {
                  e.preventDefault();
                  handleNavClick(link.href);
                }
              }}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* CTA Button */}
        <div className="hidden md:block">
          <Link to="/chat">
            <Button variant="nature" size="default">
              Commencer
            </Button>
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="md:hidden p-2 text-foreground"
          aria-label="Toggle menu"
        >
          {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden border-t border-border bg-background animate-fade-in">
          <nav className="container py-4 flex flex-col gap-4">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={(e) => {
                  if (link.href.startsWith("/#")) {
                    e.preventDefault();
                    handleNavClick(link.href);
                  }
                }}
                className="text-base font-medium text-muted-foreground transition-colors hover:text-primary py-2"
              >
                {link.label}
              </a>
            ))}
            <Link to="/chat" onClick={() => setIsMenuOpen(false)}>
              <Button variant="nature" size="lg" className="w-full mt-2">
                Commencer
              </Button>
            </Link>
          </nav>
        </div>
      )}
    </header>
  );
}
