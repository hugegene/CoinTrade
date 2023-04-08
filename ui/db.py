#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 14:15:15 2021

@author: eugene
"""

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
        
def init_db():
    db = get_db()

    # with current_app.open_resource('schema.sql') as f:
    #     db.executescript(f.read().decode('utf8'))
    for i in ["btc", "eth"]:
        db.executescript("""CREATE TABLE IF NOT EXISTS {0} 
                         (
                         `timestamp` TEXT PRIMARY KEY, 
                         `price` FLOAT NOT NULL, 
                         `avg1` FLOAT, 
                         `avg2` FLOAT, 
                         `avg3` FLOAT,
                         `avg4` FLOAT,
                         `avg5` FLOAT,
                         `avg6` FLOAT, 
                         `flag1` TEXT,
                         `flag2` TEXT,
                         `flag3` TEXT,
                         `flag4` TEXT,
                         `flag5` TEXT,
                         `flag6` TEXT
                         )""".format(i))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
    
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)