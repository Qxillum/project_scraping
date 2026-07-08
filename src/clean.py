"""
Nettoyage des révisions :
- conversion des types
- traitement des valeurs manquantes
- suppression des doublons
- tri chronologique
- ajout des informations temporelles
- détection des annulations probables
"""

from pathlib import Path

import pandas as pd

from config import REVERT_KEYWORDS


CLEAN_DIR = Path(__file__).resolve().parent.parent / "data" / "clean"


def clean_revisions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Conversion et valeurs manquantes
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
        errors="coerce"
    )
    df["size"] = pd.to_numeric(
        df["size"],
        errors="coerce"
    ).astype("Int64")

    df["comment"] = df["comment"].fillna("")
    df["user"] = df["user"].fillna("(supprimé)")

    # Suppression des dates invalides et des doublons
    df = (
        df.dropna(subset=["timestamp"])
        .drop_duplicates(subset=["revid"])
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    # Informations temporelles
    df["date"] = df["timestamp"].dt.date
    df["weekday"] = df["timestamp"].dt.day_name()
    df["hour"] = df["timestamp"].dt.hour

    # Variation de taille
    df["size_diff"] = df["size"].diff().astype("Int64")

    # Annulation détectée par retour à une ancienne empreinte
    sha1 = df["sha1"].replace("", pd.NA)
    df["revert_sha1"] = sha1.notna() & sha1.duplicated()

    # Annulation détectée dans le commentaire
    df["revert_kw"] = df["comment"].str.lower().apply(
        lambda comment: any(
            keyword in comment
            for keyword in REVERT_KEYWORDS
        )
    )

    df["is_revert"] = df["revert_sha1"] | df["revert_kw"]

    return df


def save_clean(df: pd.DataFrame, page: str) -> Path:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    path = CLEAN_DIR / f"{page.replace(' ', '_')}_clean.csv"
    df.to_csv(path, index=False)

    return path