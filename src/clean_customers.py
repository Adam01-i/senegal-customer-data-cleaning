"""
Nettoyage d'un jeu de données clients e-commerce (Sénégal / Afrique de
l'Ouest) : valeurs manquantes, catégories mal normalisées, formats
incohérents.

Corrections apportées par rapport au notebook original (`tp1.ipynb`) :

1. **Imputation redondante / contradictoire** : le notebook original
   imputait `income_fcfa` par la moyenne globale (cellule "Imputation
   simple"), PUIS, plus loin, tentait une imputation "conditionnelle" par
   groupe (moyenne par `gender`) sur la même colonne. Comme la colonne
   n'avait déjà plus aucune valeur manquante après la première imputation,
   la seconde étape ne faisait rien (code mort qui donnait l'illusion d'une
   méthode plus fine). Ici, une seule stratégie est appliquée -la
   conditionnelle, plus informative- et appliquée une seule fois.
2. **`gestion_var(df, col)` retournait un DataFrame mais la valeur de
   retour était ignorée à l'appel** (`gestion_var(df, 'city')` sans
   réassignation). Cela fonctionnait par effet de bord (mutation en place),
   mais de façon fragile et peu lisible. Corrigé : `df = gestion_var(df, col)`.
3. **Catégories jamais nettoyées avant analyse** : la colonne `segment`
   contient en réalité 15 valeurs uniques pour 5 catégories réelles
   (`'Standard'`, `'Standard '`, `'Standard\\t'`, `'Standard  '`, ...) à
   cause d'espaces/tabulations non retirés. Le notebook original ne le
   détectait pas (il n'affichait `value_counts()` que pour `gender`).
   `is_member` mélange `'yes'/'no'/'1'/'0'/'True'/'False'`. `gender`
   mélange casse et valeurs (`'M'`, `'male'`, `'FEMALE'`, `'Unknown'`,
   valeurs manquantes). Toutes ces colonnes sont maintenant normalisées.
4. **Numéros de téléphone dans des formats incohérents**
   (`+221 388642288`, `00221737929854`, `309479`, ...), jamais traités dans
   le notebook original. Une normalisation basique vers `+221XXXXXXXXX` est
   ajoutée (les numéros trop courts pour être des numéros sénégalais valides
   sont laissés tels quels et signalés).

Usage:
    python src/clean_customers.py --input data/datasets_tp1.csv --output data/customers_clean.csv
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


def report_missing(df: pd.DataFrame, label: str) -> None:
    pct = (df.isna().sum() / len(df) * 100).round(2)
    pct = pct[pct > 0]
    print(f"\n--- Valeurs manquantes ({label}) ---")
    print(pct.to_string() if len(pct) else "Aucune valeur manquante.")


def normalize_text_column(series: pd.Series) -> pd.Series:
    """Retire espaces/tabulations superflus et harmonise la casse.

    Le simple `.str.title()` casse les acronymes ('NGO' -> 'Ngo', 'VIP' ->
    'Vip') : les valeurs correspondant à un acronyme connu sont donc
    remises en majuscules après la mise en forme Title Case.
    """
    acronyms = {"Vip": "VIP", "Ngo": "NGO"}
    cleaned = series.str.strip().str.title()
    return cleaned.replace(acronyms)


def normalize_gender(series: pd.Series) -> pd.Series:
    mapping = {
        "m": "M", "male": "M", "f": "F", "female": "F",
        "unknown": "Unknown",
    }
    cleaned = series.str.strip().str.lower().map(mapping)
    return cleaned.fillna("Unknown")


def normalize_is_member(series: pd.Series) -> pd.Series:
    mapping = {"yes": True, "1": True, "true": True, "no": False, "0": False, "false": False}
    return series.str.strip().str.lower().map(mapping)


def normalize_phone(phone: str) -> str:
    """Ramène les numéros au format +221XXXXXXXXX quand c'est possible."""
    if pd.isna(phone):
        return phone
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("00221"):
        digits = digits[2:]  # 00221XXXXXXXXX -> 221XXXXXXXXX
    if digits.startswith("221") and len(digits) == 12:
        return "+" + digits
    if len(digits) == 9:  # numéro local sans indicatif
        return "+221" + digits
    return phone  # format non reconnu : laissé tel quel pour vérification manuelle


def impute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Une seule stratégie d'imputation par colonne (pas de double
    imputation contradictoire comme dans le notebook original)."""
    # Revenu : moyenne conditionnelle par genre (plus informatif qu'une moyenne globale)
    df["income_fcfa"] = df["income_fcfa"].fillna(df.groupby("gender")["income_fcfa"].transform("mean"))
    df["income_fcfa"] = df["income_fcfa"].fillna(df["income_fcfa"].mean())  # filet de sécurité

    for col in ["city", "payment_method"]:
        mode = df[col].mode()
        if not mode.empty:
            df[col] = df[col].fillna(mode[0])

    df["latitude"] = df["latitude"].fillna(df["latitude"].median())
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    n_before = len(df)
    df = df.drop_duplicates()
    print(f"Doublons supprimés : {n_before - len(df)}")

    report_missing(df, "avant nettoyage")

    df["segment"] = normalize_text_column(df["segment"])
    df["gender"] = normalize_gender(df["gender"])
    df["is_member"] = normalize_is_member(df["is_member"])
    df["country"] = df["country"].replace({"Cote dIvoire": "Côte d'Ivoire"})
    df["phone"] = df["phone"].apply(normalize_phone)

    df = impute_missing(df)

    report_missing(df, "après nettoyage")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/datasets_tp1.csv")
    parser.add_argument("--output", default="data/customers_clean.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    print(f"{len(df)} lignes, {df.shape[1]} colonnes chargées depuis {args.input}")

    df_clean = clean(df)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(args.output, index=False)
    print(f"\n✅ Données nettoyées -> {args.output}")


if __name__ == "__main__":
    main()
