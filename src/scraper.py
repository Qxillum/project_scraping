"""
Doc API : https://www.mediawiki.org/wiki/API:Revisions
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pandas as pd
import requests

from config import (
    API_ENDPOINT, DEFAULT_LANG, REQUEST_PAUSE_S, REV_BATCH, USER_AGENT,
)

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# Propriétés demandées pour chaque révision.
# sha1 = empreinte du contenu dans MediaWiki -> permet de détecter les reverts.
RV_PROPS = "ids|timestamp|user|comment|size|sha1|flags"

def fetch_revisions(page: str, lang: str = DEFAULT_LANG,
                    max_revisions: int | None = None) -> pd.DataFrame:

    endpoint = API_ENDPOINT.format(lang=lang)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    params = {
        "action": "query",
        "prop": "revisions",
        "titles": page,
        "rvlimit": REV_BATCH,
        "rvprop": RV_PROPS,
        "rvdir": "newer", # Du plus ancien au plus récent
        "format": "json",
        "formatversion": "2",
    }

    rows: list[dict] = []
    while True:
        resp = session.get(endpoint, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        pages = data.get("query", {}).get("pages", [])

        for p in pages:
            if "missing" in p:
                raise ValueError(
                    f"Page introuvable : {page!r} ({lang}.wikipedia)"
                )

            for rev in p.get("revisions", []):
                rows.append({
                    "revid": rev.get("revid"),
                    "parentid": rev.get("parentid"),
                    "timestamp": rev.get("timestamp"),
                    "user": rev.get("user", "(supprimé)"),
                    "anon": "anon" in rev,
                    "minor": "minor" in rev,
                    "size": rev.get("size"),
                    "sha1": rev.get("sha1"),
                    "comment": rev.get("comment", ""),
                })

        if max_revisions and len(rows) >= max_revisions:
            rows = rows[:max_revisions]
            break

        if "continue" in data:
            params.update(data["continue"])
            time.sleep(REQUEST_PAUSE_S)
        else:
            break

    df = pd.DataFrame(rows)
    df["page"] = page
    df["lang"] = lang
    return df

# Sauvegarde des données
def save_raw(df: pd.DataFrame, page: str) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    slug = page.replace(" ", "_")
    csv_path = RAW_DIR / f"{slug}_raw.csv"
    df.to_csv(csv_path, index=False)
    (RAW_DIR / f"{slug}_raw.json").write_text(
        json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return csv_path