# Batch Repository Cloner

A CLI tool that batch-clones student repositories from a GitLab group, filtering to only the specified repo names (e.g. Homeworks, Projects).

## Prerequisites

**System:**
* Python 3
* git

**GitLab:**
* GitLab account with access to the target group
* Personal access token with `read_api` scope
* GitLab group path (e.g. `my-org/batch-28`)

## Configuration

Copy `.env` to `.env.local` and fill in your values. `.env.local` is gitignored and takes precedence over `.env`.

```bash
cp .env .env.local
```

| Variable | Required | Description |
|---|---|---|
| `GITLAB_TOKEN` | Yes | GitLab personal access token with `read_api` scope |
| `GITLAB_GROUP` | Yes | Full path of the GitLab group to clone from (e.g. `my-org/batch-28`) |
| `FOLDERS_TO_CLONE` | No | Comma-separated repo names to include (default: `Homeworks,Projects`) |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python clone_repos.py
```

Cloned repositories are saved to `./batch-28-students/<student-name>/<repo-name>/`. The output directory name is currently hardcoded in the script.
