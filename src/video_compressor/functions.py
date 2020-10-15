from itertools import chain

def rangeSliceBySteps(start, stop, step=1):

    length = stop - start
    congruent_stop = start + (length - (length % step))

    for step_slice in map(lambda i: (i, step), range(start, congruent_stop, step)):
        yield step_slice

    if congruent_stop < stop:
        yield (congruent_stop, stop - congruent_stop)

