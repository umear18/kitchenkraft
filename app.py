"""
Kitchen Kraft — "Cook More With What You Have."
=================================================
A Flask web application that recommends recipes based on the ingredients
a user already has, and shows estimated nutrition information for each
recipe. This is the working initial-stage (Phase-1) prototype described
in the project synopsis / report.

Run with:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000

Demo login:  demo@kitchenkraft.app  /  demo1234
"""

import json
from datetime import date
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db, init_db

app = Flask(__name__)
app.secret_key = "kitchen-kraft-dev-secret-key"  # change this in production


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


CATEGORY_EMOJI = {
    "Rice": "🍚", "Curry": "🍛", "Dessert": "🍮", "Breakfast": "🥞",
    "Juices": "🥤", "Snack": "🥪",
}


@app.context_processor
def inject_helpers():
    def recipe_emoji(recipe):
        return CATEGORY_EMOJI.get(recipe["category"], "🍽️")
    return dict(recipe_emoji=recipe_emoji)


def current_user():
    if "user_id" not in session:
        return None
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()
    db.close()
    return user


def get_ingredients_grouped():
    """Return ingredients grouped by category, in a stable display order."""
    order = ["Fruits", "Vegetables", "Grains & Staples", "Ragi & Millets", "Rava & Flour",
             "Pulses & Legumes", "Dairy", "Non-Veg", "Seafood", "Spices & Herbs",
             "Nuts & Seeds", "Oils & Sauces", "Bakery & Others"]
    db = get_db()
    rows = db.execute("SELECT * FROM ingredients ORDER BY ingredient_name").fetchall()
    db.close()
    grouped = {cat: [] for cat in order}
    for row in rows:
        grouped.setdefault(row["category"], []).append(row)
    return {k: v for k, v in grouped.items() if v}


def match_recipes(available_ingredient_ids, meal_type=None, food_type=None):
    """
    Core ingredient-matching algorithm.

    match % = (number of required ingredients the user has / total required
               ingredients for the recipe) * 100

    This is the same logic documented in Chapter 6 (System Design) and
    Chapter 5 (Proposed Methodology) of the project report: a simple,
    explainable set-overlap score rather than a black-box model, which
    keeps the recommendation easy to justify to the user ("why was this
    recipe shown to me?").
    """
    db = get_db()
    query = "SELECT * FROM recipes WHERE 1=1"
    params = []
    if meal_type and meal_type != "All":
        query += " AND meal_type = ?"
        params.append(meal_type)
    if food_type and food_type != "All":
        query += " AND food_type = ?"
        params.append(food_type)
    recipes = db.execute(query, params).fetchall()

    available = set(available_ingredient_ids)
    results = []
    for recipe in recipes:
        req_rows = db.execute(
            """SELECT ri.ingredient_id, ri.quantity, i.ingredient_name, i.emoji
               FROM recipe_ingredients ri
               JOIN ingredients i ON i.ingredient_id = ri.ingredient_id
               WHERE ri.recipe_id = ?""",
            (recipe["recipe_id"],),
        ).fetchall()

        required_ids = [r["ingredient_id"] for r in req_rows]
        if not required_ids:
            continue

        have = [r for r in req_rows if r["ingredient_id"] in available]
        missing = [r for r in req_rows if r["ingredient_id"] not in available]
        match_pct = round((len(have) / len(required_ids)) * 100)

        if match_pct == 0:
            continue  # nothing in common — not worth showing

        results.append({
            "recipe": recipe,
            "match_pct": match_pct,
            "have_count": len(have),
            "total_count": len(required_ids),
            "missing": [m["ingredient_name"] for m in missing],
        })

    db.close()
    results.sort(key=lambda x: x["match_pct"], reverse=True)
    return results


# --------------------------------------------------------------------------
# Auth routes
# --------------------------------------------------------------------------

@app.route("/")
def landing():
    if "user_id" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        pref = request.form.get("food_preference", "Veg")

        if not name or not email or not password:
            flash("Please fill in all fields.", "error")
            return render_template("signup.html")

        db = get_db()
        existing = db.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("An account with that email already exists.", "error")
            db.close()
            return render_template("signup.html")

        db.execute(
            "INSERT INTO users (name, email, password_hash, food_preference) VALUES (?,?,?,?)",
            (name, email, generate_password_hash(password), pref),
        )
        db.commit()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()

        session["user_id"] = user["user_id"]
        flash(f"Welcome to Kitchen Kraft, {name}!", "success")
        return redirect(url_for("home"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("home"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# --------------------------------------------------------------------------
# Core app routes
# --------------------------------------------------------------------------

@app.route("/home")
@login_required
def home():
    db = get_db()
    popular = db.execute(
        """SELECT r.*, n.calories FROM recipes r
           LEFT JOIN nutrition n ON n.recipe_id = r.recipe_id
           ORDER BY r.recipe_id LIMIT 4"""
    ).fetchall()
    db.close()
    return render_template("home.html", user=current_user(), popular=popular)


@app.route("/my-kitchen", methods=["GET", "POST"])
@login_required
def my_kitchen():
    db = get_db()
    if request.method == "POST":
        ingredient_ids = request.form.getlist("ingredients")
        db.execute("DELETE FROM user_kitchen WHERE user_id = ?", (session["user_id"],))
        for ing_id in ingredient_ids:
            db.execute(
                "INSERT INTO user_kitchen (user_id, ingredient_id, quantity) VALUES (?,?,1)",
                (session["user_id"], ing_id),
            )
        db.commit()
        db.close()
        flash("Your kitchen has been updated.", "success")
        return redirect(url_for("what_can_i_cook"))

    selected = {row["ingredient_id"] for row in db.execute(
        "SELECT ingredient_id FROM user_kitchen WHERE user_id = ?", (session["user_id"],)
    ).fetchall()}
    db.close()

    grouped = get_ingredients_grouped()
    return render_template("my_kitchen.html", grouped=grouped, selected=selected, user=current_user())


@app.route("/what-can-i-cook")
@login_required
def what_can_i_cook():
    db = get_db()
    my_ingredients = db.execute(
        """SELECT i.* FROM user_kitchen uk JOIN ingredients i
           ON i.ingredient_id = uk.ingredient_id WHERE uk.user_id = ?
           ORDER BY i.ingredient_name""",
        (session["user_id"],),
    ).fetchall()
    db.close()

    ids = [i["ingredient_id"] for i in my_ingredients]
    meal_type = request.args.get("meal_type", "All")
    food_type = request.args.get("food_type", "All")

    results = match_recipes(ids, meal_type, food_type) if ids else []

    return render_template(
        "what_can_i_cook.html",
        my_ingredients=my_ingredients,
        results=results,
        meal_type=meal_type,
        food_type=food_type,
        user=current_user(),
    )


@app.route("/recipe/<int:recipe_id>")
@login_required
def recipe_details(recipe_id):
    db = get_db()
    recipe = db.execute("SELECT * FROM recipes WHERE recipe_id = ?", (recipe_id,)).fetchone()
    if not recipe:
        db.close()
        flash("Recipe not found.", "error")
        return redirect(url_for("what_can_i_cook"))

    ingredients = db.execute(
        """SELECT ri.quantity, i.ingredient_name, i.emoji, i.ingredient_id FROM recipe_ingredients ri
           JOIN ingredients i ON i.ingredient_id = ri.ingredient_id WHERE ri.recipe_id = ?""",
        (recipe_id,),
    ).fetchall()
    nutrition = db.execute("SELECT * FROM nutrition WHERE recipe_id = ?", (recipe_id,)).fetchone()

    my_ids = {r["ingredient_id"] for r in db.execute(
        "SELECT ingredient_id FROM user_kitchen WHERE user_id = ?", (session["user_id"],)
    ).fetchall()}

    is_favorite = db.execute(
        "SELECT 1 FROM favorites WHERE user_id = ? AND recipe_id = ?",
        (session["user_id"], recipe_id),
    ).fetchone() is not None

    similar = db.execute(
        """SELECT r.*, n.calories FROM recipes r LEFT JOIN nutrition n ON n.recipe_id = r.recipe_id
           WHERE r.category = ? AND r.recipe_id != ? LIMIT 4""",
        (recipe["category"], recipe_id),
    ).fetchall()
    db.close()

    steps = json.loads(recipe["instructions"])
    have_count = sum(1 for i in ingredients if i["ingredient_id"] in my_ids)
    match_pct = round((have_count / len(ingredients)) * 100) if ingredients else 0

    return render_template(
        "recipe_details.html",
        recipe=recipe, ingredients=ingredients, nutrition=nutrition, steps=steps,
        my_ids=my_ids, is_favorite=is_favorite, similar=similar, match_pct=match_pct,
        user=current_user(),
    )


@app.route("/recipe/<int:recipe_id>/toggle-favorite", methods=["POST"])
@login_required
def toggle_favorite(recipe_id):
    db = get_db()
    exists = db.execute(
        "SELECT 1 FROM favorites WHERE user_id = ? AND recipe_id = ?",
        (session["user_id"], recipe_id),
    ).fetchone()
    if exists:
        db.execute("DELETE FROM favorites WHERE user_id = ? AND recipe_id = ?", (session["user_id"], recipe_id))
        favorited = False
    else:
        db.execute("INSERT INTO favorites (user_id, recipe_id) VALUES (?,?)", (session["user_id"], recipe_id))
        favorited = True
    db.commit()
    db.close()
    if request.headers.get("X-Requested-With") == "fetch":
        return jsonify({"favorited": favorited})
    return redirect(request.referrer or url_for("recipe_details", recipe_id=recipe_id))


@app.route("/recipe/<int:recipe_id>/cook", methods=["POST"])
@login_required
def cook_recipe(recipe_id):
    db = get_db()
    db.execute(
        "INSERT INTO cooking_history (user_id, recipe_id, cooked_date, rating) VALUES (?,?,?,NULL)",
        (session["user_id"], recipe_id, str(date.today())),
    )
    db.commit()
    db.close()
    return redirect(url_for("dish_ready", recipe_id=recipe_id))


@app.route("/dish-ready/<int:recipe_id>")
@login_required
def dish_ready(recipe_id):
    db = get_db()
    recipe = db.execute("SELECT * FROM recipes WHERE recipe_id = ?", (recipe_id,)).fetchone()
    nutrition = db.execute("SELECT * FROM nutrition WHERE recipe_id = ?", (recipe_id,)).fetchone()
    db.close()
    return render_template("dish_ready.html", recipe=recipe, nutrition=nutrition, user=current_user())


@app.route("/favorites")
@login_required
def favorites():
    db = get_db()
    recipes = db.execute(
        """SELECT r.*, n.calories FROM favorites f
           JOIN recipes r ON r.recipe_id = f.recipe_id
           LEFT JOIN nutrition n ON n.recipe_id = r.recipe_id
           WHERE f.user_id = ?""",
        (session["user_id"],),
    ).fetchall()
    db.close()
    return render_template("favorites.html", recipes=recipes, user=current_user())


@app.route("/history")
@login_required
def history():
    db = get_db()
    rows = db.execute(
        """SELECT h.*, r.recipe_name, r.category FROM cooking_history h
           JOIN recipes r ON r.recipe_id = h.recipe_id
           WHERE h.user_id = ? ORDER BY h.cooked_date DESC""",
        (session["user_id"],),
    ).fetchall()
    db.close()
    return render_template("history.html", rows=rows, user=current_user())


@app.route("/profile")
@login_required
def profile():
    db = get_db()
    fav_count = db.execute("SELECT COUNT(*) c FROM favorites WHERE user_id = ?", (session["user_id"],)).fetchone()["c"]
    history_count = db.execute("SELECT COUNT(*) c FROM cooking_history WHERE user_id = ?", (session["user_id"],)).fetchone()["c"]
    db.close()
    return render_template("profile.html", user=current_user(), fav_count=fav_count, history_count=history_count)


@app.route("/help")
@login_required
def help_page():
    return render_template("help.html", user=current_user())


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
