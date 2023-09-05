from .marshall import *
from .keys import *

def generate_filter_object(filters, names, values):
    # filters : { attribute: '', value: '', range_value: '', condition: '', comparator: '' }
    expression = ''
    for index, filter in enumerate(filters):
        attribute = filter['attribute']
        value = filter['value']
        condition = filter['condition']
        comparator = filter['comparator']
        names[f'#F{index}'] = f'{attribute}'
        values[f':FVAL{index}'] = values
        if('range_value' in filter):
            range_value = filter['range_value']
            values[f':R_VAL{index}'] = range_value
            expression += f" {comparator} " + parse_filter_condition(
                name = f'#F{index}',
                value = f':FVAL{index}',
                condition = condition,
                range_value = f':R_VAL{index}'
            )
        expression += f" {comparator} " + parse_filter_condition(
            name = f'#F{index}',
            value = f':VAL{index}',
            condition = condition,
            range_value = f':R_VAL{index}'
        )

    return {
        'names': names,
        'values': values,
        'f_expression': expression.strip()
    }

def generate_projection_object(names, projection):
    if(projection is None or not bool(projection)): raise ValueError('The value of projection cannot be: ', projection)
    p_expression = []
    for index, attribute in enumerate(projection):
        exists = [a_hash for a_hash, a_name in names.items() if a_name == attribute]
        if(bool(exists)): 
            p_expression.append(exists[0])
        else:
            names[f'#P{index}'] = attribute
            p_expression.append(f'#P{index}')
    return dict(names = names, p_expression = ', '.join(p_expression))

def generate_scan_params(table, **kwargs):
    params, names, values = { 'TableName': table }, { }, { }
    if('projection' in kwargs):
        params['ProjectionExpression'] = generate_projection_object(names=names, projection=kwargs.get('projection'))['p_expression']
        params['ExpressionAttributeNames'] = names
    if('filters' in kwargs):
        params['FilterExpression'] = generate_filter_object(names=names, values=values, filters=kwargs.get('filters'))['f_expression']
        params['ExpressionAttributeNames'] = names
        params['ExpressionAttributeValues'] = values
    if('limit' in kwargs):
        params['Limit'] = kwargs.get('limit')
    if('segment' in kwargs):
        params['Segment'] = kwargs.get('segment')
        params['TotalSegments'] = kwargs.get('total_segments')
    if('start_key' in kwargs):
        params['ExclusiveStartKey'] = kwargs.get('start_key')
    return params

def generate_query_params(table, partition, **kwargs):
    names, values = { '#KP': partition['attribute'] }, { ':KPV': { 'S': partition['value']} }
    params = { 'TableName': table, 'KeyConditionExpression': '#KP = :KPV' }
    if('sort' in kwargs):
        sort = kwargs.get('sort')
        names['#KS'], values[':KSV'] = sort['attribute'], {'S': sort['value']}
        sort_expression = parse_sort_condition(name = '#KS', value = ':KSV', condition = sort['condition'], range_value = sort['range_value']) if sort['condition'] == 'between' else parse_sort_condition(name = '#KS', value = ':KSV', condition = sort['condition'])
        params['KeyConditionExpression'] += f' AND {sort_expression}'
    if('projection' in kwargs):
        params['ProjectionExpression'] = generate_projection_object(names=names, projection=kwargs.get('projection'))['p_expression']
    if('filters' in kwargs):
        params['FilterExpression'] = generate_filter_object(names=names, values=values, filters=kwargs.get('filters'))['f_expression']
    if('index_name' in kwargs):
        params['IndexName'] = kwargs.get('index_name')
    if('limit' in kwargs):
        params['Limit'] = kwargs.get('limit')
    params['ExpressionAttributeNames'], params['ExpressionAttributeValues']  = names, values
    print("🚀 ~ file: parameters.py:83 ~ params:", params)
    return params

def generate_get_params(table, partition, **kwargs):
    params = { 'TableName': table, 'Key': { partition['attribute'] : partition['value'] } }
    if('sort' in kwargs):
        sort = kwargs.get('sort')
        params['Key'][sort['attribute']] = sort['value']
    if('projection' in kwargs):
        names = {}
        params['ProjectionExpression'] = generate_projection_object(names=names, projection=kwargs.get('projection'))['p_expression']
        params['ExpressionAttributeNames'] = names
    return params

def generate_put_params(table, put_item, return_old_items):
    return_attributes = 'ALL_OLD' if return_old_items else 'NONE'
    item = convert_to_attribute(put_item)
    return {
        'TableName': table,
        'Item': item,
        'ReturnAttributes': return_attributes
    }

def generate_update_params(table, partition, attributes, **kwargs):
    #TODO: nested attributes, ADD, DELETE
    if(not bool(attributes)): raise ValueError('No attributes to update -> ', attributes)
    params, expression, names, values = generate_get_params(table=table, partition=partition, sort=kwargs.get('sort')) if 'sort' in kwargs else generate_get_params(table=table, partition=partition, kwargs=kwargs), [], { }, { }
    for index, test in enumerate(attributes.items()):
        key, value = test
        names[f'#UA{index}'] = f'{key}'
        values[f':UVAL{index}'] = convert_to_attribute(value)
        expression.append(parse_update_expression(name=f'#UA{index}', value=f':UVAL{index}'))
    params['ReturnItems'] = parse_return_items(kwargs.get('returnItems')) if 'returnItems' in kwargs else 'NONE'
    params['UpdateExpression'] = 'SET ' + ', '.join(expression)
    params['ExpressionAttributeNames'] = names |+ params['ExpressionAttributeNames'] if 'ExpressionAttributeNames' in params else names
    params['ExpressionAttributeValues'] = values
    return params

def generate_delete_params(table, partition, **kwargs):
    params = generate_get_params(table=table, partition=partition, sort=kwargs.get('sort')) if 'sort' in kwargs else generate_get_params(table=table, partition=partition, kwargs=kwargs)
    params['ReturnItems'] = 'ALL_OLD' if 'returnItems' in kwargs else 'NONE'
    return params