"""
This module implements different utility functions
which don't definitely fit somewhere else. It also serves
for dependency disentanglement purposes.
"""


def num_to_alpha(integer):
    """
    Transform integer to [a-z], [A-Z]

    Parameters
    ----------
    integer : int
        Integer to transform

    Returns
    -------
    a : str
        alpha-numeric representation of the integer
    """
    ascii = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if integer < 52:
        return ascii[integer]
    else:
        raise ValueError('Too large index for einsum')


def num_to_alnum(integer):
    """
    Transform integer to [a-z], [a0-z0]-[a9-z9]

    Parameters
    ----------
    integer : int
        Integer to transform

    Returns
    -------
    a : str
        alpha-numeric representation of the integer
    """
    ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    if integer < 26:
        return ascii_lowercase[integer]
    else:
        return ascii_lowercase[integer % 25 - 1] + str(integer // 25)
