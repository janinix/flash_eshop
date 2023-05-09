from market import app
from flask import render_template, redirect, url_for, flash,request
from market.models import Item, User
from market.forms import RegisterForm,LoginForm,PurchaseItemForm,SellItemForm,AddItemForm
from market import db
from flask_login import login_user,logout_user,login_required,current_user


@app.route('/home', methods=['GET', 'POST'])
def home_page():
    return render_template('home.html')

@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form=PurchaseItemForm()
    selling_form=SellItemForm()
    adding_form=AddItemForm()
    if adding_form.validate_on_submit():
        new_item=Item(name=adding_form.name.data,
                      price=int(adding_form.price.data),
                      barcode=adding_form.barcode.data,
                      description=adding_form.description.data)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('market_page'))

    if request.method=="POST":
        purchased_item=request.form.get('purchased_item')
        p_item_object=Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Purchase complete ! You purchased {p_item_object.name} for {p_item_object.price}$.",category="success")
            else:
                flash(f"You cant buy this item {p_item_object.name}, You dont have enough money",category="danger")
        #SELL ITEM
        sold_item=request.form.get('sold_item')
        s_item_object=Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"You sold {s_item_object.name} back to market.",category="success")
            else:
                flash(f"Something went wrong with selling {s_item_object.name}!")



        return redirect(url_for('market_page'))

    if request.method=="GET":
        items = Item.query.filter_by(owner=None)
        owned_items=Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items,purchase_form=purchase_form,owned_items=owned_items,selling_form=selling_form,adding_form=adding_form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created succesfully! You are logged as {user_to_create}",category="success")

        return redirect(url_for('market_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}',category='danger')

    return render_template('register.html', form=form)

@app.route('/login',methods=['GET','POST'])
def login_page():
    form=LoginForm()
    if form.validate_on_submit():
        attempted_user=User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Succesfull login ! Logged in as {attempted_user.username}',category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username or password are wrong !',category='danger')
    return  render_template('login.html',form=form)

@app.route('/logout',methods=['GET','POST'])
def logout_page():
    logout_user()
    flash("You have been logged out",category='info')
    return redirect(url_for("home_page"))