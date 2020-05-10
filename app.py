import os

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
condition = [True]

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index(try_login=False):
    title = "Home"
    return render_template("index.html", title=title, condition = condition[-1], try_login=try_login)

@app.route("/logout")
def logout():
    condition.append(False)
    return index()   

@app.route("/login", methods=["POST"])
def login():
    username_fill = request.form.get("username")
    password_fill = request.form.get("password")
    users = db.execute("SELECT USERNAME, PASSWORD FROM users")
    usernames = []
    passwords = []
    for user in users:
        username = user.username
        usernames.append(username)
        password = user.password
        passwords.append(password)

    if(username_fill in usernames):
        if(passwords[usernames.index(username_fill)] == password_fill):
            condition.append(True)
            return index()
        else:
            return index(try_login=True)
    else:
        return index(try_login=True)
   

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    db.execute("INSERT INTO users(USERNAME, PASSWORD) VALUES (:username, :password)",
                {"username" : username, "password" : password})
    db.commit()
    return index()

def get_values(before, after):
    for row in before:
        after.append(row)

@app.route("/database")
def more():
    title = "Database"

    values = db.execute("SELECT * FROM Ref_Types_of_Business")
    ref_types_values = []
    get_values(values, ref_types_values)

    customers_values = []
    values = db.execute("SELECT * FROM Customers")
    get_values(values, customers_values)

    locations_values = []
    values = db.execute("SELECT * FROM Locations")
    get_values(values, locations_values)

    products_values = []
    values = db.execute("SELECT * FROM Products")
    get_values(values, products_values)

    trans_types_values = []
    values = db.execute("SELECT * FROM Ref_Transaction_Types")
    get_values(values, trans_types_values)

    trans_values = []
    values = db.execute("SELECT * FROM Transactions")
    get_values(values, trans_values)

    return render_template("more.html", title=title, condition=condition[-1], 
                            ref_types_values=ref_types_values, customers_values=customers_values, locations_values=locations_values,
                            products_values=products_values, trans_types_values=trans_types_values, trans_values=trans_values)

@app.route("/addref", methods=["POST"])
def ref_types():
    code = request.form.get("code")
    desc = request.form.get("desc")
    try:
        db.execute("INSERT INTO ref_types_of_business(Type_of_Business_Code, Type_of_Business_Desc) VALUES (:code, :desc)",
                    {"code" : code, "desc" : desc})
        db.commit()
    except:
        return "ERROR INSERTING!"
    return redirect(url_for('.more'))

@app.route("/addcust", methods=["POST"])
def customers():
    ids = request.form.get("id")
    code = request.form.get("code")
    name = request.form.get("name")
    address = request.form.get("address")
    desc = request.form.get("desc")
    try:
        db.execute("INSERT INTO customers(Customer_ID, Type_of_Business_Code, Customer_Name, Customer_Address, Other_Details) VALUES (:ids, :code, :name, :address, :desc)",
                    {"ids": ids, "code" : code, "name" : name, "address" : address,"desc" : desc})
        db.commit()
    except:
        return "ERROR INSERTING!"
    return redirect(url_for('.more'))

@app.route("/addloc", methods=["POST"])
def locations():
    code = request.form.get("code")
    name = request.form.get("name")
    desc = request.form.get("desc")
    try:
        db.execute("INSERT INTO locations(Location_Code, Location_Name, Location_Description) VALUES (:code, :name, :desc)",
                    {"code" : code, "name" : name, "desc" : desc})
        db.commit()
    except:
        return "ERROR INSERTING!"
    return redirect(url_for('.more'))

@app.route("/addprod", methods=["POST"])
def products():
    code = request.form.get("code")
    name = request.form.get("name")
    desc = request.form.get("desc")
    oth = request.form.get("oth")
    try:
        db.execute("INSERT INTO Products(Product_ID, Product_Name, Product_Description, Other_Details) VALUES (:code, :name, :desc, :oth)",
                    {"code" : code, "name" : name, "desc" : desc, "oth" : oth})
        db.commit()
    except:
        return "ERROR INSERTING!"
    return redirect(url_for('.more'))

@app.route("/addtranstypes", methods=["POST"])
def transaction_types():
    code = request.form.get("code")
    name = request.form.get("name")
    try:
        db.execute("INSERT INTO Ref_Transaction_Types(Transaction_Type_Code, Transaction_Type_Description) VALUES (:code, :name)",
                    {"code" : code, "name" : name})
        db.commit()
    except:
        return "ERROR INSERTING!"
    return redirect(url_for('.more'))

@app.route("/addtrans", methods=["POST"])
def transactions():
    trans_id = request.form.get("trans_id")
    cust_id = request.form.get("cust_id")
    loc_code = request.form.get("loc_code")
    prod_id = request.form.get("prod_id")
    type_code = request.form.get("type_code")
    trans_date = request.form.get("trans_date")
    amount = int(request.form.get("amount"))
    count = int(request.form.get("count"))
    oth = request.form.get("oth")
    db.execute("INSERT INTO Transactions(Transaction_ID, Customer_ID, Location_Code, Product_ID, Transaction_Type_Code, Transaction_Date, Amount, Count, Other_Details) VALUES (:trans_id, :cust_id, :loc_code, :prod_id, :type_code, :trans_date, :amount, :count, :oth)",
                    {"trans_id":trans_id, "cust_id":cust_id, "loc_code":loc_code, "prod_id":prod_id, "type_code":type_code, "trans_date":trans_date, "amount":amount, "count":count, "oth":oth})
    db.commit()
    return redirect(url_for('.more'))

@app.route("/delref", methods=["POST"])
def del_ref_types():
    to_delete = str(request.form.get("delete"))
    try:
        command = "DELETE FROM Ref_Types_of_Business WHERE Type_of_Business_Code='{to_delete}'".format(to_delete=to_delete)
        db.execute(command)
        db.commit()
    except:
        return "ERROR DELETING!"
    return redirect(url_for('.more'))

@app.route("/delcust", methods=["POST"])
def del_customers():
    to_delete = str(request.form.get("delete"))
    try:
        command = "DELETE FROM Customers WHERE Customer_ID='{to_delete}'".format(to_delete=to_delete)
        db.execute(command)
        db.commit()
    except:
        return "ERROR DELETING!"
    return redirect(url_for('.more'))

@app.route("/delloc", methods=["POST"])
def del_loc():
    to_delete = str(request.form.get("delete"))
    try:
        command = "DELETE FROM Locations WHERE Location_Code='{to_delete}'".format(to_delete=to_delete)
        db.execute(command)
        db.commit()
    except:
        return "ERROR DELETING!"
    return redirect(url_for('.more'))

@app.route("/delprod", methods=["POST"])
def del_prod():
    to_delete = str(request.form.get("delete"))
    try:
        command = "DELETE FROM Products WHERE Product_ID='{to_delete}'".format(to_delete=to_delete)
        db.execute(command)
        db.commit()
    except:
        return "ERROR DELETING!"
    return redirect(url_for('.more'))

@app.route("/deltranstypes", methods=["POST"])
def del_trans_types():
    to_delete = str(request.form.get("delete"))
    try:
        command = "DELETE FROM Ref_Transactions_Types WHERE Transaction_Type_Code='{to_delete}'".format(to_delete=to_delete)
        db.execute(command)
        db.commit()
    except:
        return "ERROR DELETING!"
    return redirect(url_for('.more'))
    
@app.route("/deltrans", methods=["POST"])
def del_trans():
    to_delete = str(request.form.get("delete"))
    try:
        command = "DELETE FROM Transactions WHERE Transaction_ID='{to_delete}'".format(to_delete=to_delete)
        db.execute(command)
        db.commit()
    except:
        return "ERROR DELETING!"
    return redirect(url_for('.more'))