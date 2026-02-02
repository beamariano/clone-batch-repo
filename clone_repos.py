#!/usr/bin/env python3
"""
GitLab Batch Repository Cloner
Clones all student repositories from a GitLab group with sparse checkout
to only include specific folders (homeworks, projects) while excluding node_modules
"""

import os
import subprocess
import requests
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables
load_dotenv(".env.local")

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
GITLAB_GROUP = os.getenv("GITLAB_GROUP")
FOLDERS_TO_CLONE = os.getenv("FOLDERS_TO_CLONE", "Homeworks,Projects").split(",")

GITLAB_API_URL = "https://gitlab.com/api/v4"


def get_subgroups(group_path):
    """Fetch all subgroups (students) in a GitLab group"""
    encoded_group = quote(group_path, safe="")
    url = f"{GITLAB_API_URL}/groups/{encoded_group}/subgroups"

    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    params = {"per_page": 100}

    all_subgroups = []
    page = 1

    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error fetching subgroups: {response.status_code}")
            print(response.text)
            return []

        subgroups = response.json()
        if not subgroups:
            break

        all_subgroups.extend(subgroups)
        page += 1

    return all_subgroups


def get_subgroup_projects(subgroup_id):
    """Fetch all projects in a specific subgroup (including nested)"""
    url = f"{GITLAB_API_URL}/groups/{subgroup_id}/projects"

    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    params = {"per_page": 100, "include_subgroups": True}

    all_projects = []
    page = 1

    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error fetching projects: {response.status_code}")
            print(response.text)
            return []

        projects = response.json()
        if not projects:
            break

        all_projects.extend(projects)
        page += 1

    return all_projects


def clone_repo(repo_url, repo_name):
    """Clone a repository (full) and remove node_modules after"""
    print(f"  Cloning: {repo_name}")

    # Add token to URL for authentication
    auth_url = repo_url.replace("https://", f"https://oauth2:{GITLAB_TOKEN}@")

    try:
        # Remove existing directory if present
        if os.path.exists(repo_name):
            subprocess.run(["rm", "-rf", repo_name], check=False)

        # Full clone (all branches)
        subprocess.run(
            ["git", "clone", auth_url, repo_name],
            check=True,
            capture_output=True,
        )

        # Remove node_modules if present
        node_modules_path = os.path.join(repo_name, "node_modules")
        if os.path.exists(node_modules_path):
            subprocess.run(["rm", "-rf", node_modules_path], check=False)

        print(f"  ✓ Cloned {repo_name}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error cloning {repo_name}: {e.stderr.decode() if e.stderr else e}")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error with {repo_name}: {e}")
        return False


def main():
    """Main function to orchestrate the cloning process"""
    print("GitLab Batch Repository Cloner")
    print(f"Group: {GITLAB_GROUP}")
    print(f"Repos to clone: {', '.join(FOLDERS_TO_CLONE)}")
    print("\nFetching student subgroups from GitLab...")

    subgroups = get_subgroups(GITLAB_GROUP)

    if not subgroups:
        print("No subgroups (students) found or error occurred.")
        return

    print(f"\nFound {len(subgroups)} students")

    print("\nStudents to clone:")
    for i, subgroup in enumerate(subgroups, 1):
        print(f"  {i}. {subgroup['name']}")

    # Create a directory for all cloned repos
    output_dir = "batch-28-students"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    os.chdir(output_dir)

    print(f"\nStarting cloning process into './{output_dir}' directory...")

    success_count = 0
    for subgroup in subgroups:
        student_name = subgroup["name"]
        subgroup_id = subgroup["id"]

        print(f"\n--- Processing student: {student_name} ---")

        # Create student directory
        if not os.path.exists(student_name):
            os.makedirs(student_name)

        # Get projects (repos) for this student
        projects = get_subgroup_projects(subgroup_id)

        # Debug: show all repos found
        if projects:
            print(f"  Found repos: {[p['name'] for p in projects]}")
        else:
            print("  No repos found in this subgroup")

        # Filter to only homeworks and projects repos (case-insensitive)
        folders_lower = [f.lower() for f in FOLDERS_TO_CLONE]
        target_repos = [p for p in projects if p["name"].lower() in folders_lower]

        if not target_repos:
            print(f"  No {'/'.join(FOLDERS_TO_CLONE)} repos matched")
            continue

        for project in target_repos:
            repo_name = project["name"]
            repo_url = project["http_url_to_repo"]

            # Clone directly into student folder with repo name
            clone_path = os.path.join(student_name, repo_name)

            if clone_repo(repo_url, clone_path):
                success_count += 1

    os.chdir("..")

    print("\n" + "=" * 60)
    print(f"✓ Processed {len(subgroups)} students!")
    print(f"✓ Cloned {success_count} repositories")
    print(f"Repositories are in the './{output_dir}' directory")
    print("=" * 60)


if __name__ == "__main__":
    main()
