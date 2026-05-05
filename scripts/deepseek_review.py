import os
import sys
import json
import requests

DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]
PR_NUMBER = os.environ["PR_NUMBER"]

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
GITHUB_API = "https://api.github.com"

HEADERS_GH = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_pr_diff():
    url = f"{GITHUB_API}/repos/{REPO}/pulls/{PR_NUMBER}"
    resp = requests.get(
        url,
        headers={**HEADERS_GH, "Accept": "application/vnd.github.v3.diff"},
    )
    resp.raise_for_status()
    return resp.text


def get_pr_files():
    url = f"{GITHUB_API}/repos/{REPO}/pulls/{PR_NUMBER}/files"
    resp = requests.get(url, headers=HEADERS_GH)
    resp.raise_for_status()
    return resp.json()


def review_diff(diff, files):
    files_list = "\n".join(f["filename"] for f in files)
    prompt = f"""You are a senior software engineer reviewing a pull request. Analyze the diff below and provide a concise, actionable code review.

Changed files:
{files_list}

Diff:
{diff}

Respond with a JSON object containing:
- "summary": a short overall assessment (2-3 sentences)
- "issues": an array of objects, each with "file", "line" (approximate), "severity" ("critical", "warning", or "suggestion"), and "comment" (actionable, specific).
Only flag real problems — do not nitpick style unless it's a bug or a maintainability concern."""

    resp = requests.post(
        DEEPSEEK_URL,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-v4-flash",
            "messages": [
                {"role": "system", "content": "You are a code review assistant. Always respond with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        },
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
    return json.loads(content)


def post_review(review):
    summary = review.get("summary", "No summary provided.")
    issues = review.get("issues", [])

    body = f"## AI Code Review\n\n{summary}\n\n"
    if issues:
        body += "| Severity | File | Comment |\n"
        body += "|----------|------|--------|\n"
        for issue in issues:
            sev_emoji = {"critical": "🔴", "warning": "🟡", "suggestion": "🟢"}.get(
                issue.get("severity", "warning"), "🟡"
            )
            line = issue.get("line", "-")
            body += f"| {sev_emoji} {issue.get('severity', 'warning')} | `{issue.get('file', '?')}`:{line} | {issue.get('comment', '')} |\n"
    else:
        body += "_No issues found._"

    url = f"{GITHUB_API}/repos/{REPO}/issues/{PR_NUMBER}/comments"
    resp = requests.post(url, headers=HEADERS_GH, json={"body": body})
    resp.raise_for_status()
    print(f"Review posted: {resp.json()['html_url']}")


def main():
    print(f"Fetching diff for {REPO}#{PR_NUMBER}...")
    diff = get_pr_diff()
    files = get_pr_files()

    if not diff.strip():
        print("No diff found — skipping review.")
        return

    print(f"Reviewing {len(files)} file(s), {len(diff)} bytes of diff...")
    review = review_diff(diff, files)
    post_review(review)
    print("Done.")


if __name__ == "__main__":
    main()
