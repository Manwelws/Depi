def reverse_string(s: str) -> str:
    """
    Reverse given string

    Args:
        s: string, to be reversed

    Returns:
        s_reversd: given string reversed
    """

    lst = s.split(" ")
    s = " ".join(lst[::-1])

    return s
