from flask import Flask, render_template, request, flash, redirect, session
from urllib.parse import urlparse
import sqlite3
import scraper
import urllib
import requests
import random
import bs4

app = Flask(__name__)
app.secret_key = 'asdfghjhgfdsawertyhbvtguhnbedcwsd23457987543456hbtyh76g7yg3456ef453erf345edfbhytrescvg@$('

connect = sqlite3.connect('shop_scanner.db')
connect.execute('CREATE TABLE IF NOT EXISTS shop_items(favicon_link TEXT, shop_name TEXT, item_name TEXT, item_url TEXT UNIQUE, old_price int, new_price int, purchased TEXT, product_id TEXT, ID INT, FOREIGN KEY (ID) REFERENCES users(ID))')
connect.execute('CREATE TABLE IF NOT EXISTS users(ID INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)')
connect.execute('INSERT OR IGNORE INTO users(username, password) VALUES ("master", "156543frfgbfsd4673242wasdv23544646756758442342323234")')
connect.close()

@app.route('/')
def login_home():
   return render_template('login_page.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
   session.clear()
   if 'user' in session:
      return redirect('/homepage')

   if request.method == 'POST':
      connect = sqlite3.connect('shop_scanner.db')
      command = connect.cursor()
      username = request.form['username']
      password = request.form['password']
      command.execute('SELECT * FROM users WHERE username =? and password =?', (username, password))
      row = command.fetchone()
      print(request.form.get("reg"))
      if request.form.get('log') == 'Login' and row is not None:
         session['user'] = row[0]
         return redirect('/homepage')
      elif request.form.get('reg') == 'Register':
         print("Here")
         command.execute('''INSERT OR IGNORE INTO users (username, password) VALUES (?,?)''', (username, password))
         connect.commit()
         command.execute('SELECT * FROM users WHERE username =? and password =?', (username, password))
         row = command.fetchone()
         session['user'] = row[0]
         return redirect('/homepage')
      else:
         return redirect('/')

def get_purchased_icon(purchased_db_value):
   return "cross.svg" if purchased_db_value else "tick.svg"

@app.route('/logout')
def logout():
   session.pop('user', None)
   return redirect('/')

@app.route('/homepage')
def homePage():
   if 'user' in session:
      try: 
         connect = sqlite3.connect('shop_scanner.db')
         connect.row_factory = sqlite3.Row

         command = connect.cursor()
         command.execute('select * from shop_items WHERE ID =?',(str(session['user'])))
         rows = command.fetchall(); 
         command.execute('select username from users WHERE ID =?',(str(session['user'])))
         user = command.fetchall()[0]["username"]

         return render_template('index.html',ord=ord, rows = rows, username = user, format = format)
      
      except Exception as e:
         return redirect('/')    

@app.route('/refresh_all', methods = ['POST', 'GET'])
def refresh_all():
   if 'user' in session:
      scraper.full_trigger_update(session['user'])
      return redirect('/homepage')
   else:
      return redirect('/')

@app.route('/refresh_item', methods = ['POST', 'GET'])
def refresh_item():
   if request.method == 'POST' and 'user' in session:
      url = request.form.get('select_item')
      connect = sqlite3.connect('shop_scanner.db')
      command = connect.cursor()
      command.execute("select product_id, new_price, old_price from shop_items WHERE item_url =?",[url],)
      parameters = command.fetchall()[0]
      scraper.single_trigger_update(parameters[0], parameters[1], parameters[2])
      return redirect('/homepage')
   else:
      return redirect('/')

@app.route('/bulk_item', methods = ['POST', 'GET'])
def bulk_item():
   if request.method == 'POST' and 'user' in session:
      show_ads = request.form.get('ads_check') == "on"
      
      item_dict = scraper.trigger_bulk(request.form.get('item_name'), show_ads)
      for item in item_dict:
         product_id = ""
         shop_name = item['source']
         item_name = item['title']
         old_price = item['extracted_price']
         item_url = item['link']
         favicon_url = f"https://www.google.com/s2/favicons?domain=https://{urlparse(item_url).netloc}&sz=256"
         try:   
            product_id = item['product_id']
         except:
            pass
         connect = sqlite3.connect('shop_scanner.db')
         command = connect.cursor()
         command.execute('''INSERT OR IGNORE INTO shop_items (favicon_link, shop_name,item_name,item_url,purchased, old_price, product_id, ID) 
            VALUES (?,?,?,?,'0',?,?,?)''',(favicon_url,shop_name, item_name, item_url, old_price, product_id, str(session['user'])) ) 
         connect.commit()
      return redirect('/homepage')

   else:
      return redirect('/')


@app.route('/delete_item', methods = ['POST', 'GET'])
def delete_item():
   urls = request.form.getlist('select_item')
   print(urls)
   connect = sqlite3.connect('shop_scanner.db')
   command = connect.cursor()
   for url in urls:
      command.execute('''DELETE FROM shop_items WHERE item_url = ?''',([url]))
   connect.commit()
   return redirect('/homepage')

@app.route('/purchased', methods = ['POST', 'GET'])
def purchased():
   body = request.get_json()
   connect = sqlite3.connect('shop_scanner.db')
   command = connect.cursor()
   command.execute("select purchased from shop_items WHERE item_url =?",(body[0],))
   bought = command.fetchone()[0]
   if bought == '0':
      command.execute('''UPDATE shop_items SET purchased = 1 WHERE item_url = ?''',(body[0],))
   else:
      command.execute('''UPDATE shop_items SET purchased = 0 WHERE item_url = ?''',(body[0],))
   connect.commit()
   return redirect('/homepage')

