#!/usr/bin/env python

import os
import sqlite3
import logging
from urllib import urlencode, unquote

from flask import Flask, render_template, redirect
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
      name VARCHAR(255) NOT NULL
   ) ''' )

   cur.execute( '''CREATE TABLE IF NOT EXISTS pages (
      page_id INTEGER PRIMARY KEY,
      title VARCHAR(255) NOT NULL,
      created DATETIME NOT NULL
   ) ''' )

   cur.execute( '''CREATE INDEX IF NOT EXISTS title ON pages (title)''' )

   cur.execute( '''CREATE TABLE IF NOT EXISTS revisions (
      rev_id INTEGER NOT NULL,
      page_id INTEGER NOT NULL,
      updated DATETIME NOT NULL,
      body TEXT NOT NULL,
      PRIMARY KEY (rev_id, page_id),
      FOREIGN KEY (page_id) REFERENCES pages(page_id)
         ON DELETE CASCADE ON UPDATE NO ACTION
   ) ''' )

   cur.execute( '''CREATE TABLE IF NOT EXISTS pages_categories (
      cat_id INTEGER NOT NULL,
      page_id INTEGER NOT NULL,
      PRIMARY KEY (cat_id, page_id),
      FOREIGN KEY (cat_id) REFERENCES categories(cat_id)
         ON DELETE CASCADE ON UPDATE NO ACTION,
      FOREIGN KEY (page_id) REFERENCES pages(page_id)
         ON DELETE CASCADE ON UPDATE NO ACTION
   ) ''' )

def db_fetch_page( pagetitle ):
   cur = db_connect().cursor()
   page = cur.execute(
      '''SELECT r.updated, r.body, p.title, p.created
         FROM pages p
         LEFT JOIN revisions r ON r.page_id =p.page_id
         WHERE p.title = ?
         ORDER BY r.updated DESC
         LIMIT 1
      ''',
      (pagetitle.lower(),)
   ).fetchone()
   
   cur.close()

   return page

@app.route( '/' )
def route_root():
   return redirect( '/pages/Home' )

@app.route( '/edit/<pagetitle>' )
def route_edit( pagetitle ):
   pagetitle = unquote( pagetitle )

   page = db_fetch_page( pagetitle )
   
   if None == page:
      page = {
         'body': '',
         'updated': '',
         'title': pagetitle,
         'created': ''
      }

   return render_template( 'edit.html', page=page )

@app.route( '/pages/<pagetitle>' )
def route_index( pagetitle ):
   pagetitle = urldecode( pagetitle )
   page = db_fetch_page( pagetitle )
   if None == page:
      return redirect( '/edit/{}'.format( urlencode( pagetitle ) ) )  
   return render_template( 'page.html', page=page )

if '__main__' == __name__:
   app.run()

