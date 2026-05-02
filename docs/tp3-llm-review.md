# TP3 — LLM dans la CI : revue de code automatique sur les PR

## Objectif

Faire commenter automatiquement chaque Pull Request par un LLM (DeepSeek). À chaque ouverture ou mise à jour d'une PR, un workflow récupère le diff, l'envoie à l'API DeepSeek, et publie le retour comme commentaire de PR.

## Pré-requis : créer le secret GitHub

1. Aller dans le repo sur GitHub : **Settings → Secrets and variables → Actions → New repository secret**.
2. Nom : `DEEPSEEK_API_KEY`. Valeur : la clé d'API DeepSeek (depuis platform.deepseek.com).
3. Sauvegarder. Le secret n'est **jamais** affiché en clair, y compris dans les logs.

## À faire en classe (par le prof)

1. Créer le script `scripts/ai_review.py` (voir bloc plus bas).
2. Créer le workflow `.github/workflows/ai-review.yml` (voir bloc plus bas).
3. Commit + push sur `main`.
4. Créer une branche de démo, modifier une fonction, ouvrir une PR → observer le job `review` se lancer, puis le commentaire IA apparaître sur la PR.

## À faire ensuite (revue croisée entre étudiants)

1. Chaque étudiant ouvre une PR avec une nouvelle fonction + son test (sur sa propre branche `feature/<prenom>-tp3`).
2. **Chaque étudiant est assigné comme reviewer d'une PR d'un autre étudiant** (le prof distribue).
3. L'étudiant lit le diff, lit le commentaire IA, et écrit sa **propre** review (Approve / Request changes / Comment) en justifiant.
4. Discussion : sur quels points l'IA a-t-elle été utile ? Sur quels points est-elle passée à côté ?

## Fichier — `.github/workflows/ai-review.yml`

```yaml
name: AI Review

on:
  pull_request:
    types: [opened, synchronize]

permissions:
  pull-requests: write
  contents: read

jobs:
  review:
    name: Revue de code par DeepSeek
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install requests
      - name: Lancer la revue IA
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          BASE_SHA: ${{ github.event.pull_request.base.sha }}
          HEAD_SHA: ${{ github.event.pull_request.head.sha }}
        run: python scripts/ai_review.py
```

## Fichier — `scripts/ai_review.py`

```python
"""Envoie le diff d'une PR a DeepSeek et poste la reponse en commentaire."""

import os
import subprocess
import requests

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
MAX_DIFF_CHARS = 8000

PROMPT = (
    "Tu es un relecteur de code Python pour un cours CNAM. "
    "Donne 3 a 5 remarques concises sur ce diff (qualite, lisibilite, "
    "bugs potentiels, nommage). Reponds en francais, format liste a puces. "
    "Si le diff est trivial, dis-le simplement."
)


def get_diff(base: str, head: str) -> str:
    result = subprocess.run(
        ["git", "diff", f"{base}..{head}"],
        capture_output=True, text=True, check=True,
    )
    diff = result.stdout
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n... (diff tronque)"
    return diff


def call_deepseek(diff: str) -> str:
    api_key = os.environ["DEEPSEEK_API_KEY"]
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": f"{PROMPT}\n\n```diff\n{diff}\n```"}
        ],
    }
    resp = requests.post(
        DEEPSEEK_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def post_comment(body: str) -> None:
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    token = os.environ["GITHUB_TOKEN"]
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json={"body": body},
        timeout=30,
    )
    resp.raise_for_status()


def main() -> None:
    diff = get_diff(os.environ["BASE_SHA"], os.environ["HEAD_SHA"])
    if not diff.strip():
        print("Diff vide, on n'envoie rien.")
        return
    review = call_deepseek(diff)
    post_comment(f"### Revue automatique (DeepSeek)\n\n{review}")
    print("Commentaire poste avec succes.")


if __name__ == "__main__":
    main()
```

## Points pédagogiques

- **Sécurité des secrets** : `DEEPSEEK_API_KEY` n'est jamais visible dans les logs (GitHub masque automatiquement la valeur). Ne **jamais** commit la clé en clair.
- **`GITHUB_TOKEN`** : fourni automatiquement par GitHub à chaque run, scope limité au repo, expire à la fin du job.
- **`permissions:`** : par défaut, `GITHUB_TOKEN` est en lecture seule. Il faut explicitement `pull-requests: write` pour pouvoir commenter.
- **Coût** : chaque PR consomme du crédit DeepSeek. À monitorer.
- **Limites du LLM** : il voit seulement le diff, pas le projet entier. Il peut halluciner des défauts ou rater de vrais bugs. C'est un **assistant**, pas un remplaçant de la review humaine.
