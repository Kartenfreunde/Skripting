import csv
import importlib.resources
import os
import shutil
from collections.abc import Sequence
from typing import Any, Optional, cast

import ResourceBundle.BundleTypes.BasicResourceBundle as res
from ResourceBundle.exceptions import NotInResourceBundleError
import git
from ResourceBundle.util.Locale import Locale
from github import Github

import resources
from category.planetarium import Planetarium

DATABASE_REPOSITORY_URL = "https://github.com/astronomieatlas-deutschland/Datenbank.git"
DATABASE_REPOSITORY_NAME = "astronomieatlas-deutschland/Datenbank"
DATABASE_REPOSITORY_USER = "astronomy-database-writer"
DATABASE_REPOSITORY_EMAIL = "astronomy-database-writer@t-online.de"
DATABASE_REPOSITORY_TOKEN_KEY = "DATABASE_REPOSITORY_TOKEN"
TEMP_DATABASE_DIRECTORY = "database_temp"
UPDATE_BRANCH_NAME = "unchecked_updates"

LANGUAGES = ["de"]


def publish_database(entries: Sequence[Planetarium], local_only: bool = False):
    if os.path.isdir(TEMP_DATABASE_DIRECTORY):
        git.rmtree(TEMP_DATABASE_DIRECTORY)

    print("Cloning database repository from " + DATABASE_REPOSITORY_URL)
    local_repo = git.Repo.clone_from(DATABASE_REPOSITORY_URL, TEMP_DATABASE_DIRECTORY)
    with local_repo.config_writer() as config_writer:
        config_writer.set_value("user", "name", "AstronomyDatabaseWriter")
        config_writer.set_value("user", "email", "adw@t-online.de")

    update_branch_found = False
    for ref in local_repo.references:
        if ref.name == "origin/" + UPDATE_BRANCH_NAME:
            local_repo.git.checkout("-t", "origin/" + UPDATE_BRANCH_NAME)
            update_branch_found = True
            break

    if not update_branch_found:
        local_repo.git.checkout("-b", UPDATE_BRANCH_NAME)

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

    local_repo.git.add(all=True)
    local_repo.git.commit(m="Automatic database update")

    if local_only:
        return

    print("Pushing changes")
    token = os.environ[DATABASE_REPOSITORY_TOKEN_KEY]
    local_repo.git.push(f"https://{DATABASE_REPOSITORY_USER}:{token}@github.com/"
                        f"astronomieatlas-deutschland/Datenbank.git", UPDATE_BRANCH_NAME)
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
    csv_dir_path = os.path.join(path, "csv")
    os.mkdir(csv_dir_path)
    raw_dir_path = os.path.join(csv_dir_path, "raw")
    os.mkdir(raw_dir_path)
    write_csv(os.path.join(raw_dir_path, f"planetariums_raw.csv"), None, entries)
    for language in LANGUAGES:
        lang_dir_path = os.path.join(csv_dir_path, language)
        os.mkdir(lang_dir_path)
        translations = cast(res.BasicResourceBundle, res.get_bundle("translations", Locale(language)))
        write_csv(os.path.join(lang_dir_path, f"planetariums_{language}.csv"), translations, entries)


def write_csv(path: str, translations: Optional[res.BasicResourceBundle], lines: Sequence[Any]):
    # ensure argument validity
    if len(lines) == 0:
        raise ValueError("Cannot write empty database file")
    first_type = type(lines[0])
    if not all(isinstance(line, first_type) for line in lines):
        raise ValueError("All line objects must be of same type")

    # write file
    with open(path, 'w', newline='', encoding="utf-8") as file:
        fieldnames = list(lines[0].__dict__.keys())
        if translations is not None:
            fieldnames = [translations.get(f) for f in fieldnames]
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for line in lines:
            row_dict = line.__dict__
            if translations is not None:
                row_dict = {translations.get(k): translate_value(v, translations)
                            for k, v in row_dict.items()}
            writer.writerow(row_dict)


def translate_value(value: object, resource_bundle: res.BasicResourceBundle) -> str:
    try:
        return resource_bundle.get(str(value))
    except NotInResourceBundleError:
        return str(value)
