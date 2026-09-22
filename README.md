# 🍳 Kitchen Kraft — "Cook More With What You Have."

An ingredient-based recipe recommendation and health & nutrition web application.
This is the **Phase-1 working prototype**: a real, runnable Flask app implementing
the core flow described in the project synopsis — Login → My Kitchen → What Can I
Cook? → Recipe Details → Dish Ready → Favorites / Cooking History → Profile.

## Tech stack
- **Frontend:** HTML, CSS (custom design system), JavaScript (Jinja2 templates)
- **Backend:** Python 3 + Flask
- **Database:** SQLite (via the built-in `sqlite3` module — no ORM, so the schema
  in `database.py` is easy to read, present, and extend)

## Project structure
```
kitchen_kraft/
├── app.py              # Flask routes + ingredient-matching algorithm
├── database.py          # Schema + seed data (ingredients, recipes, nutrition)
├── requirements.txt
├── static/
│   ├── css/style.css     # Kitchen Kraft colourful design system
│   └── js/script.js
└── templates/            # Jinja2 templates (one per screen)
    ├── base.html, login.html, signup.html
    ├── home.html, my_kitchen.html, what_can_i_cook.html
    ├── recipe_details.html, dish_ready.html
    ├── favorites.html, history.html, profile.html, help.html
```

## Setup & run

```bash
cd kitchen_kraft
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

The database (`kitchen_kraft.db`) is created and seeded automatically the first
time you run the app — with 38 ingredients across 13 categories and 15 sample
recipes, each with full nutrition data. Delete the `.db` file and re-run to reset.

**Demo login:**
- Email: `demo@kitchenkraft.app`
- Password: `demo1234`

(Or click "Sign up" to create your own account.)

## How the ingredient-matching algorithm works

For every recipe, Kitchen Kraft compares the ingredients you selected in
*My Kitchen* against the recipe's required ingredient list:

```
match % = (ingredients you have ∩ ingredients required) / (ingredients required) × 100
```

Recipes are ranked by match percentage, and any missing ingredients are shown
directly on the recipe card — for example, *"80% Match — Missing: Soy Sauce."*
This is implemented in `match_recipes()` in `app.py`.

## What's implemented in this Phase-1 prototype
- User authentication (sign up / login / logout) with hashed passwords
- My Kitchen ingredient picker across 13 categories
- Ingredient-based recipe matching with meal-type and diet-type filters
- Full recipe detail pages: ingredients, step-by-step instructions, nutrition
- "Cook This Now" → Dish Ready confirmation → logged to Cooking History
- Favorites (save/unsave recipes)
- Profile page with basic settings
- Help / FAQ page

## Planned for later phases (see report, Future Scope)
- AI-based personalized recommendations, camera-based ingredient recognition,
  voice-assisted cooking, automatic grocery-list generation, and a mobile app —
  as listed in Chapter 9 of the project report.
