# -*- coding: utf-8 -*-
try:
    import pygsheets
except ImportError:
    pygsheets = None


def write_to_sheet(out, data, fields, config):
    pygsheets.authorize(**config.get('authorization', {}))


Writer = write_to_sheet if pygsheets else None
