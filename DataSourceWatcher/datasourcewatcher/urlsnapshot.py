import os
import re
import shutil
from typing import Dict
from urllib.parse import ParseResult, urlparse

import git
from github import Github

SNAPSHOT_REPOSITORY_URL = "https://github.com/astronomieatlas-deutschland/data-source-snapshots.git"
SNAPSHOT_REPOSITORY_NAME = "astronomieatlas-deutschland/data-source-snapshots"
SNAPSHOT_REPOSITORY_USER = "data-source-watcher"
SNAPSHOT_REPOSITORY_EMAIL = "data-source-watcher1@t-online.de"
SNAPSHOT_REPOSITORY_TOKEN_KEY = "SNAPSHOT_REPOSITORY_TOKEN"
TEMP_SNAPSHOT_DIRECTORY = "snapshots_temp"  # dir to which the snapshot repository is cloned
UPDATE_BRANCH_NAME = "data_changes"  # the branch to which updates are published


def publish_snapshots(snapshots: Dict[str, str], local_only=False):
    # the directory may already exist (e. g. from a previous run)
    if os.path.isdir(TEMP_SNAPSHOT_DIRECTORY):
        git.rmtree(TEMP_SNAPSHOT_DIRECTORY)

    print("Cloning snapshot repository from " + SNAPSHOT_REPOSITORY_URL)
    local_repo = git.Repo.clone_from(SNAPSHOT_REPOSITORY_URL, TEMP_SNAPSHOT_DIRECTORY)
    with local_repo.config_writer() as config_writer:
        config_writer.set_value("user", "name", "DataSourceWatcher")
        config_writer.set_value("user", "email", "dsw@t-online.de")

    # check whether our branch already exists in the remote - if it does, we start our local
    # update-branch from that and track it; otherwise, we create it starting at the main branch
    update_branch_found = False
    for ref in local_repo.references:
        if ref.name == "origin/" + UPDATE_BRANCH_NAME:
            local_repo.git.checkout("-t", "origin/" + UPDATE_BRANCH_NAME)
            update_branch_found = True
            break

    if not update_branch_found:
        local_repo.git.checkout("-b", UPDATE_BRANCH_NAME)

    # now we delete the snapshots and write them again from scratch
    print("Clearing snapshot repository...")
    for repoFile in os.listdir(TEMP_SNAPSHOT_DIRECTORY):
        if repoFile == ".git":
            continue
        repo_file_path = os.path.join(TEMP_SNAPSHOT_DIRECTORY, repoFile)
        if os.path.isdir(repo_file_path):
            shutil.rmtree(os.path.join(TEMP_SNAPSHOT_DIRECTORY, repoFile))
        else:
            os.remove(repo_file_path)

    print("Writing snapshots...")
    shutil.copy(os.path.join(os.path.dirname(__file__), "snapshots_readme.md"),
                os.path.join(TEMP_SNAPSHOT_DIRECTORY, "README.md"))

    _write_snapshots(TEMP_SNAPSHOT_DIRECTORY, snapshots)

    # check if something has changed
    if not local_repo.is_dirty(untracked_files=True):
        print("Snapshots did not change: No publishing necessary.")
        return

    print("Committing snapshot changes to " + UPDATE_BRANCH_NAME)

    local_repo.git.add(all=True)
    local_repo.git.commit(m="Data source snapshot update")

    if local_only:
        return

    print("Pushing changes")
    # get the token that we need to authenticate at github
    token = os.environ[SNAPSHOT_REPOSITORY_TOKEN_KEY]
    local_repo.git.push(f"https://{SNAPSHOT_REPOSITORY_USER}:{token}@github.com/"
                        f"{SNAPSHOT_REPOSITORY_NAME}.git", UPDATE_BRANCH_NAME)
    github_access = Github(token)
    github_repo = github_access.get_repo(SNAPSHOT_REPOSITORY_NAME)
    if github_repo.get_pulls(state='open', base='main', head=UPDATE_BRANCH_NAME).totalCount == 0:
        print("Creating pull request")
        github_repo.create_pull(
            title="Data source changes",
            body="Data source changes",
            head=UPDATE_BRANCH_NAME,
            base="main"
        )
        print("Pull request created. Snapshots updated successfully.")
    else:
        print("Pull request does already exist. Snapshots updated successfully.")


def _write_snapshots(path: str, snapshots: Dict[str, str]):
    for url, content in snapshots.items():
        parsed_url: ParseResult = urlparse(url)
        subdir = re.sub("[^a-zA-Z0-9]", "_", parsed_url.netloc)
        if all(len(i) == 0 for i in parsed_url[2:5]):
            file = "root"
        else:
            file = "_".join([re.sub("[^a-zA-Z0-9]", "_", s) for s in parsed_url[2:5] if len(s) > 0])
            file = file.strip("_")
        file += ".html"
        os.makedirs(os.path.join(path, subdir), exist_ok=True)
        with open(os.path.join(path, subdir, file), "w") as f:
            f.write(content)
