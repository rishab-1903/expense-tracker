from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Expense, Category
from app.forms import ExpenseForm, CategoryForm

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    category_form = CategoryForm()
    expense_form = ExpenseForm()

    # Fetch categories and set choices BEFORE validating the form
    categories = Category.query.filter_by(user_id=current_user.id).all()
    expense_form.category.choices = [(cat.id, cat.name) for cat in categories]  # ✅ Must be set

    # Handle category form
    if category_form.validate_on_submit() and category_form.submit.data:
        new_name = category_form.name.data.strip().lower()
    
        # Check if this category name lready existr
        existing_category = Category.query.filter(
            Category.user_id == current_user.id,
            db.func.lower(Category.name) == new_name
        ).first()
    
        if existing_category:
            flash("Category already exist.", "danger")
        else:
            new_category = Category(name=category_form.name.data.strip(), user_id=current_user.id)
            db.session.add(new_category)
            db.session.commit()
            flash("Category added!", "success")
    
        return redirect(url_for('dashboard.dashboard'))

    # Handle expense form
    if expense_form.validate_on_submit() and expense_form.submit.data:
        new_expense = Expense(
            date=expense_form.date.data,
            description=expense_form.description.data,
            amount=expense_form.amount.data,
            category_id=expense_form.category.data,  # already an ID
            user_id=current_user.id
        )
        db.session.add(new_expense)
        db.session.commit()
        flash("Expense added!", "success")
        return redirect(url_for('dashboard.dashboard'))

    # Get user's expenses
    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    # Prepare data for chart
    grouped = (
        db.session.query(Category.name, func.sum(Expense.amount))
        .join(Expense)
        .filter(Category.user_id == current_user.id)
        .group_by(Category.name)
        .all()
    )
    labels = [row[0] for row in grouped]
    values = [float(row[1]) for row in grouped]

    return render_template(
        'dashboard.html',
        category_form=category_form,
        expense_form=expense_form,
        expenses=expenses,
        labels=labels,
        values=values
    )