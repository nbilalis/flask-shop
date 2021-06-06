from os import environ
from random import randint, choice, sample
from inspect import cleandoc
from flask import Flask, g, render_template

app = Flask(__name__)


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
    # css = render_template('css/product.css')
    return render_template('index.html')


@app.route('/products/<category_id>')
def product_list(category_id):
    category = get_category(category_id, get_all_categories())
    products = get_all_products()
    app.logger.debug(products)
    return render_template('products/list.html', category=category, products=products)


@app.route('/products/<category_id>/<product_id>')
def product_details(category_id, product_id):
    category = get_category(category_id, get_all_categories())
    product = get_product(product_id)
    return render_template('products/details.html', category=category, product=product)


@app.route('/products/<product_id>/api')
def get_product_json(product_id):
    return get_product(product_id)


@app.errorhandler(404)
def page_not_found(e):
    app.logger.debug(e)
    return render_template('errors/404.html'), 404


"""
Here be dragons!
Please ignore this section... or don't!
"""


@app.before_request
def store_stuff_in_g():
    """
    Executes before *every* request
    g is a global object to store stuff for a *single* request
    """
    g.products = get_all_products()
    g.categories = get_all_categories()


def get_category(id, categories):
    for category in categories:
        if id == category['id']:
            return category
        elif 'children' in category:
            if res := get_category(id, category['children']):
                return res
    else:
        return None


def get_product(id):
    adjectives = ('Super', 'Awesome', 'Unique', 'Gorgeous',
                  'Floral', 'Casual', 'Standard', 'Formal')
    items = ('Shirt', 'T-Shirt', 'Pants', 'Dress',
             'Blouse', 'Jeans', 'Trousers')
    sizes = ('XS', 'S', 'M', 'L', 'XL')
    colors = ('green', 'yellow', 'pink', 'black', 'white')

    description = cleandoc('''Lorem ipsum dolor sit amet, consectetur adipisicing elit.
        Numquam accusamus facere iusto,
        autem soluta amet sapiente ratione inventore nesciunt a,
        maxime quasi consectetur, rerum illum.''').replace('\n', '')

    is_sale = choice((True, False, False))
    is_sold_out = not is_sale and choice((True, False, False))
    is_hot = not is_sale and not is_sold_out and choice((True, False, False))

    return {
        'id': id,
        'title': f'{choice(adjectives)} {choice(items)}',
        'description': description,
        'long_description': ' '.join([description for i in range(10)]),
        'price': randint(1000, 9999) / 100,
        'discount_ratio': randint(0, 99) / 100 if is_sale else 0,
        'stock': randint(0, 100),
        'sizes': sample(sizes, randint(1, len(sizes))),
        'colors': sample(colors, randint(1, len(colors))),
        'is_sale': is_sale,
        'is_sold_out': is_sold_out,
        'is_hot': is_hot
    }


def get_all_products(n=12):
    return [get_product(f'{i:04}') for i in range(1, n+1)]


def get_all_categories():
    return [
        {
            'id': 'men',
            'title': 'Men',
            'children': [
                {'id': 'casual', 'title': 'Casual'},
                {'id': 'sports', 'title': 'Sports'},
                {'id': 'formal', 'title': 'Formal'},
                {'id': 'standard', 'title': 'Standard'},
                {'id': 't-shirts', 'title': 'T-Shirts'},
                {'id': 'shirts', 'title': 'Shirts'},
                {'id': 'jeans', 'title': 'Jeans'},
                {'id': 'trousers', 'title': 'Trousers'},
                {
                    'id': 'other',
                    'title': 'And more…',
                    'children': [
                        {'id': 'sleep-wear', 'title': 'Sleep Wear'},
                        {'id': 'sandals', 'title': 'Sandals'},
                        {'id': 'loafers', 'title': 'Loafers'}
                    ]
                }
            ]
        },
        {
            'id': 'women',
            'title': 'Women',
            'children': [
                {'id': 'kurta-n-kurti', 'title': 'Kurta & Kurti'},
                {'id': 'trousers', 'title': 'Trousers'},
                {'id': 'casual', 'title': 'Casual'},
                {'id': 'sports', 'title': 'Sports'},
                {'id': 'formal', 'title': 'Formal'},
                {'id': 'sarees', 'title': 'Sarees'},
                {'id': 'shoes', 'title': 'Shoes'},
                {
                    'id': 'other',
                    'title': 'And more…',
                    'children': [
                        {'id': 'sleep-wear', 'title': 'Sleep Wear'},
                        {'id': 'sandals', 'title': 'Sandals'},
                        {'id': 'loafers', 'title': 'Loafers'},
                        {
                            'id': 'other',
                            'title': 'And more…',
                            'children': [
                                {'id': 'Rings', 'title': 'Rings'},
                                {'id': 'Earrings', 'title': 'Earrings'},
                                {'id': 'Jewellery Sets', 'title': 'Jewellery Sets'},
                                {'id': 'Lockets', 'title': 'Lockets'},
                                # <li class="disabled"><a class="disabled" href="#">Disabled item</a></li>
                                {'id': 'Jeans', 'title': 'Jeans'},
                                {'id': 'Polo T-Shirts', 'title': 'Polo T-Shirts'},
                                {'id': 'SKirts', 'title': 'SKirts'},
                                {'id': 'Jackets', 'title': 'Jackets'},
                                {'id': 'Tops', 'title': 'Tops'},
                                {'id': 'Make Up', 'title': 'Make Up'},
                                {'id': 'Hair Care', 'title': 'Hair Care'},
                                {'id': 'Perfumes', 'title': 'Perfumes'},
                                {'id': 'Skin Care', 'title': 'Skin Care'},
                                {'id': 'Hand Bags', 'title': 'Hand Bags'},
                                {'id': 'Single Bags', 'title': 'Single Bags'},
                                {'id': 'Travel Bags', 'title': 'Travel Bags'},
                                {'id': 'Wallets & Belts',
                                    'title': 'Wallets & Belts'},
                                {'id': 'Sunglases', 'title': 'Sunglases'},
                                {'id': 'Nail', 'title': 'Nail'},
                            ]
                        }
                    ]
                }
            ]
        },
        {
            'id': 'kids',
            'title': 'Kids',
            'children': [
                {'id': 'casual', 'title': 'Casual'},
                {'id': 'sports', 'title': 'Sports'},
                {'id': 'formal', 'title': 'Formal'},
                {'id': 'standard', 'title': 'Standard'},
                {'id': 't-shirts', 'title': 'T-Shirts'},
                {'id': 'shirts', 'title': 'Shirts'},
                {'id': 'jeans', 'title': 'Jeans'},
                {'id': 'trousers', 'title': 'Trousers'},
                {
                    'id': 'other',
                    'title': 'And more…',
                    'children': [
                        {'id': 'sleep-wear', 'title': 'Sleep Wear'},
                        {'id': 'sandals', 'title': 'Sandals'},
                        {'id': 'loafers', 'title': 'Loafers'}
                    ]
                }
            ]
        },
        {'id': 'sports', 'title': 'Sports'},
        {
            'id': 'digital',
            'title': 'Digital',
            'children': [
                {'id': 'camera', 'title': 'Camera'},
                {'id': 'mobile', 'title': 'Mobile'},
                {'id': 'tablet', 'title': 'Tablet'},
                {'id': 'laptop', 'title': 'Laptop'},
                {'id': 'accesories', 'title': 'Accesories'},
            ]
        },
        {'id': 'furniture', 'title': 'Furniture'}
    ]


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=environ.get('SERVER_PORT', 5000))
