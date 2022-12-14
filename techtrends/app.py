import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get the post count 
def get_post_count():
    connection = get_db_connection()
    post_count_row = connection.execute('SELECT count(*) FROM posts').fetchone()
    post_count = post_count_row['count(*)']
    connection.close()
    return post_count

db_connection_count = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

#Healthz endpoint for the service
@app.route('/healthz')
def healthz():
    response = app.response_class(
          response=json.dumps({"result":"OK - healthy"}),
          status=200,
          mimetype='application/json'
    )
    logging.debug('Healthz api invoked')
    return response
  
#Metrics endpoint for the service
@app.route('/metrics')
def metrics():
    post_count = get_post_count()
    logging.debug('metrics api invoked')
    return '{"db_connection_count": '+ str(db_connection_count) + ', "post_count": ' + str(post_count) + '}'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    logging.info('Index page loaded')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.error('A non-existing article ' + str(post_id) + ' is accessed and a 404 page is returned.')
      return render_template('404.html'), 404
    else:
      logging.info('Article ' + post['title'] + ' retrieved!')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info('The "About Us" page is retrieved.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            logging.error('Page creation attempted without title')
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logging.info('A new article is created with title ' + title + '.')
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
    # set logger to handle STDOUT and STDERR 
    stdout_handler =  logging.StreamHandler(sys.stdout)
    stdout_handler.level = logging.DEBUG
    stderr_handler =  logging.StreamHandler(sys.stderr)
    stderr_handler.level = logging.ERROR
    handlers = [stderr_handler, stdout_handler]
    # format output
    format_output = '%(name)s %(levelname)-8s %(asctime)s %(message)s' # formating output here
    logging.basicConfig(format=format_output, handlers=handlers)
    app.run(host='0.0.0.0', port='3111')
