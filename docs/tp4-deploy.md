# TP4 — Déploiement continu sur Render

## Objectif

Fermer la boucle CI/CD : après que les tests passent sur `main`, déclencher automatiquement un déploiement de l'API FastAPI sur Render. Toute fusion vers `main` se traduit par une nouvelle version en production, sans intervention manuelle.

## Architecture du workflow

```
Push sur main
    └─► Job "test" (pytest)
            └─► Si vert → Job "deploy" (curl → Render webhook)
                                └─► Render pull le code, rebuild, redémarre
```

Le déploiement ne se déclenche **que si les tests passent** (`needs: test`). C'est la garantie minimale de qualité avant de toucher la production.

## Pré-requis : configurer Render

1. Créer un compte sur [render.com](https://render.com) et un **Web Service** pointant sur ce repo.
2. Dans les settings du service Render :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `PYTHONPATH=src python -m uvicorn tp_app.main:app --host 0.0.0.0 --port $PORT`
3. Récupérer le **Deploy Hook URL** : Settings → Deploy Hook → Copy URL.
4. Ajouter ce secret dans GitHub : **Settings → Secrets → Actions → New secret**, nom `RENDER_DEPLOY_HOOK_URL`.

## Fichier — `.github/workflows/deploy.yml`

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  test:
    name: Run tests before deploy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Run tests
        env:
          PYTHONPATH: src
        run: pytest -v

  deploy:
    name: Deploy to Render
    runs-on: ubuntu-latest
    needs: test
    steps:
      - name: Trigger Render deploy hook
        run: curl -f -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
```

## L'application déployée

L'API expose les endpoints suivants :

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/` | Statut de l'API |
| GET | `/health` | Health check (utilisé par Render) |
| POST | `/calc/add` | Addition |
| POST | `/calc/subtract` | Soustraction |
| POST | `/calc/multiply` | Multiplication |
| POST | `/calc/divide` | Division (400 si division par zéro) |
| POST | `/text/reverse` | Inverser une chaîne |
| POST | `/text/count-words` | Compter les mots |
| POST | `/text/slugify` | Convertir en slug |

La documentation interactive est disponible à `/docs` (Swagger UI généré automatiquement par FastAPI).

## À faire en classe

1. Montrer le workflow `deploy.yml` et expliquer `needs: test`.
2. Merger une PR propre vers `main` → observer dans l'onglet **Actions** les deux jobs s'enchaîner.
3. Aller sur le dashboard Render → montrer le déploiement se déclencher automatiquement.
4. Ouvrir l'URL Render publique → tester `/docs` et un endpoint depuis le navigateur.
5. **Démo d'échec** : merger une PR avec un test cassé → `test` rouge → `deploy` bloqué, Render ne reçoit rien.

## Points pédagogiques

- **`needs: test`** : c'est la clé. Sans lui, le déploiement se ferait même si les tests échouent.
- **Deploy hook vs intégration native** : le hook est une URL secrète que Render surveille. Appel HTTP = déploiement déclenché. Simple, mais sans retour de statut dans GitHub (le workflow ne sait pas si Render a réussi).
- **`curl -f`** : le flag `-f` fait échouer la commande si le serveur renvoie une erreur HTTP. Sans lui, `curl` réussirait même sur un 404.
- **Secrets vs variables d'environnement** : le hook URL est un secret (contient un token), pas une variable — ne jamais le coller en clair dans le YAML.
- **Health check** : Render appelle `/health` après chaque déploiement pour valider que l'app répond. Si `/health` ne renvoie pas 200, Render revient à la version précédente (rollback automatique).
