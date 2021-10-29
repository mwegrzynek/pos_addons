def fiscal_ready_name(text):
    '''
    Remove characters rejected by a fiscal printer from
    product name
    '''
    replacements = {
        ')': '',
        '(': '',
        ',': '',
        '.': '',
        '.': '',
        ':': '',
        '-': '',
        '/': '',
    }
    return ''.join([replacements.get(c, c) for c in text])
