# Charte graphique
PALETTE = [
    "#5A6FC0",  # bleu
    "#A7C7E7",  # bleu clair
    "#B39DDB",  # violet clair
    "#8E44AD",  # violet
    "#4A235A",  # violet foncé
]
ACCENT = "#2C3E7B"
MOVING_AVG_COLOR = "#1F3B99"
HEATMAP_CMAP = "viridis"

# Paramètres de collecte
API_ENDPOINT = "https://{lang}.wikipedia.org/w/api.php"
DEFAULT_LANG = "fr"
USER_AGENT = "project_scrapping (GitHub: qxillum)"
REQUEST_PAUSE_S = 0.5   # temporisation entre requêtes
REV_BATCH = 500          # nb de révisions par requête max

# Mot-Clés annulation multilingues
REVERT_KEYWORDS = [
    "annulation", "annul", "révocation", "revert", "reverted",
    "undid", "undo", "rv ", "rvv", "rétabli", "restaur",
]
