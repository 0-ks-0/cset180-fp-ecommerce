from flask import Flask, redirect, render_template, request, session
from sqlalchemy import create_engine, text

from pathlib import Path
import secrets
from hashlib import sha256

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
		True if the account associated with the user_id

		False otherwise

	:rtype: bool
	"""

	account = get_query_rows(f"select * from `users` where `user_id` = {user_id}")

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

# Creating test accounts
def create_user_account(account_type, username, first_name, last_name, email_address, password):
	"""
	:return:
		True if the account could be created
		False otherwise
	"""

	if account_type not in ("customer", "vendor", "admin"):
		return False

	if check_user_username(username):
		print("Duplicate username")
		return False

	if check_user_email(email_address):
		print("Duplicate email address")
		return False

	run_query(f"""
		insert into `users`
		values
		(
		   null,
		   '{username}',
		   '{first_name}',
		   '{last_name}',
		   '{email_address}',
		   '{sha_encrypt(password)}'
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

	return True

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
def sha_encrypt(s):
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
	return sha_encrypt(password) == stored_password

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
	return sha_encrypt(password) == stored_password

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

# End of functions

# Insert test values
# Customer account
run_query("""
	insert into `users`
	values
	(
		null,
		'customer',
		'Customer',
		'Account',
		'c@c.c',
		'2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6'
	);"""
)
run_query("insert into `customers` values( null, (select last_insert_id()) );")

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
			session["email_address"] = username_email
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
			session["email_address"] = username_email
			session["username"] = get_username(email_check)
			session["account_type"] = get_account_type(email_check)
		else:
			return render_template(
				"login.html",
				message = "Incorrect password",
				no_navbar = True
			)

	return render_template("home.html", account_type = session.get("account_type"))

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
				'{sha_encrypt(password)}'
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

# End of routes

if __name__ == "__main__":
 	app.run()
