# TP3 — LLM dans la CI : revue de code automatique sur les PR

## Objectif

Faire commenter automatiquement chaque Pull Request par un LLM (DeepSeek). À chaque ouverture ou mise à jour d'une PR, un workflow récupère le diff via l'API GitHub, l'envoie à DeepSeek, et publie le retour structuré comme commentaire de PR.

## Pré-requis : créer le secret GitHub

1. Aller dans le repo sur GitHub : **Settings → Secrets and variables → Actions → New repository secret**.
2. Nom : `DEEPSEEK_API_KEY`. Valeur : la clé d'API DeepSeek (depuis platform.deepseek.com).
3. Sauvegarder. Le secret n'est **jamais** affiché en clair, y compris dans les logs.

## À faire en classe (par le prof)

1. Vérifier que `scripts/deepseek_review.py` est présent dans le repo (il est déjà fourni).
2. Créer le workflow `.github/workflows/ai-review.yml` (voir bloc plus bas, ou copier depuis `docs/workflows/ai-review.yml`).
3. Commit + push sur `main`.
4. Créer une branche de démo, modifier une fonction, ouvrir une PR → observer le job `ai-review` se lancer, puis le commentaire IA apparaître sur la PR avec le tableau de remarques.

## À faire ensuite (revue croisée entre étudiants)

1. Chaque étudiant ouvre une PR avec une nouvelle fonction + son test (sur sa branche `feature/<prenom>-tp3`).
2. **Chaque étudiant est assigné comme reviewer d'une PR d'un autre étudiant** (le prof distribue).
3. L'étudiant lit le diff, lit le commentaire IA, et écrit sa **propre** review (Approve / Request changes / Comment) en justifiant.
4. Discussion : sur quels points l'IA a-t-elle été utile ? Sur quels points est-elle passée à côté ?

## Fichier — `.github/workflows/ai-review.yml`

```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  ai-review:
    name: AI Code Review
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

      - name: Run AI Code Review
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: python scripts/deepseek_review.py
```

## Ce que fait `scripts/deepseek_review.py`

Le script fait trois choses dans l'ordre :

1. **Récupère le diff** de la PR via l'API GitHub (endpoint `/repos/{repo}/pulls/{pr}/files`).
2. **Envoie le diff à DeepSeek** (`deepseek-v4-flash`) avec un prompt demandant une réponse JSON structurée.
3. **Poste un commentaire** sur la PR avec un tableau Markdown : Sévérité | Fichier | Remarque.

La réponse attendue de DeepSeek est un objet JSON :
```json
{
  "summary": "Courte évaluation globale.",
  "issues": [
    { "file": "src/tp_app/calculator.py", "line": 12, "severity": "warning", "comment": "..." }
  ]
}
```

Les sévérités sont rendues avec des emojis : 🔴 critical, 🟡 warning, 🟢 suggestion.

## Points pédagogiques

- **Sécurité des secrets** : `DEEPSEEK_API_KEY` n'est jamais visible dans les logs (GitHub masque automatiquement la valeur). Ne **jamais** committer la clé en clair — GitLeaks (TP sécurité) le détecterait.
- **`GITHUB_TOKEN`** : fourni automatiquement par GitHub à chaque run, scope limité au repo, expire à la fin du job. Pas besoin de le créer manuellement.
- **`permissions:`** : par défaut, `GITHUB_TOKEN` est en lecture seule. Il faut explicitement `pull-requests: write` pour pouvoir commenter, et `issues: write` pour l'endpoint issues utilisé par le script.
- **API GitHub vs git diff** : le script appelle l'API REST GitHub pour obtenir le diff (plus fiable en CI que `git diff` qui nécessite un historique complet).
- **Réponse JSON structurée** : demander au LLM un format JSON précis plutôt que du texte libre facilite le post-traitement et rend le commentaire plus lisible.
- **Coût** : chaque PR consomme du crédit DeepSeek. À monitorer sur le dashboard DeepSeek.
- **Limites du LLM** : il voit seulement le diff, pas le projet entier. Il peut halluciner des défauts ou rater de vrais bugs. C'est un **assistant**, pas un remplaçant de la review humaine.
