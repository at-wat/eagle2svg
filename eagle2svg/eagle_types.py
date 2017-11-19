def named_array(data):
    if data is None:
        return []
    key = list(data.keys())[0]
    if isinstance(data[key], list):
        return data[key]
    else:
        return [data[key]]


def array(data):
    if isinstance(data, list):
        return data
    else:
        return [data]
