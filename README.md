# Nettoyage de données clients e-commerce

Pipeline Python de nettoyage et de standardisation d’un jeu de données clients e-commerce couvrant plusieurs villes d’Afrique de l’Ouest.

Le projet traite un fichier de **1 000 clients et 20 colonnes**. Il illustre une démarche reproductible de data cleaning : diagnostic des valeurs manquantes, normalisation des catégories, harmonisation des formats et export d’un fichier prêt pour l’analyse.

## Résultats clés

| Indicateur | Résultat |
| --- | ---: |
| Lignes chargées | 1 000 |
| Colonnes | 20 |
| Doublons supprimés | 0 |
| Valeurs manquantes après nettoyage | E-mails uniquement |
| Valeurs de `segment` | 15 → 5 |
| Valeurs de `gender` | 8 → 3 |
| Format de `is_member` | booléen (`True` / `False`) |

Les valeurs manquantes d’e-mail sont volontairement conservées : une adresse ne peut pas être imputée de manière fiable sans créer une donnée artificielle.

## Fonctionnalités

Le script [`src/clean_customers.py`](src/clean_customers.py) réalise les opérations suivantes :

- suppression des doublons exacts ;
- rapport des valeurs manquantes avant et après traitement ;
- nettoyage des espaces et tabulations dans les colonnes catégorielles ;
- harmonisation de `segment` avec conservation des acronymes `VIP` et `NGO` ;
- normalisation de `gender` vers `M`, `F` ou `Unknown` ;
- conversion de `is_member` vers un booléen ;
- correction de `Cote dIvoire` en `Côte d'Ivoire` ;
- normalisation des numéros sénégalais vers le format `+221XXXXXXXXX` lorsque le format est identifiable ;
- imputation de `income_fcfa` par moyenne conditionnelle au genre, avec moyenne globale de secours ;
- imputation de `city` et `payment_method` par la valeur modale ;
- imputation de `latitude` par la médiane ;
- export CSV sans index.

## Jeu de données

Le fichier source [`data/datasets_tp1.csv`](data/datasets_tp1.csv) contient notamment :

| Domaine | Colonnes |
| --- | --- |
| Identification | `id`, `customer_id` |
| Profil | `age`, `gender`, `city`, `country`, `segment` |
| Commandes | `product_category`, `quantity`, `unit_price_fcfa`, `total_amount_fcfa` |
| Dates | `signup_date`, `last_purchase_date` |
| Contact | `email`, `phone` |
| Paiement et fidélité | `payment_method`, `is_member` |
| Géolocalisation | `latitude`, `longitude` |
| Revenus | `income_fcfa` |

## Installation

Le projet nécessite Python 3 et pandas.

```bash
git clone <URL_DU_DEPOT>
cd senegal-customer-data-cleaning

python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

> Sous Linux, utilisez `python3` si la commande `python` n’est pas disponible.

## Utilisation

Avec les chemins par défaut :

```bash
python3 src/clean_customers.py
```

En indiquant explicitement les fichiers d’entrée et de sortie :

```bash
python3 src/clean_customers.py \
  --input data/datasets_tp1.csv \
  --output data/customers_clean.csv
```

Le dossier parent du fichier de sortie est créé automatiquement s’il n’existe pas.

## Exemple de sortie console

```text
1000 lignes, 20 colonnes chargées depuis data/datasets_tp1.csv
Doublons supprimés : 0

--- Valeurs manquantes (avant nettoyage) ---
income_fcfa        7.1
city               3.0
gender            16.0
payment_method     3.9
email              2.9
latitude           2.1

--- Valeurs manquantes (après nettoyage) ---
email              2.9

✅ Données nettoyées -> data/customers_clean.csv
```

## Structure du projet

```text
senegal-customer-data-cleaning/
├── data/
│   ├── customers_clean.csv    # résultat généré
│   └── datasets_tp1.csv       # données brutes
├── outputs/
│   └── .gitkeep
├── src/
│   └── clean_customers.py     # pipeline de nettoyage
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Choix méthodologiques

### Imputation

Chaque colonne suit une stratégie unique et explicite. Le revenu est d’abord imputé avec la moyenne du groupe `gender`, puis la moyenne globale sert uniquement de filet de sécurité si un groupe ne fournit aucune valeur exploitable.

Les coordonnées, la ville et le mode de paiement utilisent respectivement la médiane et le mode. Les e-mails ne sont pas inventés.

### Normalisation

Les colonnes texte sont nettoyées avant l’analyse des catégories. Cette étape évite de considérer comme différentes des valeurs telles que `Standard`, `Standard ` et `Standard\t`.

Les numéros trop courts ou ambigus ne sont pas transformés automatiquement : ils sont conservés pour une vérification manuelle plutôt que corrigés au hasard.

## Reproductibilité

Les dépendances sont déclarées dans [`requirements.txt`](requirements.txt). Pour reproduire le résultat, utilisez le fichier brut comme entrée et un nouveau chemin de sortie :

```bash
python3 src/clean_customers.py \
  --input data/datasets_tp1.csv \
  --output data/customers_clean.csv
```

Le fichier généré peut ensuite être chargé avec pandas, Excel, Power BI ou tout autre outil d’analyse compatible CSV.

## Limites et évolutions possibles

- ajouter des tests automatisés pour chaque règle de normalisation ;
- valider les formats de téléphone selon le pays, et pas uniquement selon le préfixe sénégalais ;
- produire un rapport de qualité de données au format JSON ou HTML ;
- ajouter un fichier de verrouillage des dépendances pour des exécutions totalement reproductibles ;
- externaliser les règles de mapping dans une configuration dédiée.

## Contexte pédagogique

Ce projet a été réalisé dans le cadre d’un TP de data cleaning en Master 1 Système d’Information. Il sert de démonstration pratique des techniques d’imputation, de normalisation textuelle et de contrôle de la qualité des données.

## Licence

Projet distribué sous licence MIT. Voir [`LICENSE`](LICENSE).