# cnam-cicd-tp

Repo support de la **séance 2** du cours CNAM (CI/CD avec GitHub Actions).

Cinq TPs progressifs :

1. [TP1 — Premier workflow : pytest sur push](docs/tp1-pytest.md)
2. [TP2 — Job flake8 en parallèle](docs/tp2-flake8.md)
3. [TP3 — Revue de code automatique par LLM (DeepSeek)](docs/tp3-llm-review.md)
4. [TP4 — Déploiement continu sur Render](docs/tp4-deploy.md)
5. [TP5 — Sécurité : secrets et audit des dépendances](docs/tp5-security.md)

## Structure

```text
src/tp_app/          Code Python (calculator, text_tools, API FastAPI)
tests/               Tests pytest (unitaires + API)
scripts/             Script de revue IA (utilisé au TP3)
docs/                Énoncés des TPs
docs/workflows/      Workflows de référence à recopier dans .github/workflows/
render.yaml          Configuration de déploiement Render (TP4)
.github/workflows/   À construire pendant les TPs (vide au départ)
```

## Installation locale

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Commandes utiles

```bash
pytest -v                                          # lancer les tests
flake8 .                                           # vérifier le style
PYTHONPATH=src uvicorn tp_app.main:app --reload    # lancer l'API en local
```

## Règles de contribution pendant les TPs

1. Toujours partir de `main` à jour : `git checkout main && git pull`.
2. Créer une branche par TP : `feature/<prenom>-tp<n>-<sujet>`.
3. Faire des commits courts et lisibles.
4. Ouvrir une Pull Request vers `main`.
5. Attendre que la CI soit verte avant de merger.
6. À partir du TP3 : un autre étudiant doit reviewer la PR (en plus du commentaire IA).
