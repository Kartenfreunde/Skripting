import importlib.resources
import os
import shutil
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Optional, Callable

import git
from github import Github

from . import file_format
from .planetarium import Planetarium

DATABASE_REPOSITORY_URL = "https://github.com/astronomieatlas-deutschland/Datenbank.git"
DATABASE_REPOSITORY_NAME = "astronomieatlas-deutschland/Datenbank"
DATABASE_REPOSITORY_USER = "astronomy-database-writer"
DATABASE_REPOSITORY_EMAIL = "astronomy-database-writer@t-online.de"
DATABASE_REPOSITORY_TOKEN_KEY = "DATABASE_REPOSITORY_TOKEN"
TEMP_DATABASE_DIRECTORY = "database_temp"  # dir to which the DB repository is cloned
UPDATE_BRANCH_NAME = "unchecked_updates"  # the branch to which updates are published


@dataclass
class DatabaseFormat:
    name: str
    write: Callable[[str, Optional[str], Sequence[Any]], None]


LANGUAGES = ["de"]  # supported languages
FORMATS = [  # supported formats
    DatabaseFormat("csv", file_format.write_csv),
    DatabaseFormat("geojson", file_format.write_geojson)
]


def publish_database(entries: Sequence[Planetarium], local_only: bool = False):
    # the directory may already exist (e. g. from a previous run)
    if os.path.isdir(TEMP_DATABASE_DIRECTORY):
        git.rmtree(TEMP_DATABASE_DIRECTORY)

    print("Cloning database repository from " + DATABASE_REPOSITORY_URL)
    local_repo = git.Repo.clone_from(DATABASE_REPOSITORY_URL, TEMP_DATABASE_DIRECTORY)
    with local_repo.config_writer() as config_writer:
        config_writer.set_value("user", "name", "AstronomyDatabaseWriter")
        config_writer.set_value("user", "email", "adw@t-online.de")

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

    # now we clear the database and write it again from scratch
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
    shutil.copy(os.path.join(os.path.dirname(__file__), "database_readme.md"),
                os.path.join(TEMP_DATABASE_DIRECTORY, "README.md"))

    write_database(TEMP_DATABASE_DIRECTORY, entries)

    # check if something has changed
    if not local_repo.is_dirty(untracked_files=True):
        print("Database did not change: No publishing necessary.")
        return

    print("Committing database changes to " + UPDATE_BRANCH_NAME)

    local_repo.git.add(all=True)
    local_repo.git.commit(m="Automatic database update")

    if local_only:
        return

    print("Pushing changes")
    # get the token that we need to authenticate at github
    token = os.environ[DATABASE_REPOSITORY_TOKEN_KEY]
    local_repo.git.push(f"https://{DATABASE_REPOSITORY_USER}:{token}@github.com/"
                        f"{DATABASE_REPOSITORY_NAME}.git", UPDATE_BRANCH_NAME)
    github_access = Github(token)
    github_repo = github_access.get_repo(DATABASE_REPOSITORY_NAME)
    if github_repo.get_pulls(state='open', base='main', head=UPDATE_BRANCH_NAME).totalCount == 0:
        print("Creating pull request")
        github_repo.create_pull(
            title="Automatic database update",
            body="Automatic database update",
            head=UPDATE_BRANCH_NAME,
            base="main"
        )
        print("Pull request created. Database updated successfully.")
    else:
        print("Pull request does already exist. Database updated successfully.")


def write_database(path: str, entries: Sequence[Planetarium]):
    """
    Write the database using a three-level-structure: The root directory contains one directory per
    format (csv, geojson, ...), which in turn contain one directory per language each (and one for
    the raw, i. e. not translated, format). Each of those subdirectories contains a set of files
    which comprise the database in the chosen format.
    """
    for format in FORMATS:
        format_path = os.path.join(path, format.name)
        os.mkdir(format_path)
        # first, create the "raw" directory
        raw_format_path = os.path.join(format_path, "raw")
        os.mkdir(raw_format_path)
        format.write(os.path.join(raw_format_path, f"planetariums_raw.{format.name}"),
                     None, entries)
        # then the language specific ones
        for language in LANGUAGES:
            lang_format_path = os.path.join(format_path, language)
            os.mkdir(lang_format_path)
            format.write(os.path.join(lang_format_path, f"planetariums_{language}.{format.name}"),
                         language, entries)
