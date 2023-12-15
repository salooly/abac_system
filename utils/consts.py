TYPES_MAPPING: dict = {
    'string': str,
    'boolean': bool,
    'integer': int,
}

OPERATORS_ALLOWED_TYPES: dict = {
    '=': [str, bool, int],
    '>': [str, int],
    '<': [str, int],
    'starts_with': [str],

}
