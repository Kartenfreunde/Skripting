import csv
import importlib.resources
import os
import shutil
from collections.abc import Sequence
from typing import Any

import git
from github import Github

from category.planetarium import Planetarium
import resources

DATABASE_REPOSITORY_URL = "https://github.com/astronomieatlas-deutschland/Datenbank.git"
DATABASE_REPOSITORY_NAME = "astronomieatlas-deutschland/Datenbank"
DATABASE_REPOSITORY_USER = "astronomy-database-writer"
DATABASE_REPOSITORY_EMAIL = "astronomy-database-writer@t-online.de"
DATABASE_REPOSITORY_TOKEN_KEY = "DATABASE_REPOSITORY_TOKEN"
TEMP_DATABASE_DIRECTORY = "database_temp"
UPDATE_BRANCH_NAME = "unchecked_updates"


def publish_database(entries: Sequence[Planetarium], local_only: bool = False):
    if os.path.isdir(TEMP_DATABASE_DIRECTORY):
        git.rmtree(TEMP_DATABASE_DIRECTORY)

    print("Cloning database repository from " + DATABASE_REPOSITORY_URL)
    local_repo = git.Repo.clone_from(DATABASE_REPOSITORY_URL, TEMP_DATABASE_DIRECTORY)
    with local_repo.config_writer() as config_writer:
        config_writer.set_value("user", "name", "AstronomyDatabaseWriter")
        config_writer.set_value("user", "email", "adw@t-online.de")

    print("Clearing database repository...")
    for repoFile in os.listdir(TEMP_DATABASE_DIRECTORY):
        if repoFile == ".git":
            continue
        repo_file_path = os.path.join(TEMP_DATABASE_DIRECTORY, repoFile)
        if os.path.isdir(repo_file_path):
            shutil.rmtree(os.path.join(TEMP_DATABASE_DIRECTORY, repoFile))
        else:
            os.remove(repo_file_path)

    print("Writing database...")
    with open(os.path.join(TEMP_DATABASE_DIRECTORY, "README.md"), "w") as readme_file:
        readme_file.write(importlib.resources.read_text(resources, "database_readme.md"))

    write_database(TEMP_DATABASE_DIRECTORY, entries)

    if not local_repo.is_dirty(untracked_files=True):
        print("Database did not change: No publishing necessary.")
        return

    print("Committing database changes to " + UPDATE_BRANCH_NAME)

    local_repo.git.checkout("-b", UPDATE_BRANCH_NAME)
    local_repo.git.add(all=True)
    local_repo.git.commit(m="Automatic database update")

    if local_only:
        return

    print("Creating pull request for database changes")
    local_repo.git.push("origin", UPDATE_BRANCH_NAME)
    github_access = Github(os.environ[DATABASE_REPOSITORY_TOKEN_KEY])
    github_repo = github_access.get_repo(DATABASE_REPOSITORY_NAME)
    if github_repo.get_pulls(state='open', base='main', head=UPDATE_BRANCH_NAME).totalCount == 0:
        github_repo.create_pull(
            title="Automatic database update",
            body="Automatic database update",
            head=UPDATE_BRANCH_NAME,
            base="main"
        )

    print("Database repository updated successfully. Pull request created.")


def write_database(path: str, entries: Sequence[Planetarium]):
    write_csv(os.path.join(path, "planetariums.csv"), entries)


def write_csv(path: str, lines: Sequence[Any]):
    # ensure argument validity
    if len(lines) == 0:
        raise ValueError("Cannot write empty database file")
    first_type = type(lines[0])
    if not all(isinstance(line, first_type) for line in lines):
        raise ValueError("All line objects must be of same type")

    # write file
    with open(path, 'w', newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(lines[0].__dict__.keys()), delimiter=";")
        writer.writeheader()
        for line in lines:
            writer.writerow(line.__dict__)
