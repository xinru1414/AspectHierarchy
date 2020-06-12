import pytest
from treeparser import parse, find_part_end


@pytest.mark.parametrize('inp', (
    "ParseTree('Elaboration[N][S]', ['asdf', 'sadf'])",
    "ParseTree('Elaboration[N][S]', [\"sad's toy\", 'sadf'])",
    "ParseTree('Joint[N][N]', ['( I am @ 170lbs', 'and my wife is pregnant @ around 140lbs ) .'])",
))
def test_parse(inp):
    parse(inp)


@pytest.mark.parametrize('inp, start, out', (
        ("['123']", 0, 6),
        ("['1,3']", 0, 6),
        ("['1]3']", 0, 6),
        ("['1\"3']", 0, 6),
        ("['123', '123']", 0, 6),
        ("['123', '123']", 7, 13),
        ('["123"]', 0, 6),
        ('["1,3"]', 0, 6),
        ('["1]3"]', 0, 6),
        ('["1\'3"]', 0, 6),
        ("['(a', 'b)']", 1, 5),
))
def test_find_part_end(inp, start, out):
    assert find_part_end(inp, start) == out