#!/usr/bin/env python
import argparse
import shutil
import subprocess
from github import Github
from string import ascii_lowercase

def parse_input(choice):
    try:
        if choice.isdecimal():
            choice = ascii_lowercase[int(choice) - 1]
    except IndexError as e:
        choice = None
    return choice


def git(*args):
    return subprocess.run(['git'] + list(args))

def search(keyword):
    gh = Github()
    return gh.search_repositories(keyword)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', help='Keyword or full repo name. If repo ' \
            'matches a search result\'s full repository name ' \
            '(e.g. "tmux/tmux"), clone that repository. Otherwise list ' \
            'search results to pick from.')
    parser.add_argument('clone_args', nargs=argparse.REMAINDER,
            help='Arguments passed to git clone.')
    args = parser.parse_args()
    print(args)
    keyword = args.repo
    clone_args = args.clone_args
    print(keyword)
    print(args.clone_args)

    repo_words = keyword.split('/')
    full_name = True if len(repo_words) == 2 else False
    print(full_name)
    print(repo_words)

    sr = search(keyword)
    print(len(sr))

    page = sr.get_page(0)
    print(page)
    num = min(10, len(page))
    x = 0

    term_cols = shutil.get_terminal_size((80, 20)).columns
    choices = dict()

    for repo in page[0:10]:
        letter = ascii_lowercase[x]
        number = x + 1
        choices[letter] = repo
        key = '({}) ({})'.format(x + 1, letter).rjust(8)
        data = '{} {} - {}'.format(key, repo.full_name, repo.description)
        line = (data[:term_cols - 3] + '...') if len(data) > term_cols else data
        print(line)
        x += 1

    i = input('Clone which repository? ')
    choice = parse_input(i)
    repo = choices.get(choice, None)

    if repo is None:
        print('Invalid choice: {}'.format(i))
        return
    print('Choice = {} - {}'.format(choice, repo.clone_url))
    git('clone', repo.clone_url, *clone_args)

if __name__ == '__main__':
    main()
