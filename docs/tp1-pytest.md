# TP1 — Premier workflow GitHub Actions : pytest sur push

## Objectif

Créer un workflow GitHub Actions qui exécute automatiquement la suite de tests `pytest` à chaque `push` (sur n'importe quelle branche) et à chaque `pull_request`.

## À faire en classe (par le prof)

1. Vérifier que les tests passent localement :
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
   pytest -v
   ```
2. Créer le fichier `.github/workflows/ci.yml` (voir bloc plus bas).
3. Commit + push sur `main`.
4. Aller dans l'onglet **Actions** du repo GitHub → observer le run, cliquer dessus pour voir les logs étape par étape.

## À faire ensuite par chaque étudiant

1. Créer une branche : `git checkout -b feature/<prenom>-tp1`.
2. Ajouter une nouvelle fonction dans `src/tp_app/calculator.py` (par exemple `power(base, exponent)`).
3. Ajouter un test correspondant dans `tests/test_calculator.py`.
4. Push, ouvrir une Pull Request vers `main`.
5. **Casser volontairement le test** (changer une assertion) pour voir la CI passer au rouge → corriger → voir la CI repasser au vert.

## Bloc YAML à recopier — `.github/workflows/ci.yml`

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
      - name: Installer les dépendances
        run: pip install -r requirements-dev.txt
      - name: Lancer pytest
        run: pytest -v
```

## Points pédagogiques à souligner

- Le déclencheur `on:` détermine **quand** la CI tourne (push, pull_request, schedule, manual…).
- `runs-on` : la machine virtuelle fournie par GitHub (gratuit pour les repos publics).
- `actions/checkout@v4` : récupère le code du repo dans la VM.
- `actions/setup-python@v5` : installe la version Python demandée.
- L'ordre des `steps:` est séquentiel — chaque étape doit réussir pour passer à la suivante.
- La config `pythonpath = ["src"]` dans `pyproject.toml` évite d'avoir à exporter `PYTHONPATH=src`.
