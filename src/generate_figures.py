"""Generate reproducible figures for the project README."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


COLORS = {
    "ink": "#17212b",
    "muted": "#607080",
    "before": "#d97757",
    "after": "#1f8a70",
    "accent": "#28666e",
    "grid": "#dfe7e9",
}


def style_plot() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "axes.labelcolor": COLORS["ink"],
            "axes.edgecolor": COLORS["grid"],
            "axes.labelsize": 10,
            "xtick.color": COLORS["muted"],
            "ytick.color": COLORS["muted"],
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def save_missingness(raw: pd.DataFrame, clean: pd.DataFrame, output_dir: Path) -> None:
    columns = raw.columns[raw.isna().any()]
    before = raw[columns].isna().mean().mul(100).sort_values(ascending=True)
    after = clean[columns].isna().mean().reindex(before.index).fillna(0)

    figure, axis = plt.subplots(figsize=(9, 4.8))
    positions = range(len(before))
    axis.barh([p - 0.18 for p in positions], before, height=0.34, label="Avant", color=COLORS["before"])
    axis.barh([p + 0.18 for p in positions], after, height=0.34, label="Après", color=COLORS["after"])
    axis.set_yticks(list(positions), before.index)
    axis.set_xlabel("Part de valeurs manquantes (%)")
    axis.set_title("Les valeurs manquantes après nettoyage sont limitées aux e-mails")
    axis.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    axis.set_axisbelow(True)
    axis.legend(frameon=False, loc="lower right")
    figure.tight_layout()
    figure.savefig(output_dir / "missing-values-before-after.png", dpi=180, bbox_inches="tight")
    plt.close(figure)


def save_categories(raw: pd.DataFrame, clean: pd.DataFrame, output_dir: Path) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    category_specs = [("segment", "Segment"), ("gender", "Genre")]
    for axis, (column, label) in zip(axes, category_specs):
        raw_values = raw[column].fillna("Manquant").astype(str).value_counts()
        raw_values.index = raw_values.index.map(lambda value: value.replace("\t", "[tab]"))
        clean_values = clean[column].fillna("Manquant").astype(str).value_counts()
        values = sorted(set(raw_values.index) | set(clean_values.index))
        positions = range(len(values))
        axis.barh([p - 0.18 for p in positions], [raw_values.get(value, 0) for value in values], height=0.34, label="Avant", color=COLORS["before"])
        axis.barh([p + 0.18 for p in positions], [clean_values.get(value, 0) for value in values], height=0.34, label="Après", color=COLORS["after"])
        axis.set_yticks(list(positions), values)
        axis.set_xlabel("Nombre de clients")
        axis.set_title(label)
        axis.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
        axis.set_axisbelow(True)
    axes[0].legend(frameon=False, loc="lower right")
    figure.suptitle("Réduction des variations de catégories", fontsize=15, fontweight="bold")
    figure.tight_layout()
    figure.savefig(output_dir / "category-normalization.png", dpi=180, bbox_inches="tight")
    plt.close(figure)


def save_business_snapshot(clean: pd.DataFrame, output_dir: Path) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    clean.groupby("city")["total_amount_fcfa"].sum().sort_values().plot.barh(ax=axes[0], color=COLORS["accent"])
    axes[0].set_title("Chiffre d'affaires total par ville")
    axes[0].set_xlabel("Montant total (FCFA)")
    axes[0].set_ylabel("")
    clean["income_fcfa"].plot.hist(ax=axes[1], bins=18, color=COLORS["accent"], edgecolor="white")
    axes[1].set_title("Distribution des revenus")
    axes[1].set_xlabel("Revenu (FCFA)")
    axes[1].set_ylabel("Nombre de clients")
    for axis in axes:
        axis.grid(axis="y", color=COLORS["grid"], linewidth=0.8)
        axis.set_axisbelow(True)
    figure.suptitle("Aperçu du portefeuille client après nettoyage", fontsize=15, fontweight="bold")
    figure.tight_layout()
    figure.savefig(output_dir / "customer-snapshot.png", dpi=180, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/datasets_tp1.csv")
    parser.add_argument("--clean", default="data/customers_clean.csv")
    parser.add_argument("--output-dir", default="outputs/figures")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(args.input)
    clean = pd.read_csv(args.clean)
    style_plot()
    save_missingness(raw, clean, output_dir)
    save_categories(raw, clean, output_dir)
    save_business_snapshot(clean, output_dir)
    print(f"Figures générées dans {output_dir}")


if __name__ == "__main__":
    main()