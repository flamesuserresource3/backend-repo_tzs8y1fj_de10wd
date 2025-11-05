from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import re
from urllib.parse import quote

app = FastAPI(title="WikiStyle Encyclopedia API")

# Allow all origins for sandbox; in production, restrict to the frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Article(BaseModel):
    slug: str
    title: str
    intro: str
    sentences: List[str]
    categories: List[str]


# Demo dataset kept server-side to enable richer queries and search
ARTICLES: List[Article] = [
    Article(
        slug="startseite",
        title="Startseite",
        intro="Willkommen bei der freien Enzyklopädie in deutscher Sprache.",
        sentences=[
            "Hier findest du kompakte, neutrale Artikel in genau fünf Sätzen.",
            "Nutze die Suche oben, stöbere über die Kategorien oder wähle einen Zufallsartikel.",
            "Interne Verweise helfen dir, schnell zwischen verwandten Themen zu navigieren.",
            "Aktiviere den Dark Mode für eine angenehme Darstellung in dunkler Umgebung.",
            "Diese Seite ist optimiert für Barrierefreiheit und schnelle Ladezeiten.",
        ],
        categories=["Portal"],
    ),
    Article(
        slug="computer",
        title="Computer",
        intro="Ein Computer ist eine programmierbare Maschine zur Verarbeitung von Informationen.",
        sentences=[
            "Er empfängt Eingaben, verarbeitet Daten nach definierten Regeln und liefert Ausgaben.",
            "Seine Architektur umfasst typischerweise Prozessor, Arbeitsspeicher, Massenspeicher und Schnittstellen.",
            "Computer sind Grundlage moderner Informationsgesellschaften und industrieller Produktion.",
            "Sie existieren in vielfältigen Formen von eingebetteten Systemen bis zu Hochleistungsrechnern.",
            "Software legt fest, welche Aufgaben ein Computer konkret ausführt.",
        ],
        categories=["Technologie", "Informatik"],
    ),
    Article(
        slug="demokratie",
        title="Demokratie",
        intro="Demokratie ist eine Regierungsform, in der politische Macht von den Bürgerinnen und Bürgern ausgeht.",
        sentences=[
            "Sie beruht auf freien Wahlen, Rechtsstaatlichkeit und dem Schutz von Grundrechten.",
            "Gewaltenteilung und unabhängige Institutionen begrenzen staatliche Macht.",
            "In repräsentativen Systemen übertragen Wählerinnen und Wähler Mandate an Abgeordnete.",
            "Direkte Elemente wie Volksentscheide ergänzen mancherorts die Repräsentation.",
            "Pluralismus und öffentliche Debatten sind zentrale Voraussetzungen funktionierender Demokratie.",
        ],
        categories=["Politik", "Gesellschaft"],
    ),
    Article(
        slug="photosynthese",
        title="Photosynthese",
        intro="Photosynthese ist der biologische Prozess, bei dem Lichtenergie in chemische Energie umgewandelt wird.",
        sentences=[
            "Pflanzen, Algen und bestimmte Bakterien nutzen Chlorophyll, um Licht zu absorbieren.",
            "Aus Kohlendioxid und Wasser entstehen energiereiche Verbindungen und Sauerstoff.",
            "Der Prozess gliedert sich in lichtabhängige Reaktionen und den Calvin-Zyklus.",
            "Photosynthese bildet die Grundlage fast aller Nahrungsketten auf der Erde.",
            "Ihre Effizienz hängt von Faktoren wie Lichtintensität, Temperatur und Nährstoffen ab.",
        ],
        categories=["Biologie", "Chemie"],
    ),
    Article(
        slug="kunstliche-intelligenz",
        title="Künstliche Intelligenz",
        intro="Künstliche Intelligenz befasst sich mit Systemen, die Aufgaben mit intelligentem Verhalten lösen.",
        sentences=[
            "Methoden reichen von symbolischen Verfahren bis zu statistischem Lernen und neuronalen Netzen.",
            "Anwendungen finden sich in Sprache, Bildverarbeitung, Medizin und Industrie.",
            "Machine Learning lernt Muster aus Daten und verbessert Modelle iterativ.",
            "Fragen nach Transparenz, Fairness und Sicherheit begleiten die Verbreitung.",
            "Regulatorische Rahmen sollen verantwortungsvolle Entwicklung und Nutzung gewährleisten.",
        ],
        categories=["Technologie", "Informatik"],
    ),
    Article(
        slug="ozean",
        title="Ozean",
        intro="Ozeane bedecken den größten Teil der Erdoberfläche und prägen Klima sowie Biodiversität.",
        sentences=[
            "Meeresströmungen verteilen Wärme und beeinflussen Wetterphänomene weltweit.",
            "Ökosysteme reichen von küstennahen Zonen bis zu lichtlosen Tiefseegebieten.",
            "Verschmutzung und Übernutzung gefährden Lebensräume und Ressourcen.",
            "Schutzgebiete und nachhaltige Nutzung sollen maritime Vielfalt bewahren.",
            "Forschung liefert Daten für Klimamodelle und Meeresmanagement.",
        ],
        categories=["Geographie", "Umwelt"],
    ),
    Article(
        slug="algorithmus",
        title="Algorithmus",
        intro="Ein Algorithmus ist eine endliche, eindeutige Vorschrift zur Lösung eines Problems.",
        sentences=[
            "Er beschreibt Schritte, die von Menschen oder Maschinen ausgeführt werden können.",
            "Korrektheit, Effizienz und Verständlichkeit sind wichtige Qualitätsmerkmale.",
            "Datenstrukturen beeinflussen Aufwand und Implementierung.",
            "Algorithmen werden in Pseudocode, Flussdiagrammen oder Programmiersprachen formuliert.",
            "Komplexitätstheorie untersucht systematisch Ressourcenbedarf und Grenzen der Berechenbarkeit.",
        ],
        categories=["Informatik"],
    ),
    Article(
        slug="energie",
        title="Energie",
        intro="Energie ist die Fähigkeit eines Systems, Arbeit zu verrichten oder Wärme abzugeben.",
        sentences=[
            "Sie tritt in Formen wie mechanischer, thermischer, elektrischer und chemischer Energie auf.",
            "Erhaltungssätze beschreiben, wie Energie in abgeschlossenen Systemen konstant bleibt.",
            "Umwandlungen sind mit Verlusten verbunden, die als Entropiezunahme erscheinen.",
            "Erneuerbare Quellen sollen fossile Energieträger schrittweise ersetzen.",
            "Effizienzmaßnahmen reduzieren Bedarf und Emissionen in allen Sektoren.",
        ],
        categories=["Physik", "Umwelt"],
    ),
    Article(
        slug="gravitation",
        title="Gravitation",
        intro="Gravitation ist die universelle Anziehung zwischen Massen.",
        sentences=[
            "Sie hält Planeten in Umlaufbahnen und strukturiert Galaxien.",
            "Newtons Theorie beschreibt sie als Kraft, Einsteins Allgemeine Relativität als Krümmung der Raumzeit.",
            "Messungen und Beobachtungen bestätigen ihre Wirkung im Großen und Kleinen.",
            "Gravitationswellen liefern Einblicke in energiereiche kosmische Ereignisse.",
            "Präzisionsmessungen testen die Gültigkeit physikalischer Modelle.",
        ],
        categories=["Physik", "Astronomie"],
    ),
    Article(
        slug="internet",
        title="Internet",
        intro="Das Internet ist ein globales Netzwerk miteinander verbundener Rechnernetze.",
        sentences=[
            "Es basiert auf Protokollen wie TCP/IP und ermöglicht den Austausch von Datenpaketen.",
            "Dienste wie das Web, E-Mail und Streaming bauen auf dieser Infrastruktur auf.",
            "Skalierung und Redundanz sichern Verfügbarkeit trotz hoher Lasten.",
            "Sicherheitsfragen betreffen Datenschutz, Angriffe und Resilienz.",
            "Standards werden von Gremien wie der IETF weiterentwickelt.",
        ],
        categories=["Technologie", "Kommunikation"],
    ),
    Article(
        slug="musik",
        title="Musik",
        intro="Musik ist eine Kunstform, die Klänge in Struktur und Zeit ordnet.",
        sentences=[
            "Rhythmus, Melodie, Harmonik und Klangfarbe bilden zentrale Gestaltungsmittel.",
            "Stile variieren kulturell und historisch von klassisch bis elektronisch.",
            "Aufführungspraxis und Aufnahmeverfahren prägen das Hörerlebnis.",
            "Musik kann Emotionen ausdrücken, Kommunikation fördern und Gemeinschaft stiften.",
            "Forschung untersucht Wirkung, Wahrnehmung und kognitive Grundlagen musikalischen Erlebens.",
        ],
        categories=["Kultur", "Kunst"],
    ),
    Article(
        slug="sprache",
        title="Sprache",
        intro="Sprache ist ein System von Zeichen, mit dem Menschen Bedeutungen austauschen.",
        sentences=[
            "Sie beruht auf Lauten oder Schrift und folgt grammatischen Regeln.",
            "Sprachen verändern sich durch Gebrauch, Kontakt und Innovation.",
            "Linguistik analysiert Struktur, Erwerb und Variation von Sprache.",
            "Mehrsprachigkeit ist weltweit verbreitet und gesellschaftlich relevant.",
            "Digitale Medien beeinflussen Register, Normen und Verbreitung.",
        ],
        categories=["Linguistik", "Kultur"],
    ),
    Article(
        slug="stadt",
        title="Stadt",
        intro="Eine Stadt ist eine dicht bebaute Siedlung mit vielfältigen Funktionen.",
        sentences=[
            "Sie bündelt Wohnen, Arbeit, Bildung, Kultur und Verkehr.",
            "Stadtentwicklung balanciert Wachstum, Lebensqualität und Nachhaltigkeit.",
            "Infrastruktur und Planung prägen Mobilität und Flächennutzung.",
            "Soziale Mischung und Teilhabe fördern Integration und Resilienz.",
            "Digitale Technologien unterstützen Verwaltung und beteiligungsorientierte Prozesse.",
        ],
        categories=["Geographie", "Gesellschaft"],
    ),
]


def to_snippet(article: Article) -> dict:
    return {
        "slug": article.slug,
        "title": article.title,
        "intro": article.intro,
        "categories": article.categories,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/articles")
async def list_articles(category: Optional[str] = None) -> List[dict]:
    items = [a for a in ARTICLES if (category is None or category in a.categories)]
    # sort alphabetically by title
    items.sort(key=lambda x: x.title.lower())
    return [to_snippet(a) for a in items]


@app.get("/articles/{slug}")
async def get_article(slug: str) -> Article:
    for a in ARTICLES:
        if a.slug == slug:
            return a
    raise HTTPException(status_code=404, detail="Artikel nicht gefunden")


@app.get("/search")
async def search(q: str) -> List[dict]:
    query = q.strip().lower()
    if not query:
        return []
    results = [a for a in ARTICLES if query in a.title.lower()]
    results.sort(key=lambda x: x.title.lower())
    return [to_snippet(a) for a in results[:20]]


@app.get("/categories")
async def categories() -> List[str]:
    cats = set()
    for a in ARTICLES:
        for c in a.categories:
            cats.add(c)
    return sorted(cats)


def split_to_five_sentences(text: str) -> List[str]:
    # naive sentence split on '.', '!', '?'
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    parts = [p.strip() for p in parts if p.strip()]
    # Expand or trim to exactly five sentences
    if len(parts) >= 5:
        return parts[:5]
    # If fewer than 5, pad by repeating the last sentence with slight marker
    while len(parts) < 5:
        parts.append(parts[-1])
    return parts


@app.get("/ai/explain")
async def ai_explain(term: str) -> dict:
    """
    Fetch a neutral German summary for the given term and return exactly five sentences.
    Uses the Wikipedia REST API (de) as a free knowledge source.
    """
    title = term.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Begriff darf nicht leer sein")
    url = f"https://api.wikimedia.org/core/v1/wikipedia/de/page/summary/{quote(title)}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, headers={"User-Agent": "WikiStyleSandbox/1.0"})
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Keine Zusammenfassung gefunden")
        r.raise_for_status()
        data = r.json()
    extract = data.get("extract") or data.get("description") or ""
    if not extract:
        raise HTTPException(status_code=404, detail="Keine Erklärung verfügbar")
    sentences = split_to_five_sentences(extract)
    return {"term": title, "sentences": sentences}
