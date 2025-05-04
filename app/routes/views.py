from flask import jsonify
from sqlalchemy import func

@views.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    category_form = CategoryForm()
    expense_form = ExpenseForm()
    expense_form.category.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]

    if category_form.validate_on_submit() and category_form.submit.data:
        new_cat = Category(name=category_form.name.data, user_id=current_user.id)
        db.session.add(new_cat)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('views.dashboard'))

    if expense_form.validate_on_submit() and expense_form.submit.data:
        new_exp = Expense(
            date=expense_form.date.data,
            description=expense_form.description.data,
            amount=expense_form.amount.data,
            category_id=expense_form.category.data,
            user_id=current_user.id
        )
        db.session.add(new_exp)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('views.dashboard'))

    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    # Summarize expenses by category
    summary = (
        db.session.query(Category.name, func.sum(Expense.amount))
        .join(Expense)
        .filter(Expense.user_id == current_user.id)
        .group_by(Category.name)
        .all()
    )

    labels = [item[0] for item in summary]
    values = [float(item[1]) for item in summary]

    return render_template(
        'dashboard.html',
        category_form=category_form,
        expense_form=expense_form,
        expenses=expenses,
        labels=labels,
        values=values
    )
