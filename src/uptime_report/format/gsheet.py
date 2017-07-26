# -*- coding: utf-8 -*-
import arrow

try:
    import pygsheets
except ImportError:
    pygsheets = None


def write_to_sheet(out, data, fields, config):
    """Write data to a google spreadsheet."""
    gc = pygsheets.authorize(**config.get('authorization', {}))
    sh = gc.open(config.get('sheet', 'pingdom uptime report'))
    date_format = config.get('date_format', 'YYYY-MM-DD HH:mm:ss ZZ')
    date_string = arrow.utcnow().format(fmt=date_format)
    sheet_name = config.get('name_format', 'uptime report %d')
    sheet_name.replace('%d', date_string)
    wks = sh.add_worksheet(sheet_name, rows=50, cols=60)
    wks.update_cells('A1', fields)
    rows = []
    for obj in data:
        o = obj.for_json()
        rows.append([o[f] for f in fields])
    wks.update_cells('A2', rows)


Writer = write_to_sheet if pygsheets else None
