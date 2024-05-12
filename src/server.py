from flask import Flask, redirect, render_template, request, session, flash, url_for
from sqlalchemy import create_engine, text

from pathlib import Path
import secrets
from hashlib import sha256
import datetime


EXECUTING_DIRECTORY = Path(__file__).parent.resolve()

# Initialize Flask
app = Flask(__name__)
app.secret_key = secrets.token_hex()

# Connect to database
DB_USERNAME = "root"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_DB = "cset180final"

engine = create_engine(f"mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DB}")
sql = engine.connect()

def run_query(query, parameters = None):
	return sql.execute(text(query), parameters)

def run_file(path, parameters = None):
	path = (EXECUTING_DIRECTORY / path).resolve()

	file = open(path)

	return run_query(file.read(), parameters)

# Set up database
run_file("./scripts/db/setup.sql")


# Functions
def get_query_rows(query, parameters = None):
	results = run_query(query, parameters)

	if not results:
		return []

	results = results.all()

	list_rows = []

	for row in results:
		list_rows.append(row._mapping)

	return list_rows

# Check if account exists
def user_exists(user_id):
	"""
	:param int user_id:

	:return:
		True if the account associated with the user_id exists

		False otherwise

	:rtype: bool
	"""

	account = get_query_rows(f"select * from `users` where `id` = {user_id}")

	if len(account) < 1:
		return False

	return True

# End of check if account exists

# Login check for email address
def check_user_email(email_address):
	"""
	:param str email_address: The email associated with a user

	:return:
		The user id if the user account exists

		False otherwise

	:rtype:
		int if the email exists

		bool otherwise

	"""

	user = get_query_rows(f"select * from `users` where `email_address` = '{email_address}'")

	if len(user) < 1:
		return False

	return user[0].id

# Login check for username
def check_user_username(username):
	"""
	:param str username: The username associated with a user

	:return:
		The user id if the user account exists

		False otherwise

	:rtype:
		int if the email exists

		bool otherwise

	"""

	user = get_query_rows(f"select * from `users` where `username` = '{username}'")

	if len(user) < 1:
		return False

	return user[0].id

# Create test accounts
def create_user_account(account_type, username, first_name, last_name, email_address, password):
	if account_type not in ("customer", "vendor", "admin"):
		return

	if check_user_username(username):
		print("Duplicate username")
		return

	if check_user_email(email_address):
		print("Duplicate email address")
		return

	run_query(f"""
		insert into `users`
		values
		(
		   null,
		   '{username}',
		   '{first_name}',
		   '{last_name}',
		   '{email_address}',
		   '{sha_hash(password)}'
		);
	""")

	run_query(f"""
		insert into `{account_type}s`
		values
		(
			null,
			(select last_insert_id())
		);
	""")

# Sessions
def destroy_session(session):
	"""
	Destroys the session if it exists
	:param session:

	:return:
		False if session does not exist

		Nothing otherwise
	"""

	if not session:
		return False

	if session.get("user_id"):
		del session["user_id"]

	if session.get("username"):
		del session["username"]

	if session.get("email_address"):
		del session["email_address"]

def validate_session(session):
	"""
	:param session:

	:return:
		True if username and email are correct for user

		False otherwise

	:rtype: bool
	"""

	if not session:
		return False

	user_id = session.get("user_id")
	username = session.get("username")
	email_address = session.get("email_address")

	if not user_id or not username or not email_address:
		return False

	return user_id == check_user_username(username) == check_user_email(email_address)

# End of sessions

# Login Validation
def sha_hash(s):
	return sha256(s.encode("utf-8")).hexdigest()

def validate_email_login(email, password):
	"""
	Checks if the password matches the stored password associated with email

	:param email:
	:param password:

	:return:
		True if the password matches the stored password associated with email

		False otherwise

	:rtype: bool
	"""

	if not check_user_email(email):
		return False

	stored_password = get_query_rows(f"select `password` from `users` where `email_address` = '{email}'")

	if len(stored_password) < 1:
		return False

	stored_password = stored_password[0].password.decode("utf-8")
	return sha_hash(password) == stored_password

def validate_username_login(username, password):
	"""
	Checks if the password matches the stored password associated with email

	:param username:
	:param password:

	:return:
		True if the password matches the stored password associated with username

		False otherwise

	:rtype: bool
	"""
	if not check_user_username(username):
		return False

	stored_password = get_query_rows(f"select `password` from `users` where `username` = '{username}'")

	if len(stored_password) < 1:
		return False

	stored_password = stored_password[0].password.decode("utf-8")
	return sha_hash(password) == stored_password

# End of login validation

# Get account id
def get_customer_id(user_id):
	"""
	:param user_id:

	:return:
		The customer_id associated with the user_id if the account is customer account

		False otherwise

	:rtype:
		int if the account is customer account

		bool otherwise
	"""

	customer_id = get_query_rows(f"select `id` from `customers` where `user_id` = {user_id}")

	if len(customer_id) < 1:
		return False

	return customer_id[0].id

def get_vendor_id(user_id):
	"""
	:param user_id:

	:return:
		The vendor_id associated with the user_id if the account is vendor account

		False otherwise

	:rtype:
		int if the account is vendor account

		bool otherwise
	"""

	vendor_id = get_query_rows(f"select `id` from `vendors` where `user_id` = {user_id}")

	if len(vendor_id) < 1:
		return False

	return vendor_id[0].id

def get_admin_id(user_id):
	"""
	:param user_id:

	:return:
		The admin_id associated with the user_id if the account is admin account

		False otherwise

	:rtype:
		int if the account is admin account

		bool otherwise
	"""

	admin_id = get_query_rows(f"select `id` from `admins` where `user_id` = {user_id}")

	if len(admin_id) < 1:
		return False

	return admin_id[0].id

# End of get account id

# Get username
def get_username(user_id):
	"""
	:param int user_id:

	:return:
	The username associate with the user_id if the account exists

	False otherwise

	:rtype:
	str if the account exists

	bool otherwise
	"""

	username = get_query_rows(f"select `username` from `users` where `id` = {user_id}")

	if len(username) < 1:
		return False

	return username[0].username

# End of get username

# Get email address
def get_email(user_id):
	"""
	:param int user_id:

	:return:
	The email associate with the user_id if the account exists

	False otherwise

	:rtype:
	str if the account exists

	bool otherwise
	"""

	email = get_query_rows(f"select `email_address` from `users` where `id` = {user_id}")

	if len(email) < 1:
		return False

	return email[0].email_address

# End of get email addresss=

# Get account type
def get_account_type(user_id):
	"""
	:param user_id:

	:return:
		"admin", "customer", or "vendor" if the user_id exists

		False otherwise

	:rtype:
		str if the user_id exists

		bool otherwise
	"""

	if get_customer_id(user_id):
		return "customer"

	if get_vendor_id(user_id):
		return "vendor"

	if get_admin_id(user_id):
		return "admin"

	return False

# End of get account type

# End of accounts

# Products
# Create products
def create_product(name, description, vendor_id, quantity, price):
	"""
	:param str name:
	:param str description:
	:param int/str vendor_id:
	:param int quantity:
	:param int/float price:

	:return:
		product_id

	:rtype:
		int
	"""
	#TODO Validate vendor_id

	if quantity < 0:
		raise Exception("Quantity must be greater than 0")

	if price < 0:
		raise Exception("Price must be greater than 0.00")

	price = f"{price : 0.2f}"

	run_query(f"""
		insert into `products`
		values
		(
			null,
			'{name}',
			'{description}',
			{vendor_id},
			{quantity},
			{price}
		);
	""")

	return get_query_rows(f"select last_insert_id() as `id`")[0].id

# End of creating products

# Check if product id exists
def product_id_exists(product_id):
	"""
	:return:
		True if the product_id exists

		False otherwise
	"""

	id = get_query_rows(f"select `id` from `products` where `id`=  {product_id};")

	if len(id) < 1:
		return False

	return True

# End of check if product id exits

# Create product images
def create_product_images(product_id, images):
	"""
	:param int product_id:
	:param list images:
	"""

	for image in images:
		run_query(f"insert into `product_images` values ( {product_id}, '{image}' );")

# End of creating product images

# Create product discount
def create_product_discount(product_id, discount, start_date, end_date = None):
	# Validate product_id
	if not product_id_exists(product_id):
		return

	# Check discount format
	if discount < 0 or discount > 1:
		raise Exception("Discount must be between 0.00 and 1.00")

	# TODO check format of start_date

	# Format end_date
	if end_date:
		# TODO check format of end_date if not None

		end_date = f"'{end_date}'"
	else:
		end_date = f"'9999-12-31 23:59:59'"

	run_query(f"""
		insert into `product_discounts`
		values
		(
			null,
			{product_id},
			{discount},
			'{start_date}',
			{end_date}
		);
	""")

# End of creating product discount

# Create product warranty
def create_product_warranty(product_id, days, coverage):
	if not product_id_exists(product_id):
		return

	if not days:
		days = "null"

	run_query(f"""
		insert into `product_warranty`
		values
		(
		   null,
		   {product_id},
		   {days},
		   '{coverage}'
		);
	""")

# End of create product warranty

# Get product_id
def get_product_id(vendor_id, name):
	"""
	:vendor_id:
	:param str name: the product name


	:return:
		The product_id associated with the vendor_id and product_name

		False if there is no such product

	:rtype:
		int

		bool if there is no such product
	"""

	product_id = get_query_rows(f"select `id` from `products` where `vendor_id` = {vendor_id} and `name` = '{name}';")

	if len(product_id) < 1:
		return False

	return product_id[0].id

# End of get product id

# Get product info
def get_product_info(product_id):
	"""
	:return:
		All the data in the product table associated with the product_id

		False if the product_id does not exist
	"""

	if not product_id_exists(product_id):
		return False

	info = get_query_rows(f"select * from `products` where `id` = {product_id};")

	return info

# End of get product info

# Get product images
def get_product_images(product_id):
	"""
	:return:
		List of product images if they exist

		An empty list if there are no images or the product_id does not exist
	"""

	# Check if the product id exists
	if not product_id_exists(product_id):
		return []

	images = get_query_rows(f"select * from `product_images` where `product_id` = {product_id};")

	# Check if there are images
	if len(images) < 1:
		return []

	images_list = []

	for image in images:
		images_list.append(image.image_data)

	return images_list

# End of get product images

# Get product discounts
def get_product_discounts(product_id, type):
	"""
	:param int product_id:

	:param str type: "expired", "active", or "upcoming"

	:return:
		All the discounts of the product_id meeting the type if there are discounts

		An empty list if there are no discounts or the type is not a supported type
	"""

	discounts = None

	match type:
		case "expired":
			discounts = get_query_rows(f"select * from `product_discounts` where now() > `end_date` and `product_id` = {product_id};")
		case "active":
			discounts = get_query_rows(f"select * from `product_discounts` where now() between `start_date` and `end_date` and `product_id` = {product_id};")
		case "upcoming":
			discounts = get_query_rows(f"select * from `product_discounts` where now() < `start_date` and `product_id` = {product_id};")
		case _:
			return []

	return discounts

# Get end date of current discount
def get_current_discount_end(product_id):
	return get_query_rows(f"""
		select `end_date`
		from `product_discounts`
		where `discount` =
		(
			select max(`discount`) as `current_discount`
			from `product_discounts`
			where now() between `start_date` and `end_date` and `product_id` = {product_id}
		);
	""")

# Get product warranty
def get_product_warranties(product_id):
	warranty = get_query_rows(f"select * from `product_warranty` where `product_id` = {product_id};")

	return warranty

# End of get product warranty

# Get product data
def get_product_data(product_id):
	"""
	:param int product_id:

	:return:
		Format:

		{
			id: 1,
			images: ["", ""] or [],
			name: "",
			description: "",
			vendor_username: "",
			quantity: 0,
			original_price: 0.00,
			expired_discounts: [{}, {}] or [],
 			active_discounts: [{}, {}] or [],
			current_discount: 0.00 or None,
			current_discount_end: "" or None,
			discounted_price: 0.00 or None,
			current_price: original_price or discounted_price
 			upcoming_discounts: [{}, {}],
 			warranties: [{}, {}] or []
		}

		{} if the product_id does not exist
	"""

	# TODO maybe return a dictionary of the format instead
	if not product_id_exists(product_id):
		return {}

	data  = {}

	data["id"] = product_id
	data["images"] = get_product_images(product_id)

	product_info = get_product_info(product_id)[0]

	data["name"] = product_info.name
	data["description"] = product_info.description

	username = get_query_rows(f"""
		select `username` from `users` as `u`
		where `u`.`id` =
		(
			select `user_id` from `vendors` as `v`
			where `v`.`id` =
			(
				select `vendor_id` from `products` as `p`
				where `p`.`id` = {product_id}
			)
		);""")

	# TODO if vendor account deleted, there would be no username
	# Maybe handles that
	if len(username) < 1:
		username = "Deleted Vendor"
	else:
		username = username[0].username

	data["vendor_username"] = username
	data["quantity"] = product_info.quantity
	data["original_price"] = product_info.price

	# Discounts
	data["expired_discounts"] = get_product_discounts(product_id, "expired")
	data["active_discounts"] = get_product_discounts(product_id, "active")

	data["current_discount"] = get_query_rows(f"select max(`discount`) as `current_discount` from `product_discounts` where now() between `start_date` and `end_date` and `product_id` = {product_id};")[0].current_discount

	data["current_discount_end"] = get_current_discount_end(product_id)

	# Check if there is a discount
	if len(data["current_discount_end"]) < 1:
		data["current_discount_end"] = None

	# Format wording of date
	else:
		date = data["current_discount_end"][0].end_date

		if date == datetime.datetime(9999, 12, 31, 23, 59, 59):
			data["current_discount_end"] = "Forever"
		else:
			data["current_discount_end"] = data["current_discount_end"][0].end_date

	# TODO remove discounted_price and use current_price instead
	data["discounted_price"] = None

	# Format current_discount and discounted_price if there is an active discount
	if data["current_discount"] != None:
		data["current_discount"] = f"{int(float(data["current_discount"]) * 100)}"
		data["discounted_price"] = f"{(float(data["original_price"]) * (100 - float(data["current_discount"])) / 100) : 0.2f}"

	# Current price
	if data["current_discount"] != None:
		data["currrent_price"] = data["discounted_price"]
	else:
		data["currrent_price"] = data["original_price"]

	data["upcoming_discounts"] = get_product_discounts(product_id, "upcoming")

	data["warranties"] = get_product_warranties(product_id)

	return data

# Update products
def update_product(product_id, name, description, quantity, price):
	run_query(f"""
		update `products`
		set
			`name` = '{name}',
			`description` = '{description}',
			`quantity` = {quantity},
			`price` = {price}
		where `id` = {product_id};
	""")

	sql.commit()

# Update product images
def update_product_images(product_id, images):
	"""
	:param int/str product_id:
	:param list images:
	"""

	# Better way. no time :/
	# TODO delete everything if len(images) == 0

	# TODO if len(images) <= num of images in database, loop through amount in database and update. delete the rest if they exist

	# TODO if len(images) > num of images in database, loop through amount in database and create new ones

	# Delete images
	run_query(f"delete from `product_images` where `product_id` = {product_id};")

	# Create images
	create_product_images(product_id, images)

	sql.commit()

# Update product warranties
def update_product_warranties(product_id, warranties):
	"""
	Deletes warranties and creates new ones

	:param int/str product_id:
	:param list of dictionaries warranties:
	"""

	# Better way. no time :/
	# TODO delete everything if len(warranties) == 0

	# TODO if len(warranties) <= num of warranties in database, loop through amount in database and update. delete the rest if they exist

	# TODO if len(warranties) > num of warranties in database, loop through amount in database and create new ones

	# Delete warranties
	run_query(f"delete from `product_warranty` where `product_id` = {product_id};")

	# Create warranties
	for warranty in warranties:
		create_product_warranty(product_id, warranty.get("coverage_days"), warranty.get("coverage_info"))

	sql.commit()

# Update product discounts
def update_product_discounts(product_id, discounts):
	"""
	Deletes discounts and creates new ones

	No time to do this better

	:param int/str product_id:
	:param list of dictionaries discounts:
	"""

	# Better way. no time :/
	# TODO delete everything if len(discounts) == 0

	# TODO if len(discounts) <= num of discounts in database, loop through amount in database and update. delete the rest if they exist

	# TODO if len(discounts) > num of discounts in database, loop through amount in database and create new ones

	# Delete discounts
	run_query(f"delete from `product_discounts` where `id` = {product_id};")

	# Create discounts
	for discount in discounts:
		create_product_discount(product_id, float(discount.get("discount")), discount.get("start_date"), discount.get("end_date"))

	sql.commit()


# End of products

# Cart
# Create cart
def create_cart(user_id):
	"""
	:return:
		The cart_id

	:rtype: int
	"""

	if not user_exists(user_id):
		return

	run_query(f"insert into `carts` values (null, {user_id});")

	sql.commit()

	return get_query_rows(f"select last_insert_id() as `id`")[0].id

def get_current_cart(user_id):
	"""
	:return:
		The current cart_id associated with the user_id if there is one

		None otherwise
	"""

	# Get max cart_id of user where not in orders table
	cart_id = get_query_rows(f"""
		select max(`id`) as `id` from `carts` as `c`
		where
		(
			`c`.`user_id` = {user_id}
			and `c`.`id` not in
			(select `id` from `orders` as `o` where `c`.`id` = `o`.`cart_id`)
		);
	""")

	if cart_id[0].id == None:
		return

	return cart_id[0].id

# Check cart id in carts
def cart_id_exists(cart_id):
	"""
	:return:
		True if the cart_id exists in carts table

		False otherwise
	"""

	id = get_query_rows(f"select `id` from `carts` where `id` = {cart_id};")

	if len(id) < 1:
		return False

	return True

# Check if item in cart alredy
def cart_item_exists(cart_id, product_id):
	"""
	:return:
		1 if the product already exists in the cart

		0 otherwise
	"""

	return get_query_rows(f"select exists(select * from `cart_items` where `cart_id` = {cart_id} and `product_id` = {product_id}) as `exists`;")[0].exists

# Update quantity of item in cart
def update_cart_item_quantity(cart_id, product_id):
	"""
	Updates the quantity of the item in cart if the item already exists in cart
	"""

	run_query(f"""
		update `cart_items`
		set `quantity` = `quantity` + 1
		where `cart_id` = {cart_id} and `product_id` = {product_id};
	""")

	sql.commit()

# Add to cart
def add_to_cart(cart_id, product_id):
	# Check if cart_id exists
	if not cart_id_exists(cart_id):
		return

	# Check if product_id exists
	if not product_id_exists(product_id):
		return

	# Update quantity if item already in cart
	if cart_item_exists(cart_id, product_id):
		update_cart_item_quantity(cart_id, product_id)

	# Add item to cart
	else:
		run_query(f"""
			insert into `cart_items`
			values
			(
				null,
				{cart_id},
				{product_id},
				1
			);
		""")

		sql.commit()
# End of functions

# Insert test values
# Accounts
# Customer accounts
create_user_account("customer", "customer", "Customer", "Account", "c@c.c", "c")
create_user_account("customer", "lawrencetheflorence", "Jessica", "Lawrence", 'jessicalawrence@gmail.com', 'j')

# Vendor accounts
create_user_account("vendor", 'food_schmood', 'Food', 'Schmood', 'contact@foodschmood.com', 'f')
create_user_account("vendor", 'the_clean_mile', 'Clean', 'Mile', 'contact@thecleanmile.com', 'c')

# Admin accounts
create_user_account("admin", 'rcampbell', 'Rebecca', 'Campbell', 'rebecca_campbell@gmail.com', 'r')

# Products
# Food Schmood
# Silicone Baking Mat
create_product('Silicone Baking Mat', 'A non-stick silicone mat for baking, suitable for use in ovens and microwaves.', get_vendor_id(check_user_username("food_schmood")), 100, 9.99)
create_product_images(get_product_id(get_vendor_id(check_user_username("food_schmood")), "Silicone Baking Mat"), [
	"https://cdn.pixabay.com/photo/2017/05/31/08/35/kitchen-accessories-2359484_1280.jpg",
	"https://cdn.pixabay.com/photo/2020/02/29/10/17/pretzels-4889633_1280.jpg"
])
create_product_discount(get_product_id(get_vendor_id(check_user_username("food_schmood")), "Silicone Baking Mat"), 0.20, "2024-05-04 00:00:00")
# This is just to test a lifetime warranty
create_product_warranty(1, None, "not realistic. just a lifetime warranty test")

# Bamboo Cutting Board
create_product('Bamboo Cutting Board','A durable bamboo cutting board for slicing and chopping ingredients.', get_vendor_id(check_user_username("food_schmood")), 90, 14.99)
create_product_discount(get_product_id(get_vendor_id(check_user_username("food_schmood")), "Bamboo Cutting Board"), 0.10, "2024-05-04 00:00:00", "2024-05-17 00:00:00")
create_product_warranty(2, 30, "Returnable within 30 days")

# The Clean Mile
# Microfiber Cleaning Cloths
create_product('Microfiber Cleaning Cloths','Pack of reusable and absorbent microfiber cleaning cloths for versatile cleaning tasks.', get_vendor_id(check_user_username("the_clean_mile")), 300, 4.99)
create_product_discount(get_product_id(get_vendor_id(check_user_username("the_clean_mile")), "Microfiber Cleaning Cloths"), 0.05, "2024-05-02 00:00:00", "2024-05-03 00:00:00" )

# Latex Cleaning Gloves
create_product('Latex Cleaning Gloves','Durable latex gloves for protecting hands during cleaning chores.', get_vendor_id(check_user_username("the_clean_mile")), 400, 2.99)
create_product_discount(get_product_id(get_vendor_id(check_user_username("the_clean_mile")), "Latex Cleaning Gloves"), 0.15, "2024-06-01 00:00:00")

sql.commit()
# End of inserting test values

# Routes
# Home route
@app.route("/")
@app.route("/home/")
def home():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	return render_template("home.html", account_type = session.get("account_type"))

# Login route
@app.route("/login/")
def create_login():
	destroy_session(session)

	return render_template("login.html", no_navbar = True)

@app.route("/login/", methods=[ "POST" ])
def check_login():
	username_email = request.form.get("username_email")
	password = request.form.get("password")

	# Check if username or email exists
	username_check = check_user_username(username_email)
	email_check = check_user_email(username_email)

	if not username_check and not email_check:
		return render_template(
			"login.html",
			message = "This username or email does not exist",
			no_navbar = True
		)

	# Check login through username
	if username_check:
		if validate_username_login(username_email, password):
			session["user_id"] = username_check
			session["email_address"] = get_email(username_check)
			session["username"] = get_username(username_check)
			session["account_type"] = get_account_type(username_check)

		else:
			return render_template(
				"login.html",
				message = "Incorrect password",
				no_navbar = True
			)

	# Check login through email
	elif email_check:
		if validate_email_login(username_email, password):
			session["user_id"] = email_check
			session["email_address"] = get_email(email_check)
			session["username"] = get_username(email_check)
			session["account_type"] = get_account_type(email_check)

		else:
			return render_template(
				"login.html",
				message = "Incorrect password",
				no_navbar = True
			)

	return redirect("/home")


# Sign up route
@app.route("/signup/")
def create_signup():
	destroy_session(session)

	return render_template("signup.html", no_navbar = True)

@app.route("/signup/", methods = [ "POST" ])
def check_signup():
	username = request.form.get("username")
	email_address = request.form.get("email_address")
	password = request.form.get("password")
	password_confirm = request.form.get("password_confirm")

	# Check if passwords match
	if password != password_confirm:
		return render_template(
			"signup.html",
			no_navbar = True,
			message = "Passwords do not match"
		)

	# Check if account with that email address exists
	if check_user_email(email_address):
		return render_template(
			"signup.html",
			no_navbar = True,
			message = "An account with that email addresss already exists"
		)

	# Check if account with that username exists
	if check_user_username(username):
		return render_template(
			"signup.html",
			no_navbar = True,
			message = "An account with that username already exists"
		)

	first_name = request.form.get("first_name")
	last_name = request.form.get("last_name")

	# Insert into users table
	try:
		run_query(f"""
			insert into `users`
			values
			(
				null,
				'{username}',
				'{first_name}',
				'{last_name}',
				'{email_address}',
				'{sha_hash(password)}'
			);
		""")

		# Insert into customers or vendors table
		account_type = request.form.get("account_type")

		if not account_type in ("customers", "vendors"):
			raise Exception("Invalid account type")

		run_query(f"insert into `{account_type}` values ( null, {check_user_email(email_address)} );")

		sql.commit()

		return redirect("/login")

	except:
		return render_template(
			"signup.html",
			no_navbar = True,
			message = "Sorry, your account could not be created"
		)

# Products route
@app.route("/products/")
def view_products():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	products = get_query_rows(f"select * from `products`")

	if len(products) < 1:
		return render_template(
			"products.html",
			account_type = session.get("account_type")
		)

	# Get vendor products if vendor account
	if session.get("account_type") == "vendor":
		vendor_id = get_vendor_id(session.get("user_id"))
		products = get_query_rows(f"select * from `products` where `vendor_id` = {vendor_id};")

	# Get all the product_ids
	product_ids = []

	for product in products:
		product_ids.append(product.id)

	# print(f"product_ids: {product_ids}")

	# Get all the data of each product
	product_data = []

	for id in product_ids:
		product_data.append(get_product_data(id))

	# print(f"product_data: {product_data}")

	return render_template(
		"products.html",
		account_type = session.get("account_type"),
		product_data = product_data
	)

# Products info route
@app.route("/products/<id>")
def display_product_info(id):

	# For some reason after creating a product with images,
	# this route is triggering with the first image of the product passed here as `id`
	try:
		int(id)
	except:
		return redirect("/products")

	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	# print(f"product info id: {id}")

	# Prevent vendor from accessing product info of another vendor
	if session.get("account_type") == "vendor":
		vendor_id = get_vendor_id(session.get("user_id"))
		vendor_product_ids = get_query_rows(f"select `id` from `products` where `vendor_id` = {vendor_id};")

		if len(vendor_product_ids) < 1:
			return redirect("/products")

		id_list = []

		for data in vendor_product_ids:
			id_list.append(data.id)

		if int(id) not in id_list:
			return redirect("/products")

	return render_template(
		"product_info.html",
		account_type = session.get("account_type"),
		data = get_product_data(id)
	)

def route_add_to_cart():
	product_id = request.get_json().get("product_id")

	cart_id = get_current_cart(session.get("user_id"))

	add_to_cart(cart_id, product_id)

	product_name = get_product_info(product_id)[0].name

	return f"{product_name} has been added"

@app.route("/products", methods = [ "POST" ])
def products_add_to_cart():
	return route_add_to_cart()

@app.route("/products/<id>", methods = [ "POST" ])
def products_info_add_to_cart(id):
	return route_add_to_cart()

def route_delete_product():
	product_id = request.get_json().get("product_id")

	run_query(f"delete from `products` where `id` = {product_id};")

	sql.commit()

	# return redirect(url_for('products')) # Not working

	return {
		"response": "/products"
	}

@app.route("/products", methods = [ "DELETE" ])
def products_delete_product():
	return route_delete_product()

@app.route("/products/<id>", methods = [ "DELETE" ])
def products_info_delete_product(id):
	return route_delete_product()

@app.route("/products/create")
def display_product_create():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	# Validate account type
	if session.get("account_type") not in ["vendor", "admin"]:
		return redirect("/products")

	return render_template(
		"product_create.html",
		account_type = session.get("account_type")
	)

@app.route("/products/create", methods = [ "POST" ])
def post_product_create():
	data = request.get_json()

	vendor_id = data.get("vendor_id")
	if not vendor_id:
		vendor_id = get_vendor_id(session.get("user_id"))

	name = data.get("name")
	description = data.get("description")
	quantity = int(data.get("quantity"))
	price = float(data.get("price"))
	images = data.get("images")
	warranties = data.get("warranties")

	# Create product
	product_id = create_product(name, description, vendor_id, quantity, price)

	# Create product images
	create_product_images(product_id, images)

	# Create product warranties
	for warranty in warranties:
		create_product_warranty(product_id, warranty.get("coverage_days"), warranty.get("coverage_info"))

	sql.commit()

	return {
		"message": f"{name} has been created"
	}

@app.route("/products/edit/<id>")
def display_product_edit(id):
	# Make sure id is formatted as a number
	try:
		int(id)
	except:
		return redirect("/products")

	# Make sure user is logged in
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	# Validate account type
	if session.get("account_type") not in ["vendor", "admin"]:
		return redirect("/products")

	# Validate product is from vendor
	if session.get("account_type") == "vendor":
		vendor_id = get_vendor_id(session.get("user_id"))
		vendor_product_ids = get_query_rows(f"select `id` from `products` where `vendor_id` = {vendor_id};")

		# Vendor has no products
		if len(vendor_product_ids) < 1:
			return redirect("/products")

		# Vendor trying to access a product that is not theirs

		id_list = []

		for data in vendor_product_ids:
			id_list.append(data.id)

		if int(id) not in id_list:
			return redirect("/products")

	return render_template(
		"product_edit.html",
		data = get_product_data(id)
	)

@app.route("/products/edit/<id>", methods = [ "PUT" ])
def update_product_info(id):
	data = request.get_json()

	# Update product info
	product_id = data.get("product_id")
	name = data.get("name")
	description = data.get("description")
	quantity = data.get("quantity")
	price = data.get("price")

	update_product(product_id, name, description, quantity, price)

	# Update product images
	images = data.get("images")

	update_product_images(product_id, images)

	# Update warranties
	warranties = data.get("warranties")

	update_product_warranties(product_id, warranties)

	# Update upcoming discounts
	upcoming_discounts = data.get("discounts")

	update_product_discounts(product_id, upcoming_discounts)

	return {
		"message": "Updated successfully",
		"url": f"/products/{product_id}"
	}

# End of routes

if __name__ == "__main__":
	app.run()
