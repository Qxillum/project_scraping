"""
Utilisation :
    python main.py "Vaccination" --lang fr

Avec une limite de révisions :
    python main.py "Vaccination" --lang fr --max 1000
"""
import argparse

from src.analyze import run_all
from src.clean import clean_revisions, save_clean
from src.scraper import fetch_revisions, save_raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("page")
    parser.add_argument("--lang", default="fr")
    parser.add_argument("--max", type=int)
    args = parser.parse_args()

    raw = fetch_revisions(args.page, args.lang, args.max)

    if raw.empty:
        raise ValueError("Aucune révision récupérée.")

    raw_path = save_raw(raw, args.page)

    clean = clean_revisions(raw)

    if clean.empty:
        raise ValueError("Aucune donnée après nettoyage.")

    clean_path = save_clean(clean, args.page)
    result = run_all(clean, args.page)

    print(f"{len(raw)} révisions collectées : {raw_path}")
    print(f"{len(clean)} révisions nettoyées : {clean_path}")

    print("\nMétriques :")
    for nom, valeur in result["metrics"].items():
        print(f"- {nom} : {valeur}")

    print("\nFigures :")
    for nom, chemin in result["figures"].items():
        print(f"- {nom} : {chemin}")


if __name__ == "__main__":
    main()