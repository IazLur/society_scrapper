import argparse
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def guess_company_name(domain: str) -> str:
    """Try to guess the company name from the website title."""
    for scheme in ("https", "http"):
        try:
            resp = requests.get(f"{scheme}://{domain}", timeout=5)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                meta = soup.find("meta", property="og:site_name")
                if meta and meta.get("content"):
                    return meta["content"].strip()
                if soup.title and soup.title.string:
                    return soup.title.string.strip()
        except Exception:
            pass
    return urlparse(domain).hostname.split(".")[0] if domain else domain


def search_company(name: str, **filters):
    """Query the recherche-entreprises API."""
    url = "https://recherche-entreprises.api.gouv.fr/search"
    params = {"q": name, "page": 1, "per_page": 20}
    if filters.get("ape"):
        params["activite_principale"] = filters["ape"]
    if filters.get("departement"):
        params["departement"] = filters["departement"]
    if filters.get("region"):
        params["region"] = filters["region"]
    if filters.get("ville"):
        params["commune"] = filters["ville"]
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json().get("results", [])


def compute_score(company: dict) -> float:
    score = 0.0
    siege = company.get("siege", {})
    tranche = siege.get("tranche_effectif_salarie")
    try:
        if tranche:
            score += int(tranche)
    except ValueError:
        pass
    finances = company.get("finances", {})
    if finances:
        latest = sorted(finances.keys())[-1]
        ca = finances[latest].get("ca")
        if isinstance(ca, (int, float)):
            score += ca / 1e6  # millions
    return score


def export_csv(companies, path):
    fields = [
        "nom",
        "domaine",
        "adresse",
        "telephone",
        "email",
        "site",
        "secteur",
        "siren",
        "siret",
        "ca",
        "date_creation",
        "effectif",
        "score",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for c in companies:
            siege = c.get("siege", {})
            finances = c.get("finances", {})
            ca = None
            if finances:
                latest = sorted(finances.keys())[-1]
                ca = finances[latest].get("ca")
            writer.writerow({
                "nom": c.get("nom_raison_sociale"),
                "domaine": None,
                "adresse": siege.get("adresse"),
                "telephone": None,
                "email": None,
                "site": None,
                "secteur": c.get("activite_principale"),
                "siren": c.get("siren"),
                "siret": siege.get("siret"),
                "ca": ca,
                "date_creation": c.get("date_creation"),
                "effectif": siege.get("tranche_effectif_salarie"),
                "score": compute_score(c),
            })


def main():
    parser = argparse.ArgumentParser(description="Search companies by domain")
    parser.add_argument("domain", help="Domain name")
    parser.add_argument("--ape")
    parser.add_argument("--departement")
    parser.add_argument("--region")
    parser.add_argument("--ville")
    parser.add_argument("--export", help="Export CSV path")
    args = parser.parse_args()

    name = guess_company_name(args.domain)
    companies = search_company(
        name,
        ape=args.ape,
        departement=args.departement,
        region=args.region,
        ville=args.ville,
    )
    for c in companies:
        c["score"] = compute_score(c)
    companies.sort(key=lambda x: x["score"], reverse=True)
    for c in companies:
        print(f"{c['nom_raison_sociale']} - SIREN {c['siren']} - Score {c['score']:.2f}")

    if args.export:
        export_csv(companies, args.export)
        print(f"Exported {len(companies)} companies to {args.export}")

if __name__ == "__main__":
    main()
