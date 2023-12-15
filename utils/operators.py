def bigger_than(a, b):
    return a > b


def smaller_than(a, b):
    return a < b


def equal(a, b):
    return a == b


def starts_with(a, b):
    return f'{a}'.startswith(f'{b}')


OPERATORS_FUNCTIONS_MAPPING: dict = {
    '=': equal,
    '>': bigger_than,
    '<': smaller_than,
    'starts_with': starts_with,
}
