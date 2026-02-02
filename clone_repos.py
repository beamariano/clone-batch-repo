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
load_dotenv()

GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
GITLAB_GROUP = os.getenv('GITLAB_GROUP')
FOLDERS_TO_CLONE = os.getenv('FOLDERS_TO_CLONE', 'homeworks,projects').split(',')

GITLAB_API_URL = "https://gitlab.com/api/v4"


def get_group_projects(group_path):
    """Fetch all projects in a GitLab group"""
    encoded_group = quote(group_path, safe='')
    url = f"{GITLAB_API_URL}/groups/{encoded_group}/projects"
    
    headers = {
        'PRIVATE-TOKEN': GITLAB_TOKEN
    }
    
    params = {
        'per_page': 100,
        'include_subgroups': True
    }
    
    all_projects = []
    page = 1
    
    while True:
        params['page'] = page
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


def clone_with_sparse_checkout(repo_url, repo_name, folders):
    """Clone a repository with sparse checkout for specific folders"""
    print(f"\n{'='*60}")
    print(f"Cloning: {repo_name}")
    print(f"{'='*60}")
    
    # Add token to URL for authentication
    auth_url = repo_url.replace('https://', f'https://oauth2:{GITLAB_TOKEN}@')
    
    try:
        # Clone with no checkout
        print(f"Step 1: Cloning repository (no checkout)...")
        subprocess.run([
            'git', 'clone', '--filter=blob:none', '--no-checkout', auth_url, repo_name
        ], check=True)
        
        os.chdir(repo_name)
        
        # Initialize sparse checkout
        print(f"Step 2: Initializing sparse checkout...")
        subprocess.run(['git', 'sparse-checkout', 'init', '--cone'], check=True)
        
        # Set folders to checkout
        print(f"Step 3: Setting folders to clone: {', '.join(folders)}")
        subprocess.run(['git', 'sparse-checkout', 'set'] + folders, check=True)
        
        # Checkout the files
        print(f"Step 4: Checking out files...")
        subprocess.run(['git', 'checkout'], check=True)
        
        # Add node_modules to .gitignore if not already there
        gitignore_path = '.gitignore'
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                content = f.read()
            if 'node_modules' not in content:
                with open(gitignore_path, 'a') as f:
                    f.write('\nnode_modules/\n')
        else:
            with open(gitignore_path, 'w') as f:
                f.write('node_modules/\n')
        
        os.chdir('..')
        print(f"✓ Successfully cloned {repo_name}")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error cloning {repo_name}: {e}")
        os.chdir('..')
    except Exception as e:
        print(f"✗ Unexpected error with {repo_name}: {e}")
        if os.path.exists(repo_name):
            os.chdir('..')


def main():
    """Main function to orchestrate the cloning process"""
    print("GitLab Batch Repository Cloner")
    print(f"Group: {GITLAB_GROUP}")
    print(f"Folders to clone: {', '.join(FOLDERS_TO_CLONE)}")
    print("\nFetching repository list from GitLab...")
    
    projects = get_group_projects(GITLAB_GROUP)
    
    if not projects:
        print("No projects found or error occurred.")
        return
    
    print(f"\nFound {len(projects)} repositories")
    print("\nRepositories to clone:")
    for i, project in enumerate(projects, 1):
        print(f"  {i}. {project['name']}")
    
    # Create a directory for all cloned repos
    output_dir = 'batch-28-students'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    os.chdir(output_dir)
    
    print(f"\nStarting cloning process into './{output_dir}' directory...")
    
    for project in projects:
        repo_name = project['name']
        repo_url = project['http_url_to_repo']
        
        # Skip if already cloned
        if os.path.exists(repo_name):
            print(f"\n⊙ Skipping {repo_name} (already exists)")
            continue
        
        clone_with_sparse_checkout(repo_url, repo_name, FOLDERS_TO_CLONE)
    
    os.chdir('..')
    
    print("\n" + "="*60)
    print("✓ All repositories processed!")
    print(f"Repositories are in the './{output_dir}' directory")
    print("="*60)


if __name__ == "__main__":
    main()
