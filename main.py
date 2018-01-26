#!/usr/bin/env python
import argparse
import shutil
import subprocess
from collections import OrderedDict
from github import Github
from string import ascii_lowercase

CHOICE_LIST = 'list'
CHOICE_FULL_NAME_MATCH = 'full_match'
CHOICE_FULL_NAME_NO_MATCH = 'full_no_match'
CHOICE_NONE = 'none'

def parse_input(choice, limit):
    choice = choice.lower()
    try:
        if choice.isdecimal():
            if int(choice) > limit:
                choice = None
            else:
                choice = ascii_lowercase[int(choice) - 1]
        elif ascii_lowercase.find(choice) >= limit:
            choice = None
    except IndexError as e:
        choice = None
    return choice

def git(*args):
    return subprocess.run(['git'] + list(args))

def search(keyword):
    gh = Github()
    return gh.search_repositories(keyword)

def parse_search_results(results):
    page = results.get_page(0)
    limit = min(len(page), len(ascii_lowercase))
    term_cols = shutil.get_terminal_size((80, 20)).columns

    repos = OrderedDict()
    i = 0
    for repo in page[0:limit]:
        letter = ascii_lowercase[i]
        number = i + 1
        repos[letter] = repo
        i += 1
    return repos

def get_choice(keyword, repos):
    repo_words = keyword.split('/')
    full_name = True if len(repo_words) == 2 else False
    choice = CHOICE_LIST
    if full_name:
        match = [repo for repo in repos.values() if repo.full_name == keyword]
        if len(match) == 1:
            choice = CHOICE_FULL_NAME_MATCH
    if len(repos) == 0:
        if full_name:
            choice = CHOICE_FULL_NAME_NO_MATCH
        else:
            choice = CHOICE_NONE
    return choice

def print_repos(repos, limit):
    if limit is None:
        limit = 10

    term_cols = shutil.get_terminal_size((80, 20)).columns
    i = 0
    lines = []
    for letter, repo in list(repos.items())[:limit]:
        # Set length of string to make items line up evenly
        str_len = 8
        key = '({}) ({})'.format(i + 1, letter).rjust(str_len)
        data = '{} {} - {}'.format(key, repo.full_name, repo.description)
        line = (data[:term_cols - 3] + '...') if len(data) > term_cols else data
        lines.append(line)
        i += 1
    print('\n'.join(lines))

def get_list_input_url(repos, limit=None):
    if limit is None:
        limit = 10
    print_repos(repos, limit)
    i = get_input('Clone which repository? ')
    letter = parse_input(i, limit)
    repo = repos.get(letter, None)

    if repo is None:
        print('Invalid choice: {}'.format(i))
        return None
    return repo.clone_url

def get_no_match_input_url(keyword):
    gh_url_format = 'https://github.com/{}.git'
    clone_url = gh_url_format.format(keyword)
    query = "Repository not found. Clone '{}' ? [y/n] ".format(clone_url)
    response = get_input(query)
    if response.lower() == 'y':
        return clone_url
    else:
        return None

def get_input(msg):
    try:
        return input(msg)
    except KeyboardInterrupt:
        exit()

def get_match_url(keyword, repos):
    match = [repo for repo in repos.values() if repo.full_name == keyword]
    return match[0].clone_url

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', help='Keyword or full repo name. If repo ' \
            'matches a search result\'s full repository name ' \
            '(e.g. "tmux/tmux"), clone that repository. Otherwise list ' \
            'search results to pick from.')
    parser.add_argument('clone_args', nargs=argparse.REMAINDER,
            help='Arguments passed to git clone.')
    args = parser.parse_args()
    keyword = args.repo
    clone_args = args.clone_args

    repos = parse_search_results(search(keyword))
    choice = get_choice(keyword, repos)
    clone_url = None

    if choice == CHOICE_NONE:
        print('No repositories found.')
        clone_url = None
    elif choice == CHOICE_LIST:
        clone_url = get_list_input_url(repos)
    elif choice == CHOICE_FULL_NAME_MATCH:
        clone_url = get_match_url(keyword, repos)
    elif choice == CHOICE_FULL_NAME_NO_MATCH:
        clone_url = get_no_match_input_url(keyword)

    if(clone_url == None):
        return
    else:
        git('clone', clone_url, *clone_args)

if __name__ == '__main__':
    main()
