# TP5 — Sécurité : détection de secrets et audit des dépendances

## Objectif

Ajouter deux contrôles de sécurité automatiques qui tournent sur chaque push et chaque PR :
1. **GitLeaks** — détecte les secrets commités par erreur (clés API, tokens, mots de passe)
2. **pip-audit** — détecte les dépendances Python qui ont des vulnérabilités connues (CVEs)

## Pourquoi c'est important

| Sans sécurité CI | Avec sécurité CI |
|-----------------|-----------------|
| Un dev commit une clé API → elle est exposée publiquement | GitLeaks bloque la PR avant le merge |
| Une dépendance vulnérable en prod pendant des mois | pip-audit alerte dès qu'une CVE est détectée |

## À faire en classe (par le prof)

1. Créer le workflow `.github/workflows/security.yml` (voir bloc plus bas).
2. Commit + push sur `main`.
3. **Démo GitLeaks** : créer une branche, coller une fausse clé API dans un fichier :
   ```python
   API_KEY = "sk-1234567890abcdef"
   ```
   Push → observer GitLeaks bloquer la PR.
4. **Démo pip-audit** : montrer le rapport de vulnérabilités sur le dashboard.

## À faire ensuite par chaque étudiant

1. Créer une branche `feature/<prenom>-tp5`.
2. Introduire volontairement une fausse clé en dur dans le code.
3. Ouvrir une PR → constater que GitLeaks passe au rouge.
4. Supprimer la clé, utiliser `os.environ["MA_CLE"]` à la place → CI verte.

## Fichier — `.github/workflows/security.yml`

```yaml
name: Security

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

jobs:
  gitleaks:
    name: Detect secrets
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Run GitLeaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  pip-audit:
    name: Audit dependencies
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
          cache: "pip"
      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit -r requirements.txt
```

## Points pédagogiques

- **Deux jobs en parallèle** : `gitleaks` et `pip-audit` sont indépendants — même pattern que TP2.
- **GitLeaks scanne l'historique git** (`fetch-depth: 0` obligatoire) — un secret supprimé dans le dernier commit est quand même détecté s'il était dans un commit précédent. La bonne pratique : ne jamais committer un secret, même temporairement.
- **La bonne pratique pour les clés** : toujours passer par des variables d'environnement (`os.environ["MA_CLE"]`) ou des secrets GitHub, jamais en dur dans le code.
- **pip-audit vs Dependabot** : pip-audit vérifie à la demande dans la CI, Dependabot ouvre des PRs automatiquement quand une mise à jour de sécurité est disponible. Les deux sont complémentaires.
- **CVE** (Common Vulnerabilities and Exposures) : base de données publique des failles connues. pip-audit s'appuie dessus pour signaler les packages dangereux.
