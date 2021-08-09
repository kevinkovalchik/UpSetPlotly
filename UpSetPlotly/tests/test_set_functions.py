from UpSetPlotly.set_functions import get_all_intersects


def test_get_all_intersects():
    names = ['a', 'b', 'c']
    samples = [[1, 2, 3, 4], [2, 3, 4], [2, 5, 6]]

    should_return = [{'samples': ('a',), 'elements': {1}},
                     {'samples': ('b',), 'elements': set()},
                     {'samples': ('c',), 'elements': {5, 6}},
                     {'samples': ('a', 'b'), 'elements': {3, 4}},
                     {'samples': ('a', 'c'), 'elements': set()},
                     {'samples': ('b', 'c'), 'elements': set()},
                     {'samples': ('a', 'b', 'c'), 'elements': {2}}]

    returned = get_all_intersects(samples, names)

    assert returned == should_return
