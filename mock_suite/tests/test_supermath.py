from sut.supermath import add
import os
import sys

import pytest
import random



@pytest.mark.color('red')
@pytest.mark.issue(issue_id='ISSUE-123')
@pytest.mark.component('Adder')
@pytest.mark.parametrize("a, b, e", [[1, 1, 2], [1, 2, 3], [3, 4, 7], [-1, 2, 1]])
def test_add(a, b, e):
    '''Testing adding fucntionality'''
    print('STD OUT')
    print('STD ERR', file=sys.stderr)
    assert add(a, b) == e


@pytest.mark.component('Randomizer')
@pytest.mark.color('green')
def test_random():
    '''Testing randomizer component'''
    value = random.randint(0,10)
    result = True
    if value <= 3:
        result = False
        print('Process has timed out', file=sys.stderr)

    assert value > 3

@pytest.mark.component('Failer')
@pytest.mark.color('blue')
def test_fail():
    '''Testing failer component, seems to be failing'''
    raise ValueError('Missing data')
    assert True

@pytest.mark.component('Skipper')
@pytest.mark.color('yellow')
def test_skip(secondary_properties):
    '''Skipper component will be skipping'''
    pytest.skip("skipping test")
