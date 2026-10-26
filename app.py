import os, csv, io, re, secrets
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass
from functools import wraps
from flask import Flask, g, render_template, request, redirect, url_for, session, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
app=Flask(__name__); app.secret_key=os.getenv('SECRET_KEY','brovault-local-change-this-key')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

UP=os.path.join(os.path.dirname(__file__),'static','uploads'); os.makedirs(UP,exist_ok=True)
# Existing product image names mapped to local uploaded photos.
PRODUCT_IMAGE_MAP = {
    'watch_midnight.svg': 'watch1.png',
    'watch_champagne.svg': 'watch1.png',
    'watch_urban.svg': 'watch1.png',
    'wallet_tan.svg': 'wallet1.png',
    'wallet_mocha.svg': 'wallet1.png',
    'cardholder_black.svg': 'wallet1.png',
    'perfume_amber.svg': 'perfume1.png',
    'perfume_citrus.svg': 'perfume1.png',
    'perfume_noir.svg': 'perfume1.png',
    'sunglasses_aviator.svg': 'sunglasses1.png',
    'sunglasses_black.svg': 'sunglasses1.png',
    'bracelet_steel.svg': 'bracelet1.png',
    'bracelet_leather.svg': 'bracelet1.png',
    'keychain_initial.svg': 'keychain1.png',
    'keyorganiser.svg': 'keychain1.png',
    'personal_box.svg': 'giftbox1.png',
    'combo_gentleman.svg': 'giftbox1.png',
    'combo_watch_wallet.svg': 'giftbox1.png',
    'combo_scent.svg': 'giftbox1.png',
    'birthday_luxe.svg': 'giftbox1.png',
    'anniversary_set.svg': 'giftbox1.png',
    'desk_set.svg': 'pen1.png',
    'grooming_kit.svg': 'perfume1.png',
    'grooming_pouch.svg': 'giftbox1.png',
    'wallet_personal.svg': 'wallet1.png',
}
import mysql.connector
from mysql.connector import Error as MySQLError


MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USER', 'avnadmin'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'defaultdb'),
    'autocommit': False,
}

_ssl_ca = os.getenv('MYSQL_SSL_CA', '/etc/secrets/ca.pem')
if os.path.isfile(_ssl_ca):
    MYSQL_CONFIG.update({
        'ssl_ca': _ssl_ca,
        'ssl_verify_cert': True,
        'ssl_verify_identity': True,
    })


def _translate_sql(sql):
    # Keep the existing route SQL compatible with the supplied MySQL schema.
    sql = re.sub(r'\bINSERT\s+OR\s+IGNORE\b', 'INSERT IGNORE', sql, flags=re.I)
    sql = re.sub(r'\bwishlist\b', 'wishlists', sql, flags=re.I)
    sql = re.sub(r'\bpassword\b', 'password_hash', sql, flags=re.I)
    sql = re.sub(r'\boriginal\b', 'original_price', sql, flags=re.I)
    sql = sql.replace('?', '%s')
    # MySQL DATE columns should receive NULL rather than an empty date string.
    sql = re.sub(r'INSERT INTO coupons\(code,discount,expiry\) VALUES\(%s,%s,%s\)',
                 "INSERT INTO coupons(code,discount,expiry) VALUES(%s,%s,NULLIF(%s,''))", sql, flags=re.I)
    return sql

class _CursorResult:
    def __init__(self, cursor):
        self._cursor = cursor
        self.lastrowid = cursor.lastrowid
        self.rowcount = cursor.rowcount
    def fetchone(self):
        row = self._cursor.fetchone()
        return self._aliases(row) if row is not None else None
    def fetchall(self):
        return [self._aliases(row) for row in self._cursor.fetchall()]
    @staticmethod
    def _aliases(row):
        if row is None: return None
        row = dict(row)
        if 'password_hash' in row: row.setdefault('password', row['password_hash'])
        if 'original_price' in row: row.setdefault('original', row['original_price'])
        if 'created_at' in row: row.setdefault('created', row['created_at'])
        return row

class _ConnectionAdapter:
    def __init__(self, connection): self.connection = connection
    def execute(self, sql, args=()):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(_translate_sql(sql), args)
        return _CursorResult(cursor)
    def commit(self): self.connection.commit()
    def close(self): self.connection.close()

def db():
    if 'db' not in g:
        g.db = _ConnectionAdapter(mysql.connector.connect(**MYSQL_CONFIG))
    return g.db

def init():
    """Seed only empty catalog tables; never drop or reset customer data."""
    c = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        cur = c.cursor()
        # Safe, additive migration for duplicate-checkout protection.
        cur.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='orders' AND COLUMN_NAME='checkout_token'", (MYSQL_CONFIG['database'],))
        if cur.fetchone()[0] == 0:
            cur.execute("ALTER TABLE orders ADD COLUMN checkout_token VARCHAR(64) NULL UNIQUE")
        cur.execute("SELECT COUNT(*) FROM categories")
        if cur.fetchone()[0] == 0:
            cats = [
                ("Watches", "Everyday and statement watches"),
                ("Wallets & Card Holders", "Slim wallets and card holders"),
                ("Perfumes & Fragrances", "Signature scents"),
                ("Sunglasses", "Modern eyewear"),
                ("Bracelets & Rings", "Finishing-touch accessories"),
                ("Keychains & Small Accessories", "Useful little extras"),
                ("Grooming Accessories", "Everyday grooming essentials"),
                ("Personalized Gifts", "Made personal for him"),
                ("Gift Combos & Gift Boxes", "Ready-to-gift sets"),
                ("Birthday & Occasion Gifts", "Gifts for memorable days"),
            ]
            cur.executemany("INSERT INTO categories(name,description) VALUES(%s,%s)", cats)
        cur.execute("SELECT COUNT(*) FROM products")
        if cur.fetchone()[0] == 0:
            products = [
                ("Midnight Minimal Watch","Minimal black dial watch with a brushed steel finish.",1,2499,3299,14,"watch_midnight.svg",1),
                ("Champagne Classic Watch","Champagne-tone dial with a refined everyday profile.",1,3199,3999,9,"watch_champagne.svg",1),
                ("Urban Chronograph Watch","Sport-inspired chronograph look for daily wear.",1,2899,3599,11,"watch_urban.svg",1),
                ("Classic Tan Bifold Wallet","Tan textured wallet with practical card slots.",2,899,1199,24,"wallet_tan.svg",1),
                ("Black Slim Card Holder","Compact black card holder for a clean carry.",2,599,799,30,"cardholder_black.svg",0),
                ("Mocha Leather Wallet","Warm mocha wallet with a timeless finish.",2,1099,1399,17,"wallet_mocha.svg",1),
                ("Cedar & Amber Perfume","Warm woody fragrance for evenings and occasions.",3,1599,1999,13,"perfume_amber.svg",1),
                ("Fresh Citrus Eau de Parfum","Bright citrus opening with a clean, modern base.",3,1299,1699,16,"perfume_citrus.svg",1),
                ("Noir Signature Fragrance","Deep, sophisticated scent in a matte dark bottle.",3,1899,2399,8,"perfume_noir.svg",1),
                ("Aviator Smoke Sunglasses","Classic aviator silhouette with smoke lenses.",4,999,1299,20,"sunglasses_aviator.svg",0),
                ("Matte Black Wayfarers","Everyday wayfarer frame with a matte finish.",4,1199,1499,18,"sunglasses_black.svg",1),
                ("Steel Link Bracelet","Polished steel bracelet with a minimal profile.",5,699,999,21,"bracelet_steel.svg",0),
                ("Black Onyx Ring","Understated dark ring with a clean design.",5,799,1099,12,"ring_onyx.svg",0),
                ("Braided Leather Bracelet","Braided black bracelet with a secure clasp.",5,499,699,27,"bracelet_leather.svg",0),
                ("Engraved Initial Keychain","Personalized metal-look keychain for daily carry.",6,349,499,40,"keychain_initial.svg",0),
                ("Minimal Metal Key Organiser","Compact organiser for a tidy key set.",6,449,599,25,"keyorganiser.svg",0),
                ("Beard Care Grooming Kit","A neat set of beard-care essentials.",7,999,1299,15,"grooming_kit.svg",1),
                ("Travel Grooming Pouch","Compact pouch for grooming and travel essentials.",7,699,899,19,"grooming_pouch.svg",0),
                ("Personalized Name Wallet","Wallet-style gift with a customizable name detail.",8,1199,1499,10,"wallet_personal.svg",1),
                ("Custom Message Gift Card Box","A keepsake box with space for a personal note.",8,799,999,14,"personal_box.svg",0),
                ("The Everyday Gentleman Box","Wallet, keychain and gift-ready packaging.",9,2199,2799,7,"combo_gentleman.svg",1),
                ("Watch & Wallet Gift Set","Coordinated accessories in a premium gift box.",9,3499,4299,5,"combo_watch_wallet.svg",1),
                ("Signature Scent Gift Set","Fragrance and grooming accessories for gifting.",9,2499,3199,6,"combo_scent.svg",1),
                ("Birthday Luxe Gift Box","A ready-to-gift box with curated men's accessories.",10,1999,2599,8,"birthday_luxe.svg",1),
                ("Anniversary Keepsake Set","A refined keepsake set for a special occasion.",10,1799,2299,9,"anniversary_set.svg",0),
                ("Desk Essentials Gift Set","A practical set of understated everyday accessories.",10,1499,1899,12,"desk_set.svg",0),
            ]
            cur.executemany(
                "INSERT INTO products(name,description,category_id,price,original_price,stock,image,featured) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", products
            )
        cur.execute("INSERT IGNORE INTO coupons(code,discount,active) VALUES('VAULT10',10,1)")
        cur.execute('SELECT id FROM users WHERE email=%s', (os.getenv('ADMIN_EMAIL', 'admin@brovault.local'),))
        if not cur.fetchone():
            cur.execute("INSERT INTO users(name,email,password_hash,role) VALUES(%s,%s,%s,%s)",
                        ("BroVault Admin",os.getenv("ADMIN_EMAIL","admin@brovault.local"),generate_password_hash(os.getenv("ADMIN_PASSWORD","ChangeMe@123")),"admin"))
        c.commit()
    finally:
        c.close()
@app.before_request
def startup():
 if not getattr(app,'ready',False): init(); app.ready=True
@app.teardown_appcontext
def close(e=None):
 c=g.pop('db',None)
 if c:c.close()
def all(sql,args=()): return [dict(x) for x in db().execute(sql,args).fetchall()]
def one(sql,args=()):
 x=db().execute(sql,args).fetchone(); return dict(x) if x else None
def run(sql,args=()):
 c=db(); cur=c.execute(sql,args); c.commit(); return cur.lastrowid
def login_req(fn):
 @wraps(fn)
 def w(*a,**kw):
  if not session.get('uid'): flash('Please log in to continue.','info'); return redirect(url_for('login'))
  return fn(*a,**kw)
 return w
def admin_req(fn):
 @wraps(fn)
 def w(*a,**kw):
  if session.get('role')!='admin': flash('Administrator access required.','error'); return redirect(url_for('login'))
  return fn(*a,**kw)
 return w
@app.context_processor
def globals():
 n=0
 if session.get('uid') and session.get('role')!='admin':
  c=one('select id from carts where user_id=?',(session['uid'],))
  if c:n=one('select coalesce(sum(quantity),0) n from cart_items where cart_id=?',(c['id'],))['n']
 return dict(me=session.get('name'),role=session.get('role'),cart_count=n,today=__import__('datetime').date.today().strftime('%b %d, %Y'))
@app.template_filter('money')
def money(v): return '₹{:,.0f}'.format(float(v or 0))
def cart_for(create=False):
 c=one('select * from carts where user_id=?',(session['uid'],))
 if not c and create:
  i=run('insert into carts(user_id) values(?)',(session['uid'],)); c=one('select * from carts where id=?',(i,))
 return c

@app.template_filter('product_image')
def product_image(filename):
    from flask import url_for

    filename = str(filename or '').strip().replace('\\', '/')
    filename = filename.lstrip('/')

    # Support database paths that already include "static/".
    if filename.startswith('static/'):
        filename = filename[len('static/'):]

    # Keep valid uploaded or bundled image paths.
    if filename.startswith(('uploads/', 'images/')):
        relative_path = filename
    else:
        # Match the existing catalogue SVG names to your uploaded photos.
        name = os.path.basename(filename)
        mapped = PRODUCT_IMAGE_MAP.get(name)

        if mapped:
            relative_path = 'uploads/' + mapped
        elif os.path.isfile(os.path.join(
            app.static_folder, 'images', 'products', name
        )):
            relative_path = 'images/products/' + name
        else:
            relative_path = 'uploads/giftbox1.png'

    # Check that the image actually exists.
    full_path = os.path.join(
        app.static_folder,
        *relative_path.split('/')
    )

    if not os.path.isfile(full_path):
        relative_path = 'uploads/giftbox1.png'

    # Always generate the correct /static/... URL.
    return url_for('static', filename=relative_path)

@app.route('/')
def home(): return render_template('home.html',cats=all('select * from categories'),products=all('select p.*,c.name category from products p left join categories c on c.id=p.category_id where active=1 order by featured desc,id desc limit 8'))
@app.route('/shop')
def shop():
 q=request.args.get('q','').strip(); cat=request.args.get('category',''); sort=request.args.get('sort','featured'); sql='select p.*,c.name category from products p left join categories c on c.id=p.category_id where active=1'; args=[]
 if q: sql+=' and (p.name like ? or p.description like ? or c.name like ?)'; args += ['%'+q+'%']*3
 if cat.isdigit(): sql+=' and category_id=?'; args.append(int(cat))
 sql+=' order by '+{'price_low':'price asc','price_high':'price desc','name':'p.name asc'}.get(sort,'featured desc,p.id desc')
 return render_template('shop.html',products=all(sql,args),cats=all('select * from categories'),q=q,cat=cat,sort=sort)
@app.route('/product/<int:i>')
def product(i):
 p=one('select p.*,c.name category from products p left join categories c on c.id=p.category_id where p.id=? and active=1',(i,))
 if not p: flash('Product not found.','error'); return redirect(url_for('shop'))
 return render_template('product.html',p=p,related=all('select * from products where category_id=? and id<>? and active=1 limit 4',(p['category_id'],i)) )
@app.route('/register',methods=['GET','POST'])
def register():
 if request.method=='POST':
  name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); pw=request.form.get('password','')
  if len(name)<2 or '@' not in email or len(pw)<8: flash('Enter a valid name/email and password of at least 8 characters.','error')
  elif one('select id from users where email=?',(email,)): flash('Email already registered.','error')
  else:
   uid=run('insert into users(name,email,password) values(?,?,?)',(name,email,generate_password_hash(pw))); session.update(uid=uid,name=name,role='customer'); flash('Welcome to BroVault!','success'); return redirect(url_for('gift_box') if session.get('pending_gift_box') else url_for('home'))
 return render_template('auth.html',mode='register')
@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  u=one('select * from users where email=?',(request.form.get('email','').strip().lower(),))
  if u and check_password_hash(u['password'],request.form.get('password','')):
   pending_box = session.get('pending_gift_box')
   session.clear()
   session.update(uid=u['id'],name=u['name'],role=u['role'])
   if pending_box: session['pending_gift_box'] = pending_box
   return redirect(url_for('dashboard') if u['role']=='admin' else (url_for('gift_box') if pending_box else url_for('home')))
  flash('Email or password is incorrect.','error')
 return render_template('auth.html',mode='login')
@app.route('/logout')
def logout(): session.clear(); flash('You are logged out.','info'); return redirect(url_for('home'))
@app.route('/profile',methods=['GET','POST'])
@login_req
def profile():
 u=one('select * from users where id=?',(session['uid'],))
 if request.method=='POST':
  name=request.form.get('name','').strip()
  if len(name)>1: run('update users set name=? where id=?',(name,session['uid'])); session['name']=name; flash('Profile updated.','success'); return redirect(url_for('profile'))
  flash('Enter your name.','error')
 return render_template('profile.html',u=u)
@app.route('/cart/add/<int:i>',methods=['POST'])
@login_req
def add_cart(i):
 p=one('select * from products where id=? and active=1',(i,))
 try: qty=max(1,min(int(request.form.get('quantity',1) or 1),99))
 except (TypeError, ValueError): qty=1
 if not p or qty>p['stock']: flash('Product not found or quantity exceeds stock.','error'); return redirect(request.referrer or url_for('shop'))
 c=cart_for(True); recipient=request.form.get('recipient','').strip()[:100]; message=request.form.get('message','').strip()[:400]; wrap=int(bool(request.form.get('wrap'))); card=int(bool(request.form.get('card')))
 ex=one('select * from cart_items where cart_id=? and product_id=? and recipient=? and message=? and wrap=? and card=?',(c['id'],i,recipient,message,wrap,card))
 if ex:
  if ex['quantity']+qty>p['stock']: flash('Quantity exceeds available stock.','error'); return redirect(url_for('cart'))
  run('update cart_items set quantity=quantity+? where id=?',(qty,ex['id']))
 else: run('insert into cart_items(cart_id,product_id,quantity,recipient,message,wrap,card) values(?,?,?,?,?,?,?)',(c['id'],i,qty,recipient,message,wrap,card))
 flash('Added to your cart.','success'); return redirect(url_for('cart'))
@app.route('/cart')
@login_req
def cart():
 c=cart_for(); items=all('select ci.*,p.name,p.image,(p.price + ci.wrap*79 + ci.card*39) price,p.stock from cart_items ci join products p on p.id=ci.product_id where ci.cart_id=?',(c['id'],)) if c else []
 for x in items:x['line']=x['price']*x['quantity']
 return render_template('cart.html',items=items,subtotal=sum(x['line'] for x in items))
@app.route('/cart/update/<int:i>',methods=['POST'])
@login_req
def cart_update(i):
 item=one('select ci.*,p.stock,c.user_id from cart_items ci join carts c on c.id=ci.cart_id join products p on p.id=ci.product_id where ci.id=? and c.user_id=?',(i,session['uid']))
 if item:
  try: q=int(request.form.get('quantity',1))
  except (TypeError, ValueError): q=1
  if q<=0: run('delete from cart_items where id=?',(i,))
  elif q<=item['stock']:run('update cart_items set quantity=? where id=?',(q,i,))
  else:flash('Quantity exceeds stock.','error')
 return redirect(url_for('cart'))
@app.route('/cart/remove/<int:i>',methods=['POST'])
@login_req
def cart_remove(i):
 run('delete from cart_items where id in (select ci.id from cart_items ci join carts c on c.id=ci.cart_id where ci.id=? and c.user_id=?)',(i,session['uid'])); flash('Item removed.','info'); return redirect(url_for('cart'))
@app.route('/wishlist')
@login_req
def wishlist():
    # Use the exact table name from database/schema.sql (MySQL: wishlists).
    products = all(
        'SELECT p.*, c.name AS category FROM wishlists w '
        'JOIN products p ON p.id=w.product_id '
        'LEFT JOIN categories c ON c.id=p.category_id '
        'WHERE w.user_id=? ORDER BY w.id DESC',
        (session['uid'],)
    )
    return render_template('wishlist.html', products=products)

@app.route('/wishlist/<int:i>', methods=['POST'])
@login_req
def wishlist_toggle(i):
    # Validate product and write to MySQL; run() commits each change.
    product = one('SELECT id FROM products WHERE id=? AND active=1', (i,))
    if not product:
        flash('This product is no longer available.', 'error')
        return redirect(request.referrer or url_for('shop'))

    saved = one(
        'SELECT id FROM wishlists WHERE user_id=? AND product_id=?',
        (session['uid'], i)
    )
    if saved:
        run('DELETE FROM wishlists WHERE user_id=? AND product_id=?',
            (session['uid'], i))
        flash('Removed from wishlist.', 'info')
    else:
        run('INSERT IGNORE INTO wishlists(user_id, product_id) VALUES(?, ?)',
            (session['uid'], i))
        flash('Saved to wishlist.', 'success')
    return redirect(request.referrer or url_for('shop'))
@app.route('/personalize')
@login_req
def personalize(): return render_template('personalize.html',products=all('select * from products where active=1'),chosen=request.args.get('product_id',type=int))
@app.route('/checkout',methods=['GET','POST'])
@login_req
def checkout():
 if request.method == 'GET' or not session.get('checkout_token'):
  session['checkout_token'] = secrets.token_urlsafe(24)
 c=cart_for()
 items=all('select ci.*,p.name,p.image,(p.price + ci.wrap*79 + ci.card*39) price,p.stock from cart_items ci join products p on p.id=ci.product_id where ci.cart_id=?',(c['id'],)) if c else []
 if not items:
  flash('Your cart is empty.','info')
  return redirect(url_for('shop'))
 subtotal=sum(float(i['price'])*int(i['quantity']) for i in items)
 code=request.form.get('coupon','').strip().upper() if request.method=='POST' else ''
 cp=one('select * from coupons where code=? and active=1 and (expiry is null or expiry>=CURRENT_DATE)',(code,)) if code else None
 disc=subtotal*float(cp['discount'])/100 if cp else 0
 if code and not cp and request.method=='POST':
  flash('Invalid coupon code.','error')
 ship=0 if subtotal>=1500 else 79
 total=subtotal-disc+ship
 if request.method=='POST' and request.form.get('action')=='place':
  token=request.form.get('checkout_token','')
  if not token or token != session.get('checkout_token'):
   flash('This checkout form has expired. Please review your cart and try again.', 'error')
   return redirect(url_for('checkout'))
  existing_order=one('select id,payment from orders where checkout_token=?',(token,))
  if existing_order:
   session['checkout_token']=secrets.token_urlsafe(24)
   if existing_order['payment']=='Scan QR & Pay':
    return redirect(url_for('qr_payment',i=existing_order['id']))
   flash('This order was already submitted.', 'info')
   return redirect(url_for('orders'))
  fields=[request.form.get(k,'').strip() for k in ['fullname','phone','address','city','state','postal']]
  if any(not value for value in fields):
   flash('Complete all delivery details.','error')
  elif any(int(i['quantity'])>int(i['stock']) for i in items):
   flash('Stock changed. Update your cart.','error')
  else:
   pay=request.form.get('payment','Cash on Delivery')
   if pay not in ('Cash on Delivery','Scan QR & Pay'):
    pay='Cash on Delivery'
   address=' | '.join(fields)
   conn=db()
   try:
    order_result=conn.execute('insert into orders(user_id,total,status,payment,address,coupon,checkout_token) values(?,?,?,?,?,?,?)',
      (session['uid'],total,'Pending',pay,address,code if cp else '',token))
    oid=order_result.lastrowid
    for i in items:
     custom='Recipient: {}; Message: {}; Wrapping: {}; Card: {}'.format(i.get('recipient',''),i.get('message',''),'Yes' if i['wrap'] else 'No','Yes' if i['card'] else 'No')
     conn.execute('insert into order_items(order_id,product_id,product_name,price,quantity,custom) values(?,?,?,?,?,?)',(oid,i['product_id'],i['name'],i['price'],i['quantity'],custom))
     stock_update = conn.execute('update products set stock=stock-? where id=? and stock>=?', (i['quantity'],i['product_id'],i['quantity']))
     if stock_update.rowcount != 1:
      raise ValueError('Stock changed while checking out. Please review your cart.')
     conn.execute('insert into inventory_log(product_id,delta,note) values(?,?,?)',(i['product_id'],-i['quantity'],'Order #'+str(oid)))
    conn.execute('insert into status_history(order_id,status) values(?,?)',(oid,'Pending'))
    conn.execute('delete from cart_items where cart_id=?',(c['id'],))
    conn.commit()
   except Exception:
    try: conn.connection.rollback()
    except Exception: pass
    app.logger.exception('BroVault checkout failed while saving order')
    flash('Order could not be saved. Check the terminal for the database error and confirm MySQL is running.','error')
    return redirect(url_for('checkout'))
   session['checkout_token']=secrets.token_urlsafe(24)
   if pay=='Scan QR & Pay':
    return redirect(url_for('qr_payment',i=oid))
   flash('Order #{} placed successfully! Payment: Cash on Delivery.'.format(oid),'success')
   return redirect(url_for('orders'))
 return render_template('checkout.html',items=items,subtotal=subtotal,discount=disc,shipping=ship,total=total,code=code,checkout_token=session.get('checkout_token',''))

@app.route('/payment/qr/<int:i>',methods=['GET','POST'])
@login_req
def qr_payment(i):
 o = one(
  'select * from orders where id=? and user_id=?',
  (i, session['uid'])
 )

 if not o:
  flash('Order not found.', 'error')
  return redirect(url_for('orders'))

 if o['payment'] not in (
  'Scan QR & Pay',
  'UPI Payment Submitted (unverified)'
 ):
  flash('This order is not set for QR payment.', 'info')
  return redirect(url_for('order_detail', i=i))

 # Use the QR image already uploaded in static/uploads/
 return render_template(
  'payment_qr.html',
  o=o,
  qr_data=None,
  upi_id=''
 )

@app.route('/payment/confirmation/<int:i>')
@login_req
def payment_confirmation(i):
 o=one('select * from orders where id=? and user_id=?',(i,session['uid']))
 if not o:
  flash('Order not found.','error')
  return redirect(url_for('orders'))
 return render_template('payment_confirmation.html',o=o)
@app.route('/orders')
@login_req
def orders(): return render_template('orders.html',orders=all('select * from orders where user_id=? order by id desc',(session['uid'],)))
@app.route('/order/<int:i>')
@login_req
def order_detail(i):
 o=one('select o.*,u.name customer from orders o join users u on u.id=o.user_id where o.id=? and (o.user_id=? or ?="admin")',(i,session['uid'],session.get('role')))
 if not o:flash('Order not found.','error');return redirect(url_for('orders'))
 return render_template('order_detail.html',o=o,items=all('select * from order_items where order_id=?',(i,)),history=all('select * from status_history where order_id=? order by id',(i,)))
@app.route('/admin')
@admin_req
def dashboard():
 stats={'orders':one('select count(*) n from orders')['n'],'sales':one("select coalesce(sum(total),0) n from orders where status!='Cancelled'")['n'],'customers':one("select count(*) n from users where role='customer'")['n'],'low':one('select count(*) n from products where active=1 and stock<6')['n']}
 return render_template('dashboard.html',stats=stats,recent=all('select o.*,u.name customer from orders o join users u on u.id=o.user_id order by o.id desc limit 5'),products=all('select * from products where active=1 order by featured desc limit 5'),cats=all('select c.name,coalesce(sum(oi.quantity*oi.price),0) sales from categories c left join products p on p.category_id=c.id left join order_items oi on oi.product_id=p.id group by c.id,c.name'),monthly=all("select substr(created,1,7) month,sum(total) sales from orders where status!='Cancelled' group by substr(created,1,7) order by month"),low=all('select * from products where active=1 and stock<6 order by stock limit 6'))
@app.route('/admin/products', methods=['GET', 'POST'])
@admin_req
def admin_products():
    # Only read form fields and insert a product for POST requests.
    if request.method == 'POST':
        name = request.form.get('name', '').strip()

        try:
            price = float(request.form.get('price') or 0)
            original = float(request.form.get('original') or price)
            stock = int(request.form.get('stock') or 0)
            cat = int(request.form.get('category_id') or 0)
        except (TypeError, ValueError):
            flash('Check product fields.', 'error')
            return redirect(url_for('admin_products'))

        if not name or price <= 0 or original < price or stock < 0:
            flash('Enter valid product details.', 'error')
            return redirect(url_for('admin_products'))

        if not one('SELECT id FROM categories WHERE id=?', (cat,)):
            flash('Please select a valid category.', 'error')
            return redirect(url_for('admin_products'))

        image = 'gift_box.svg'
        f = request.files.get('image')
        if f and f.filename:
            if '.' not in f.filename:
                flash('Upload PNG/JPG/WEBP/GIF only.', 'error')
                return redirect(url_for('admin_products'))

            ext = f.filename.rsplit('.', 1)[-1].lower()
            if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                flash('Upload PNG/JPG/WEBP/GIF only.', 'error')
                return redirect(url_for('admin_products'))

            filename = secure_filename(f.filename)
            if not filename:
                flash('Invalid image filename.', 'error')
                return redirect(url_for('admin_products'))

            # Avoid overwriting an image with the same filename.
            base, extension = os.path.splitext(filename)
            save_path = os.path.join(UP, filename)
            counter = 1
            while os.path.exists(save_path):
                filename = f'{base}_{counter}{extension}'
                save_path = os.path.join(UP, filename)
                counter += 1

            f.save(save_path)
            image = 'uploads/' + filename

        try:
            run(
                'INSERT INTO products(name,description,category_id,price,original,stock,image,featured) '
                'VALUES(?,?,?,?,?,?,?,?)',
                (
                    name,
                    request.form.get('description', '').strip(),
                    cat,
                    price,
                    original,
                    stock,
                    image,
                    int(bool(request.form.get('featured'))),
                ),
            )
            flash('Product added successfully.', 'success')
        except MySQLError:
            app.logger.exception('Failed to add product')
            flash('Could not add product. Please check the details.', 'error')

        return redirect(url_for('admin_products'))

    # GET requests only display the products page; no form variables are needed.
    products = all(
        'SELECT p.*, c.name category FROM products p '
        'LEFT JOIN categories c ON c.id=p.category_id ORDER BY p.id DESC'
    )
    cats = all('SELECT * FROM categories ORDER BY name')
    return render_template('admin_products.html', products=products, cats=cats)

@app.route('/admin/products/<int:i>/edit',methods=['POST'])
@admin_req
def edit_product(i):
 try:run('update products set name=?,description=?,category_id=?,price=?,original=?,stock=?,featured=? where id=?',(request.form['name'],request.form.get('description',''),int(request.form['category_id']),float(request.form['price']),float(request.form.get('original') or request.form['price']),int(request.form['stock']),int(bool(request.form.get('featured'))),i));flash('Product updated.','success')
 except:flash('Could not update product; check values.','error')
 return redirect(url_for('admin_products'))
@app.route('/admin/products/<int:i>/delete',methods=['POST'])
@admin_req
def delete_product(i):run('update products set active=0 where id=?',(i,));flash('Product archived.','success');return redirect(url_for('admin_products'))
@app.route('/admin/categories', methods=['GET', 'POST'])
@admin_req
def admin_categories():
    if request.method == 'POST':
        name=request.form.get('name','').strip()
        description=request.form.get('description','').strip()
        if not name:
            flash('Category name is required.', 'error')
        else:
            try:
                run('INSERT INTO categories(name,description) VALUES(?,?)',(name,description))
                flash('Category added.', 'success')
            except MySQLError:
                flash('That category already exists or could not be saved.', 'error')
        return redirect(url_for('admin_categories'))
    return render_template('admin_categories.html', categories=all('SELECT c.*,COUNT(p.id) product_count FROM categories c LEFT JOIN products p ON p.category_id=c.id GROUP BY c.id ORDER BY c.name'))
@app.route('/admin/inventory',methods=['GET','POST'])
@admin_req
def inventory():
 if request.method=='POST':
  i=int(request.form['id']); qty=int(request.form['stock']); p=one('select stock from products where id=?',(i,));
  if p and qty>=0:run('update products set stock=? where id=?',(qty,i));run('insert into inventory_log(product_id,delta,note) values(?,?,?)',(i,qty-p['stock'],'Manual stock adjustment'));flash('Stock updated.','success')
  else:flash('Invalid stock quantity.','error')
  return redirect(url_for('inventory'))
 return render_template('inventory.html',products=all('select p.*,c.name category from products p left join categories c on c.id=p.category_id where active=1 order by stock'),logs=all('select l.*,p.name from inventory_log l left join products p on p.id=l.product_id order by l.id desc limit 12'))
@app.route('/admin/orders',methods=['GET','POST'])
@admin_req
def admin_orders():
 if request.method=='POST':
  i=int(request.form['id']); s=request.form['status'];
  if s in ['Pending','Confirmed','Processing','Shipped','Delivered','Cancelled']:
   run('update orders set status=? where id=?',(s,i));run('insert into status_history(order_id,status) values(?,?)',(i,s));flash('Order status updated.','success')
  return redirect(url_for('admin_orders'))
 return render_template('admin_orders.html',orders=all('select o.*,u.name customer,u.email from orders o join users u on u.id=o.user_id order by o.id desc'))
@app.route('/admin/customers')
@admin_req
def customers():return render_template('customers.html',customers=all("select u.*,count(o.id) orders,coalesce(sum(o.total),0) spend from users u left join orders o on o.user_id=u.id where u.role='customer' group by u.id order by u.id desc"))
@app.route('/admin/coupons',methods=['GET','POST'])
@admin_req
def coupons():
 if request.method=='POST':
  code=request.form.get('code','').strip().upper(); expiry=request.form.get('expiry','')
  try:
   disc=int(request.form.get('discount',10))
   if not code or not 1 <= disc <= 80: raise ValueError('Invalid coupon')
   run('insert into coupons(code,discount,expiry) values(?,?,?)',(code,disc,expiry or None));flash('Coupon created.','success')
  except:flash('Coupon code already exists or values are invalid.','error')
  return redirect(url_for('coupons'))
 return render_template('coupons.html',coupons=all('select * from coupons order by id desc'))
@app.route('/admin/coupons/<int:i>/toggle',methods=['POST'])
@admin_req
def coupon_toggle(i):run('update coupons set active=1-active where id=?',(i,));flash('Coupon status changed.','success');return redirect(url_for('coupons'))
@app.route('/admin/reports')
@admin_req
def reports():return render_template('reports.html',revenue=one("select coalesce(sum(total),0) n from orders where status!='Cancelled'")['n'],count=one('select count(*) n from orders')['n'],cats=all('select c.name,coalesce(sum(oi.price*oi.quantity),0) sales from categories c left join products p on p.category_id=c.id left join order_items oi on oi.product_id=p.id group by c.id,c.name'),best=all('select product_name,sum(quantity) units from order_items group by product_name order by units desc limit 8'),monthly=all("select substr(created,1,7) month,sum(total) sales from orders where status!='Cancelled' group by substr(created,1,7) order by month"))
@app.route('/admin/reports/export.csv')
@admin_req
def export():
 data=all('select o.id order_id,o.created,u.name customer,u.email,o.status,o.payment,o.total,o.coupon from orders o join users u on u.id=o.user_id'); out=io.StringIO(); w=csv.writer(out);w.writerow(['order_id','date','customer','email','status','payment','total','coupon']);
 for x in data:w.writerow([x[k] for k in ['order_id','created','customer','email','status','payment','total','coupon']])
 r=make_response(out.getvalue());r.headers['Content-Disposition']='attachment; filename=brovault_orders.csv';r.headers['Content-Type']='text/csv';return r

@app.route('/gift-finder', methods=['GET', 'POST'])
def gift_finder():
    occasion = request.values.get('occasion', 'Birthday')
    budget = request.values.get('budget', '2500')
    style = request.values.get('style', 'Any')
    try:
        cap = max(300, min(int(budget), 20000))
    except (TypeError, ValueError):
        cap = 2500
    style_terms = {
        'Minimal': ['minimal', 'slim', 'black', 'classic'],
        'Classic': ['classic', 'wallet', 'watch', 'leather'],
        'Bold': ['noir', 'chronograph', 'sunglasses', 'bracelet'],
        'Practical': ['wallet', 'key', 'grooming', 'organiser', 'pouch'],
    }
    terms = style_terms.get(style, [])
    products = []
    if terms:
        conditions = ' OR '.join(['LOWER(p.name) LIKE ? OR LOWER(p.description) LIKE ? OR LOWER(c.name) LIKE ?' for _ in terms])
        args = [cap]
        for term in terms: args.extend(['%'+term+'%']*3)
        products = all(
            "SELECT p.*, c.name category FROM products p LEFT JOIN categories c ON c.id=p.category_id "
            "WHERE p.active=1 AND p.price<=? AND ("+conditions+") "
            "ORDER BY p.featured DESC, p.price DESC LIMIT 12", tuple(args)
        )
    if not products:
        products = all(
            "SELECT p.*, c.name category FROM products p LEFT JOIN categories c ON c.id=p.category_id "
            "WHERE p.active=1 AND p.price<=? ORDER BY p.featured DESC, p.price DESC LIMIT 12", (cap,)
        )
    return render_template('gift_finder.html', products=products, occasion=occasion, budget=cap, style=style)

@app.route('/gift-box', methods=['GET', 'POST'])
def gift_box():
    products = all("SELECT p.*, c.name category FROM products p LEFT JOIN categories c ON c.id=p.category_id "
                   "WHERE p.active=1 AND p.stock>0 ORDER BY p.featured DESC, p.name")
    if request.method == 'POST':
        ids = []
        for value in request.form.getlist('product_ids'):
            try:
                n = int(value)
                if n not in ids: ids.append(n)
            except (TypeError, ValueError):
                continue
        if not 2 <= len(ids) <= 4:
            flash('Choose between 2 and 4 different products for your gift box.', 'error')
            return redirect(url_for('gift_box'))
        if not session.get('uid'):
            session['pending_gift_box'] = ids
            flash('Log in to save your gift box to the cart.', 'info')
            return redirect(url_for('login'))
        c = cart_for(True)
        conn = db()
        try:
            for pid in ids:
                p = one('SELECT id,stock FROM products WHERE id=? AND active=1', (pid,))
                if not p or int(p['stock']) < 1:
                    raise ValueError('One of your selected products is no longer available.')
            for pid in ids:
                existing = one('SELECT id FROM cart_items WHERE cart_id=? AND product_id=? AND recipient=? AND message=? AND wrap=0 AND card=0',
                               (c['id'], pid, 'BroVault Gift Box', 'Curated gift box'))
                if existing:
                    conn.execute('UPDATE cart_items SET quantity=quantity+1 WHERE id=?', (existing['id'],))
                else:
                    conn.execute('INSERT INTO cart_items(cart_id,product_id,quantity,recipient,message,wrap,card) VALUES(?,?,?,?,?,?,?)',
                                 (c['id'], pid, 1, 'BroVault Gift Box', 'Curated gift box', 0, 0))
            conn.commit()
            session.pop('pending_gift_box', None)
            flash('Your gift box items were added to the cart.', 'success')
            return redirect(url_for('cart'))
        except Exception as exc:
            try: conn.connection.rollback()
            except Exception: pass
            flash(str(exc) if isinstance(exc, ValueError) else 'Could not add the gift box. Please try again.', 'error')
            return redirect(url_for('gift_box'))
    return render_template('gift_box.html', products=products)

@app.route('/about')
def about():
    return render_template('info.html', page_title='About BroVault',
        eyebrow='THE ART OF GIVING', body='BroVault curates thoughtful gifts and everyday accessories for him. From signature scents to timeless essentials, every pick is made to leave a lasting impression.')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name=request.form.get('name','').strip()
        email=request.form.get('email','').strip()
        message=request.form.get('message','').strip()
        if not name or '@' not in email or len(message)<5:
            flash('Please complete your name, a valid email and a message.', 'error')
        else:
            # This starter project does not configure email delivery; avoid a false sent-message claim.
            flash('Your message is ready, but email delivery is not configured. Please contact the store administrator directly.', 'info')
    return render_template('contact.html')

if __name__=='__main__': init(); app.ready=True; app.run(host='127.0.0.1',port=5000,debug=False)
