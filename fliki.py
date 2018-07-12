#!/usr/bin/env python

import os
import sqlite3
import logging
from urllib import urlencode

from flask import Flask, render_template
app = Flask( __name__ )

def db_connect():
   conn = sqlite3.connect( 'pages.db' )
   return conn
   
@app.before_first_request
def app_setup():
   cur = db_connect().cursor()

   logging.basicConfig( loglevel=logging.INFO )
   logger = logging.getLogger( 'setup' )
   logger.info( 'Setting up DB...' )

   cur.execute( '''CREATE TABLE IF NOT EXISTS categories (
      cat_id INTEGER PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
   ); ''' )

   cur.execute( '''CREATE TABLE IF NOT EXISTS pages (
      page_id INTEGER PRIMARY KEY,
      title text NOT NULL,
      created DATETIME NOT NULL,
   ); ''' )

   cur.execute( '''CREATE INDEX IF NOT EXISTS title ON pages (route) ASC''' )

   cur.execute( '''CREATE TABLE IF NOT EXISTS revisions (
      rev_id INTEGER NOT NULL,
      page_id INTEGER NOT NULL,
      updated DATETIME NOT NULL,
      body TEXT NOT NULL,
      PRIMARY KEY (rev_id, page_id),
      FOREIGN KEY (page_id) REFERENCES pages(page_id)
         ON DELETE CASCADE ON UPDATE NO ACTION,
   ); ''' )

   cur.execute( '''CREATE TABLE IF NOT EXISTS pages_categories (
      cat_id INTEGER NOT NULL,
      page_id INTEGER NOT NULL,
      PRIMARY KEY (cat_id, page_id),
      FOREIGN KEY (cat_id) REFERENCES categories(cat_id)
         ON DELETE CASCADE ON UPDATE NO ACTION,
      FOREIGN KEY (page_id) REFERENCES pages(page_id)
         ON DELETE CASCADE ON UPDATE NO ACTION
   ); ''' )

@app.route( '/pages/<pagetitle>' )
def route_index():
   cur = db_connect().cursor()

   page = cur.execute(
      '''SELECT r.updated, r.body, p.title, p.create
         FROM pages p
         LEFT JOIN revisions r ON r.page_id =p.page_id
         WHERE p.title = ?''',
      pagetitle
   )

   return render_template( 'page.html', page=page )

if '__main__' == __name__:
   app.run()

