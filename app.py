from os import environ
from random import randint, choice
from inspect import cleandoc
from pathlib import Path
from flask import Flask, g, request, render_template, abort
import sqlite3

app = Flask(__name__)

app.secret_key = environ.get('SECRET_KEY', '1234')

DATABASE_PATH = Path(__file__).parent / 'data/flask_shop.db'


def get_conn():
    if 'conn' not in g:     # hasattr(g, 'conn')
        app.logger.debug(f"» New Connection requested from endpoint '{request.endpoint}'")
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        g.conn = conn       # setattr(g, 'conn', conn)

    return g.conn


@app.before_request
def load_categories():
    '''
    Load categories, needed by menu
    '''

    # Quick return if request comes from static asset
    if not request or request.endpoint == 'static':
        return

    if not hasattr(g, 'categories'):
        cur = get_conn().cursor()
        categories = cur.execute(
            '''
            SELECT [id], [title], [parent], [other]
            FROM [product_category]
            '''
        ).fetchall()

        setattr(g, 'categories', categories)


@app.teardown_request
def teardown_request(ctx):
    '''
    Close connection on request teardown
    '''
    if hasattr(g, 'conn'):
        app.logger.debug('» Teardown Request')
        app.logger.debug('» Connection closed')
        g.conn.close()


@app.teardown_appcontext
def close_connection(ctx):
    '''
    Close connection on appcontext teardown
    This will fire whether there was an exception or not
    '''
    if conn := g.pop('conn', None):
        app.logger.debug('» Teardown AppContext')
        app.logger.debug('» Connection closed')
        conn.close()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/products/<category_id>')
def product_list(category_id):
    params = {'category_id': category_id}

    cur = get_conn().cursor()
    category = cur.execute(
        '''
        SELECT [id], [title], [parent]
        FROM [product_category]
        WHERE [id] = :category_id
        ''', params
    ).fetchone()
    cur.close()

    if not category:
        abort(404)

    cur = get_conn().cursor()
    products = cur.execute(
        '''
        SELECT [id], [title], [description], [price], [discount_ratio], [stock], [is_hot]
        FROM [product]
        WHERE [product_category_id] = :category_id
        ''', params
    ).fetchall()
    cur.close()

    if not products:
        abort(404)

    return render_template('products/list.html', category=category, products=products)


@app.route('/products/<category_id>/<int:product_id>')
def product_details(category_id, product_id):
    cur = get_conn().cursor()
    category = cur.execute(
        '''
        SELECT [id], [title], [parent]
        FROM [product_category]
        WHERE [id] = :category_id
        ''',
        {'category_id': category_id}
    ).fetchone()
    cur.close()

    if not category:
        abort(404)

    cur = get_conn().cursor()
    product = cur.execute(
        '''
        SELECT *
        FROM [product]
        WHERE [id] = :product_id
        ''',
        {'product_id': product_id}
    ).fetchone()
    cur.close()

    if not product:
        abort(404)

    return render_template('products/details.html', category=category, product=product)


@app.errorhandler(404)
def page_not_found(e):
    app.logger.debug(e)
    return render_template('errors/404.html'), 404


'''
Here be dragons
'''


''' @app.post('/products/<category_id>')
def add_to_cart(category_id):
    product_id = request.form.get('product-id')
    product = get_product(product_id)

    if not product:
        abort(500)

    cart = session.get('cart', [])
    cart.append([product, 1])

    app.logger.debug(cart)
    session['cart'] = cart

    return redirect(url_for('product_details', category_id=category_id, product_id=product_id)) '''


def insert_test_products(category):
    adjectives = (
        'Animal Print',
        'Awesome',
        'Casual',
        'Formal',
        'Gorgeous',
        'Floral',
        'Simple',
        'Standard',
        'Super',
        'Stunning',
        'Unique',
    )

    sizes = ('XS', 'S', 'M', 'L', 'XL')
    colors = ('green', 'yellow', 'pink', 'black', 'white')

    description = cleandoc(
        '''Lorem ipsum dolor sit amet, consectetur adipisicing elit.
        Numquam accusamus facere iusto,
        autem soluta amet sapiente ratione inventore nesciunt a,
        maxime quasi consectetur, rerum illum.'''
    ).replace('\n', '')

    conn = get_conn()
    cur = conn.cursor()
    cur.executemany(
        '''
        INSERT INTO [product] ([title], [description], [price], [discount_ratio], [stock], [is_hot], [product_category_id])
        VALUES (:title, :description, :price, :discount_ratio, :stock, :is_hot, :product_category_id)
        ''',
        ({'title': f"{adj} {category['title']}",
         'description': description,
          'price': randint(1000, 9999) / 100,
          'discount_ratio': 0 if choice((True, False, False)) else randint(0, 80) / 100,
          'stock': randint(0, 100),
          'is_hot': choice((True, False, False)),
          'product_category_id': category['id']} for adj in adjectives)
    )
    conn.commit()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(environ.get('SERVER_PORT', 5000)))
