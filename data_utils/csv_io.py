from json import dumps


def escape_csv_field(field):
    field = str(field)
    if ',' in field or '"' in field or '\n' in field:
        field = '"' + field.replace('"', '""') + '"'
    return field

def write_data(filename: str, data: dict | list[list]):
    ext = filename.split('.')[-1]
    if ext == 'json':
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(dumps(data, indent=2))
    elif ext == 'csv':
        with open(filename, 'w', encoding='utf-8') as file:
            lines = [''.join([','.join(escape_csv_field(x) for x in row)]) for row in data]
            file.write('\n'.join(lines) + '\n')
    else:
        print("Unsupported data type")
    print("Written: " + filename)