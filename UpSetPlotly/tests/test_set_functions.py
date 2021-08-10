from UpSetPlotly.set_functions import get_all_intersects, order_sample_intersects


def test_get_all_intersects_returns():
    names = ['a', 'b', 'c']

    should_return = [{'samples': ('a',), 'elements': {1}, 'n': 1},
                     {'samples': ('b',), 'elements': set(), 'n': 0},
                     {'samples': ('c',), 'elements': {5, 6}, 'n': 2},
                     {'samples': ('a', 'b'), 'elements': {3, 4}, 'n': 2},
                     {'samples': ('a', 'c'), 'elements': set(), 'n': 0},
                     {'samples': ('b', 'c'), 'elements': set(), 'n': 0},
                     {'samples': ('a', 'b', 'c'), 'elements': {2}, 'n': 1}]

    returned = get_all_intersects([[1, 2, 3, 4], [2, 3, 4], [2, 5, 6]], names)
    assert returned == should_return

    returned = get_all_intersects([(1, 2, 3, 4), (2, 3, 4), (2, 5, 6)], names)
    assert returned == should_return

    returned = get_all_intersects([{1, 2, 3, 4}, {2, 3, 4}, {2, 5, 6}], names)
    assert returned == should_return

    returned = get_all_intersects([(1, 2, 3, 4), {2, 3, 4}, [2, 5, 6]], names)
    assert returned == should_return


def test_get_all_intersects_n():
    # the sum of all 'n' in the returned list should be equal to the total number of unique elements given

    samples = [range(1, 20), range(5, 15), range(7, 21), range(10, 30), range(28, 40), [1, 7, 11, 12, 25, 41]]
    samples = [list(x) for x in samples]
    unique = set()
    for sample in samples:
        unique = unique | set(sample)
    returned = get_all_intersects(samples)
    n = 0
    for x in returned:
        n += x['n']
    assert n == len(unique)


def test_order_sample_intersects_increasing():
    should_return = [{'samples': ('b',), 'elements': set(), 'n': 0},
                     {'samples': ('a', 'c'), 'elements': set(), 'n': 0},
                     {'samples': ('b', 'c'), 'elements': set(), 'n': 0},
                     {'samples': ('a',), 'elements': {1}, 'n': 1},
                     {'samples': ('a', 'b', 'c'), 'elements': {2}, 'n': 1},
                     {'samples': ('c',), 'elements': {5, 6}, 'n': 2},
                     {'samples': ('a', 'b'), 'elements': {3, 4}, 'n': 2}]
    samples = [[1, 2, 3, 4], [2, 3, 4], [2, 5, 6]]
    names = ['a', 'b', 'c']

    intersects = get_all_intersects(samples, names)
    assert order_sample_intersects(intersects, 'increasing') == should_return


def test_order_sample_intersects_decreasing():
    should_return = [{'samples': ('c',), 'elements': {5, 6}, 'n': 2},
                     {'samples': ('a', 'b'), 'elements': {3, 4}, 'n': 2},
                     {'samples': ('a',), 'elements': {1}, 'n': 1},
                     {'samples': ('a', 'b', 'c'), 'elements': {2}, 'n': 1},
                     {'samples': ('b',), 'elements': set(), 'n': 0},
                     {'samples': ('a', 'c'), 'elements': set(), 'n': 0},
                     {'samples': ('b', 'c'), 'elements': set(), 'n': 0}]
    samples = [[1, 2, 3, 4], [2, 3, 4], [2, 5, 6]]
    names = ['a', 'b', 'c']

    intersects = get_all_intersects(samples, names)
    assert order_sample_intersects(intersects, 'decreasing') == order_sample_intersects(intersects) == should_return
