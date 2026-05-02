# TP2 — Qualité de code : job flake8 en parallèle

## Objectif

Ajouter un second job `lint` dans `.github/workflows/ci.yml` pour vérifier le style PEP8 avec `flake8`. Ce job tourne **en parallèle** du job `tests` (pas de `needs:`).

## À faire en classe (par le prof)

1. Vérifier que `flake8` ne remonte rien sur le code actuel :
   ```bash
   flake8 src tests
   ```
2. Éditer `.github/workflows/ci.yml` pour ajouter le job `lint` (voir bloc plus bas).
3. Commit + push.
4. Dans l'onglet **Actions**, montrer que les deux jobs `tests` et `lint` apparaissent **côte à côte** dans le même run, et démarrent en même temps.
5. Démontrer un échec : insérer une ligne trop longue ou un import inutile dans `src/tp_app/calculator.py`, push → la CI passe au rouge **uniquement** sur le job `lint`, le job `tests` reste vert.

## À faire ensuite par chaque étudiant

1. Repartir de `main` à jour : `git checkout main && git pull`.
2. Créer une branche `feature/<prenom>-tp2`.
3. Ajouter une fonction dans `src/tp_app/text_tools.py` (par exemple `to_upper(text)`).
4. Introduire **volontairement** un défaut de style : ligne > 100 caractères, ou variable inutilisée.
5. Push, ouvrir une PR → constater que `lint` est rouge.
6. Corriger, repush → constater que les deux jobs sont verts.

## Fichier complet — `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: ["**"]
  pull_request:

jobs:
  tests:
    name: Tests pytest
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-dev.txt
      - run: pytest -v

  lint:
    name: Lint flake8
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-dev.txt
      - run: flake8 src tests
```

## Points pédagogiques

- **Pas de `needs:`** entre `tests` et `lint` → exécution parallèle. Plus rapide, et les deux résultats sont indépendants.
- L'absence de configuration partagée : chaque job repart d'une VM neuve. C'est volontaire pour l'isolation, mais ça implique de réinstaller les deps. (On pourra plus tard introduire le cache `actions/cache@v4`.)
- La config flake8 vit dans `.flake8` à la racine (`max-line-length = 100`).
- Un job rouge **bloque** un merge si la branche est protégée (à montrer dans Settings → Branches).
