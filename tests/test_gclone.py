import pytest
from collections import namedtuple
from gclone import parseopts
from gclone import Gclone, Gsearch
def assert_parseopts(args, expected):
    known_args, clone_args = parseopts(args)
    assert (vars(known_args), clone_args) == expected

def test_parseopts():
    # test 1
    args = ['--branch', 'master', '--depth=1', 'repo', 'dest']
    known_args = {
            'repo': 'repo',
            'sort': Gsearch.SORT_CHOICES[0],
            'order': Gsearch.ORDER_CHOICES[0],
            'limit': Gsearch.LIMIT_DEFAULT
            }
    clone_args = ['--branch=master', '--depth=1', 'dest']
    assert_parseopts(args, (known_args, clone_args))

    # test 2
    args = ['--branch', 'master', '--depth=1', 'repo', 'dest', '--sort',
            'updated', '--order=asc', '--limit', '50']
    known_args = {
            'repo': 'repo',
            'sort': 'updated',
            'order': 'asc',
            'limit': 50
            }
    clone_args = ['--branch=master', '--depth=1', 'dest']
    assert_parseopts(args, (known_args, clone_args))

    # test 3
    args = ['--branch', 'master', 'repo', '--depth=1', '--sort', 'updated',
            '--order=asc', 'dest', '--limit', '50']
    known_args = {
            'repo': 'repo',
            'sort': 'updated',
            'order': 'asc',
            'limit': 50
            }
    clone_args = ['--branch=master', '--depth=1', 'dest']
    assert_parseopts(args, (known_args, clone_args))

def test_gclone_none():
    gclone = Gclone('test', [])
    assert gclone._state == Gclone.STATE_NONE
    assert gclone.needs_input() == False

def test_gclone_no_match():
    gclone = Gclone('test/test', [])
    assert gclone._state == Gclone.STATE_FULL_NAME_NO_MATCH
    assert gclone.needs_input() == True

    with pytest.raises(KeyError):
        gclone.handle_input('k')
    with pytest.raises(KeyError):
        gclone.handle_input('')

    gclone.handle_input('y')
    assert gclone.get_clone_url() == 'https://github.com/test/test.git'
    gclone.handle_input('n')
    assert gclone.get_clone_url() is None

def test_gclone_match():
    Repo = namedtuple('Repo', ['full_name', 'description', 'clone_url'])
    repo1 = Repo('test/test', 'test desc', 'test.com/test.git')
    gclone = Gclone('test/test', [repo1])
    assert gclone._state == Gclone.STATE_FULL_NAME_MATCH
    assert gclone.needs_input() == False
    assert gclone.get_clone_url() == 'test.com/test.git'

def test_gclone_list():
    Repo = namedtuple('Repo', ['full_name', 'description', 'clone_url'])
    repo1 = Repo('test/test', 'test desc', 'test.com/test.git')
    repo2 = Repo('test/testa', 'testa desc', 'test.com/testa.git')
    gclone = Gclone('test', [repo1, repo2])
    assert gclone._state == Gclone.STATE_LIST
    assert gclone.needs_input() == True

    with pytest.raises(IndexError):
        gclone.handle_input('3')
    with pytest.raises(IndexError):
        gclone.handle_input('0')
    with pytest.raises(TypeError):
        gclone.handle_input('a')
    gclone.handle_input('1')
    assert gclone.get_clone_url() == 'test.com/test.git'

    gclone.handle_input('2')
    assert gclone.get_clone_url() == 'test.com/testa.git'
