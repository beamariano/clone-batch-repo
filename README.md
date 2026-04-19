# Batch Repository Cloner

A CLI tool that batch-clones student repositories from a GitLab group, filtering to only the specified sub-repository/folder names (e.g. Homeworks, Projects).

## Prerequisites

**System:**
* Python 3
* git

**GitLab:**
* GitLab account with access to the target group
* Personal access token. To create your own PAT, see: https://docs.gitlab.com/user/profile/personal_access_tokens/
* GitLab group ID. See: https://docs.gitlab.com/user/group/#find-the-group-id

## Configuration

Copy `.env` to `.env.local` and fill in your values. `.env.local` is gitignored and takes precedence over `.env`.

```bash
cp .env .env.local
```

| Variable | Required | Description |
|---|---|---|
| `GITLAB_TOKEN` | Yes | GitLab personal access token with `read_api` scope |
| `GITLAB_GROUP` | Yes | The group ID of the repository (e.g. `123456789`) |
| `FOLDERS_TO_CLONE` | No | Comma-separated repository/folder names to include (default: `Homeworks,Projects`) |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python clone_repos.py
```

Cloned repositories are saved to `./batch-01-students/<student-name>/<repo-name>/`. The output directory name is currently hardcoded in the script.
