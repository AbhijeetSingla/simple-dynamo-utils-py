def parse_filter_condition(name, value, condition, **kwargs):
    if(condition == 'equal'): return f'{name} = {value}'
    if(condition == 'notEqual'): return ' '.join([name, '<>', value])
    if(condition == 'lessThan'): return f'{name} < {value}'
    if(condition == 'lessThanEqual'): return f'{name} <= {value}'
    if(condition == 'greaterThan'): return f'{name} > {value}'
    if(condition == 'greaterThanEqual'): return f'{name} >= {value}'
    if(condition == 'between'):
        range_value = kwargs.get('range_value')
        return f'{name} BETWEEN {value} AND {range_value}'
    if(condition == 'beginsWith'): return f'begins_with ( {name}, {value} )'
    if(condition == 'startsWith'): return f'begins_with ( {name}, {value} )'
    if(condition == 'contains'): return f'contains ({name}, {value})'
    if(condition == 'listAppend'): return f'list_append ({name}, {value})'
    if(condition == 'exists'): return f'attribute_exists ({name})'
    if(condition == 'notExists'): return f'attribute_not_exists ({name})'
    if(condition == 'type'): return f'attribute_type ({name}, {value})'
    if(condition == 'size'): return f'begins_with ({name}, {value})'
    return ''

def parse_sort_condition(name, value, condition, **kwargs):
    if(condition == 'equal'): return f'{name} = {value}'
    if(condition == 'lessThan'): return f'{name} < {value}'
    if(condition == 'lessThanEqual'): return f'{name} <= {value}'
    if(condition == 'greaterThan'): return f'{name} > {value}'
    if(condition == 'greaterThanEqual'): return f'{name} >= {value}'
    if(condition == 'between'):
        range_value = kwargs.get('range_value')
        return f'{name} BETWEEN {value} AND {range_value}'
    if(condition == 'beginsWith'): return f'begins_with ( {name}, {value} )'
    if(condition == 'startsWith'): return f'begins_with ( {name}, {value} )'

def parse_update_expression(name, value, condition = 'equal'):
    if(condition == 'equal'): return f'{name} = {value}'
    if(condition == 'increment'): return f'{name} = {name} + {value}'
    if(condition == 'decrement'): return f'{name} = {name} - {value}'
    if(condition == 'equalIfNotExists'): return f'{name} = if_not_exists ({name, value})'
    if(condition == 'addToList'): return f'list_append ({name}, {value})'
    if(condition == 'removeIndex'): return f'{name}[{value}]'

def parse_return_items(state):
    if(state == 'all_old'): return 'ALL_OLD'
    if(state == 'all_new'): return 'ALL_NEW'
    if(state == 'updated_old'): return 'UPDATED_OLD'
    if(state == 'updated_new'): return 'UPDATED_NEW'
    return 'NONE'