from typing import List, Set, Union, Dict
import itertools


def get_all_intersects(samples: Union[List[List], List[Set]], names: List[str] = None) -> List[Dict]:
    """
    Get the elements unique to all possible intersections of a list of lists or sets. Lists will automatically be
    converted to sets.
    :param samples: A list of lists or sets (the samples). These are the sets of elements which will be compared.
    :param names: Names for the respective samples. They must be unique. If None, sequential integers will be used.
    :return: A list of dictionaries of form {'samples': [samples], 'elements': [elements unique to these samples],
    'n': [number of elements]}
    """

    if names:
        if not len(samples) == len(names):
            raise ValueError('the length of samples and names must be equal.')
    else:
        # if there are no names provided, use sequential integers starting at 1
        names = [str(x) for x in range(1, len(samples) + 1)]

    # put the samples in a dictionary, making sure everything is sets
    sets = {name: set(x) for name, x in zip(names, samples)}

    # get all possible combinations of samples
    possible_intersects = []
    for i in range(1, len(samples) + 1):
        possible_intersects += list(itertools.combinations(names, i))

    # now get a list that is the compliment, i.e. the samples not in each possible combination
    compliment_sets = []
    for intersect in possible_intersects:
        compliment_sets.append(tuple([x for x in names if x not in intersect]))  # as a tuple to be consistent

    # and now get the actual intersects
    intersects = []
    for intersect in possible_intersects:
        S = sets[intersect[0]]
        for name in intersect:
            S = S & sets[name]
        intersects.append(S)

    # remove any elements found in the compliment sets
    for i in range(len(intersects)):
        intersect = intersects[i]
        compliment = compliment_sets[i]
        for c_s in compliment:
            intersect = intersect - sets[c_s]
        intersects[i] = intersect

    out = [{'samples': intersect, 'elements': elements, 'n': len(elements)}
           for intersect, elements in zip(possible_intersects, intersects)]
    return out
