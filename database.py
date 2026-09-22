"""
Kitchen Kraft - Database layer
--------------------------------
Uses plain sqlite3 (no ORM) so the schema is easy to read and to defend
in a viva. All tables described in the project synopsis are created here,
and a small but representative set of ingredients / recipes is seeded so
the app is demonstrable out of the box.
"""

import sqlite3
import json
import os
from datetime import date
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "kitchen_kraft.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    food_preference TEXT DEFAULT 'Veg'
);

CREATE TABLE IF NOT EXISTS ingredients (
    ingredient_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT UNIQUE NOT NULL,
    category        TEXT NOT NULL,
    emoji           TEXT DEFAULT '🥘'
);

CREATE TABLE IF NOT EXISTS recipes (
    recipe_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name   TEXT NOT NULL,
    category      TEXT,
    meal_type     TEXT,
    food_type     TEXT,           -- Veg / Non-Veg / Egg / Seafood
    cooking_time  INTEGER,        -- minutes
    difficulty    TEXT,
    servings      INTEGER,
    description   TEXT,
    instructions  TEXT,           -- JSON list of steps
    tags          TEXT            -- comma separated
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id     INTEGER NOT NULL REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(ingredient_id) ON DELETE CASCADE,
    quantity      TEXT,
    PRIMARY KEY (recipe_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS nutrition (
    recipe_id     INTEGER PRIMARY KEY REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    calories      REAL,
    protein       REAL,
    carbohydrates REAL,
    fat           REAL,
    fibre         REAL,
    sugar         REAL,
    sodium        REAL
);

CREATE TABLE IF NOT EXISTS user_kitchen (
    user_id       INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(ingredient_id) ON DELETE CASCADE,
    quantity      TEXT DEFAULT '1',
    PRIMARY KEY (user_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS favorites (
    user_id   INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    recipe_id INTEGER NOT NULL REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, recipe_id)
);

CREATE TABLE IF NOT EXISTS cooking_history (
    history_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    recipe_id   INTEGER NOT NULL REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    cooked_date TEXT,
    rating      INTEGER
);
"""

# --------------------------------------------------------------------------
# Seed data
# --------------------------------------------------------------------------

INGREDIENTS = [
    # name, category, emoji
    ("Rice", "Grains & Staples", "🍚"), ("Onion", "Vegetables", "🧅"),
    ("Tomato", "Vegetables", "🍅"), ("Potato", "Vegetables", "🥔"),
    ("Egg", "Non-Veg", "🥚"), ("Milk", "Dairy", "🥛"),
    ("Green Chilli", "Vegetables", "🌶️"), ("Turmeric Powder", "Spices & Herbs", "🟡"),
    ("Oil", "Oils & Sauces", "🛢️"), ("Salt", "Spices & Herbs", "🧂"),
    ("Coriander Leaves", "Spices & Herbs", "🌿"), ("Garlic", "Vegetables", "🧄"),
    ("Ginger", "Vegetables", "🫚"), ("Carrot", "Vegetables", "🥕"),
    ("Beans", "Vegetables", "🫛"), ("Peas", "Vegetables", "🟢"),
    ("Paneer", "Dairy", "🧀"), ("Curd", "Dairy", "🥣"),
    ("Ragi Flour", "Ragi & Millets", "🌾"), ("Rava", "Rava & Flour", "🌾"),
    ("Wheat Flour", "Rava & Flour", "🌾"), ("Toor Dal", "Pulses & Legumes", "🫘"),
    ("Moong Dal", "Pulses & Legumes", "🫘"), ("Soy Sauce", "Oils & Sauces", "🫙"),
    ("Chicken", "Non-Veg", "🍗"), ("Fish", "Seafood", "🐟"),
    ("Cumin Seeds", "Spices & Herbs", "🟤"), ("Mustard Seeds", "Spices & Herbs", "⚫"),
    ("Sugar", "Grains & Staples", "🍬"), ("Banana", "Fruits", "🍌"),
    ("Lemon", "Fruits", "🍋"), ("Cardamom", "Spices & Herbs", "🌱"),
    ("Nuts (Mixed)", "Nuts & Seeds", "🥜"), ("Honey", "Oils & Sauces", "🍯"),
    ("Capsicum", "Vegetables", "🫑"), ("Spinach", "Vegetables", "🥬"),
    ("Butter", "Dairy", "🧈"), ("Cheese", "Dairy", "🧀"),
    ("Bread", "Bakery & Others", "🍞"),
]

# Each recipe: name, category, meal_type, food_type, time, difficulty, servings,
# description, steps(list), tags(list), ingredients {name: qty}, nutrition dict
RECIPES = [
    dict(
        name="Tomato Rice", category="Rice", meal_type="Lunch", food_type="Veg",
        time=25, difficulty="Easy", servings=3,
        description="A simple and comforting dish made with fresh tomatoes and aromatic spices. "
                     "Perfect for a quick lunch or dinner!",
        steps=[
            "Wash the rice and cook it with 1.5 cups of water. Keep it aside.",
            "Heat oil in a pan. Add chopped onions and saute until light golden.",
            "Add green chillies and chopped tomatoes. Cook until the tomatoes turn soft and mushy.",
            "Add turmeric powder, salt and mix well.",
            "Add the cooked rice and gently mix so everything is combined.",
            "Cook for 2-3 minutes on low flame.",
            "Garnish with coriander leaves and serve hot.",
        ],
        tags=["Simple", "Quick", "Tasty"],
        ingredients={"Rice": "1 cup", "Tomato": "3 medium", "Onion": "1 medium",
                     "Green Chilli": "2", "Turmeric Powder": "1/2 tsp", "Oil": "2 tbsp",
                     "Salt": "to taste", "Coriander Leaves": "few"},
        nutrition=dict(calories=280, protein=6, carbohydrates=45, fat=8, fibre=4, sugar=5, sodium=320),
    ),
    dict(
        name="Onion Rice", category="Rice", meal_type="Lunch", food_type="Veg",
        time=20, difficulty="Easy", servings=3,
        description="Fragrant rice tossed with caramelised onions and whole spices.",
        steps=[
            "Cook rice and spread it out to cool so the grains stay separate.",
            "Heat oil, add mustard seeds and let them splutter.",
            "Add sliced onions and fry until deep golden brown.",
            "Add turmeric powder and salt, then add the cooked rice.",
            "Toss gently on low flame for 2-3 minutes.",
            "Garnish with coriander leaves and serve.",
        ],
        tags=["Quick", "Easy", "Comfort Food"],
        ingredients={"Rice": "1 cup", "Onion": "2 large", "Mustard Seeds": "1/2 tsp",
                     "Turmeric Powder": "1/4 tsp", "Oil": "2 tbsp", "Salt": "to taste",
                     "Coriander Leaves": "few"},
        nutrition=dict(calories=260, protein=4, carbohydrates=48, fat=7, fibre=3, sugar=4, sodium=290),
    ),
    dict(
        name="Potato Curry", category="Curry", meal_type="Lunch", food_type="Veg",
        time=30, difficulty="Easy", servings=4,
        description="A homely, spiced potato curry that pairs well with rice or chapati.",
        steps=[
            "Boil the potatoes until soft, then peel and cube them.",
            "Heat oil and add cumin seeds until they splutter.",
            "Add chopped onions and saute until translucent.",
            "Add tomatoes, turmeric powder and salt; cook until soft.",
            "Add the boiled potatoes and a little water; simmer for 8-10 minutes.",
            "Garnish with coriander leaves and serve hot.",
        ],
        tags=["Healthy", "Wholesome"],
        ingredients={"Potato": "4 medium", "Onion": "1 medium", "Tomato": "2 medium",
                     "Cumin Seeds": "1/2 tsp", "Turmeric Powder": "1/2 tsp", "Oil": "2 tbsp",
                     "Salt": "to taste", "Coriander Leaves": "few"},
        nutrition=dict(calories=310, protein=5, carbohydrates=52, fat=9, fibre=5, sugar=6, sodium=340),
    ),
    dict(
        name="Egg Fried Rice", category="Rice", meal_type="Dinner", food_type="Non-Veg",
        time=25, difficulty="Easy", servings=2,
        description="Wok-tossed rice with scrambled egg and a dash of soy sauce.",
        steps=[
            "Cook rice ahead of time and let it cool (day-old rice works best).",
            "Beat eggs and scramble them in a hot pan; set aside.",
            "In the same pan, saute onions and carrots until slightly softened.",
            "Add the rice, soy sauce and scrambled egg; toss on high flame.",
            "Season with salt and pepper and serve immediately.",
        ],
        tags=["Quick", "Filling"],
        ingredients={"Rice": "1.5 cups", "Egg": "2", "Onion": "1 medium", "Carrot": "1 small",
                     "Soy Sauce": "1 tbsp", "Oil": "2 tbsp", "Salt": "to taste"},
        nutrition=dict(calories=340, protein=12, carbohydrates=46, fat=11, fibre=3, sugar=3, sodium=480),
    ),
    dict(
        name="Vegetable Pulao", category="Rice", meal_type="Lunch", food_type="Veg",
        time=35, difficulty="Medium", servings=4,
        description="Aromatic one-pot rice cooked with mixed vegetables and whole spices.",
        steps=[
            "Heat oil/ghee and add cumin seeds and whole spices.",
            "Add chopped onions and saute until golden.",
            "Add chopped carrots, beans and peas; saute for 2-3 minutes.",
            "Add washed rice, salt and water; bring to a boil.",
            "Cover and cook on low flame until the rice is done.",
            "Fluff gently and garnish with coriander leaves.",
        ],
        tags=["Aromatic", "Healthy", "Easy"],
        ingredients={"Rice": "1 cup", "Carrot": "1", "Beans": "handful", "Peas": "1/2 cup",
                     "Onion": "1 medium", "Cumin Seeds": "1 tsp", "Oil": "2 tbsp", "Salt": "to taste"},
        nutrition=dict(calories=300, protein=7, carbohydrates=50, fat=8, fibre=6, sugar=4, sodium=310),
    ),
    dict(
        name="Tomato Egg Curry", category="Curry", meal_type="Dinner", food_type="Non-Veg",
        time=30, difficulty="Medium", servings=3,
        description="Boiled eggs simmered in a rich, spiced tomato-onion gravy.",
        steps=[
            "Boil the eggs, peel and lightly score them.",
            "Heat oil and saute onions until golden brown.",
            "Add ginger-garlic paste and cook until raw smell disappears.",
            "Add tomatoes and spices; cook until oil separates.",
            "Add water to form a gravy and simmer for 5 minutes.",
            "Add the boiled eggs, simmer for 3-4 minutes, and serve hot.",
        ],
        tags=["Rich", "Flavourful"],
        ingredients={"Egg": "4", "Onion": "2 medium", "Tomato": "3 medium", "Garlic": "4 cloves",
                     "Ginger": "1 inch", "Turmeric Powder": "1/2 tsp", "Oil": "2 tbsp", "Salt": "to taste"},
        nutrition=dict(calories=290, protein=14, carbohydrates=18, fat=17, fibre=3, sugar=6, sodium=360),
    ),
    dict(
        name="Rice Kheer", category="Dessert", meal_type="Dessert", food_type="Veg",
        time=40, difficulty="Medium", servings=4,
        description="A creamy, slow-cooked rice pudding flavoured with cardamom and nuts.",
        steps=[
            "Wash and soak rice for 15 minutes, then drain.",
            "Boil milk in a heavy-bottomed pan; add the rice.",
            "Simmer on low flame, stirring often, until the rice is soft and the milk thickens.",
            "Add sugar and cardamom powder; cook for 5 more minutes.",
            "Garnish with chopped nuts and serve warm or chilled.",
        ],
        tags=["Creamy", "Dessert"],
        ingredients={"Rice": "1/4 cup", "Milk": "1 litre", "Sugar": "1/2 cup",
                     "Cardamom": "2 pods", "Nuts (Mixed)": "2 tbsp"},
        nutrition=dict(calories=250, protein=7, carbohydrates=38, fat=8, fibre=1, sugar=28, sodium=90),
    ),
    dict(
        name="Tomato Omelette", category="Breakfast", meal_type="Breakfast", food_type="Non-Veg",
        time=15, difficulty="Easy", servings=1,
        description="A quick, protein-rich omelette studded with tomato and onion.",
        steps=[
            "Beat eggs with salt and a pinch of turmeric.",
            "Add finely chopped onion, tomato and green chilli to the egg mixture.",
            "Heat oil in a pan and pour the mixture in.",
            "Cook on medium flame until golden on both sides.",
            "Serve hot with toast.",
        ],
        tags=["Quick", "Protein Rich"],
        ingredients={"Egg": "2", "Tomato": "1 small", "Onion": "1 small",
                     "Green Chilli": "1", "Oil": "1 tbsp", "Salt": "to taste"},
        nutrition=dict(calories=210, protein=13, carbohydrates=5, fat=15, fibre=1, sugar=2, sodium=310),
    ),
    dict(
        name="Ragi Dosa", category="Breakfast", meal_type="Breakfast", food_type="Veg",
        time=20, difficulty="Easy", servings=2,
        description="A quick, instant millet crepe that's naturally high in fibre and calcium.",
        steps=[
            "Mix ragi flour, rice flour (or rava), curd and water into a thin batter.",
            "Add chopped onions, green chilli and salt; rest for 10 minutes.",
            "Heat a tawa and pour a ladle of batter, spreading thin.",
            "Drizzle oil around the edges and cook until crisp.",
            "Flip briefly, then serve hot with chutney.",
        ],
        tags=["Healthy", "Millet", "Fibre Rich"],
        ingredients={"Ragi Flour": "1 cup", "Rava": "1/4 cup", "Curd": "1/2 cup",
                     "Onion": "1 small", "Green Chilli": "1", "Oil": "2 tbsp", "Salt": "to taste"},
        nutrition=dict(calories=220, protein=6, carbohydrates=34, fat=6, fibre=7, sugar=2, sodium=260),
    ),
    dict(
        name="Paneer Curry", category="Curry", meal_type="Lunch", food_type="Veg",
        time=30, difficulty="Medium", servings=3,
        description="Soft paneer cubes simmered in a rich, spiced tomato-onion gravy.",
        steps=[
            "Cube the paneer; lightly pan-fry until golden (optional).",
            "Saute onions until golden, then add ginger-garlic paste.",
            "Add tomato puree and spices; cook until oil separates.",
            "Add water/cream to form a gravy and simmer for 5 minutes.",
            "Add paneer cubes, simmer for 2-3 minutes and serve hot.",
        ],
        tags=["Rich", "Spicy", "Comfort Food"],
        ingredients={"Paneer": "200 g", "Onion": "2 medium", "Tomato": "3 medium",
                     "Garlic": "4 cloves", "Ginger": "1 inch", "Butter": "1 tbsp",
                     "Turmeric Powder": "1/2 tsp", "Oil": "1 tbsp", "Salt": "to taste"},
        nutrition=dict(calories=360, protein=15, carbohydrates=14, fat=27, fibre=3, sugar=6, sodium=380),
    ),
    dict(
        name="Fruit Smoothie", category="Juices", meal_type="Breakfast", food_type="Veg",
        time=10, difficulty="Easy", servings=1,
        description="A creamy, energising blend of banana and milk — ready in minutes.",
        steps=[
            "Peel and roughly chop the banana.",
            "Add banana, milk and honey to a blender.",
            "Blend until smooth and frothy.",
            "Pour into a glass and serve immediately.",
        ],
        tags=["Quick", "Energising"],
        ingredients={"Banana": "1 large", "Milk": "1 cup", "Honey": "1 tbsp"},
        nutrition=dict(calories=180, protein=6, carbohydrates=32, fat=3, fibre=2, sugar=24, sodium=60),
    ),
    dict(
        name="Vegetable Sandwich", category="Snack", meal_type="Snack", food_type="Veg",
        time=15, difficulty="Easy", servings=2,
        description="A simple, filling sandwich layered with fresh vegetables and cheese.",
        steps=[
            "Wash and thinly slice the tomato, onion and capsicum.",
            "Butter the bread slices lightly.",
            "Layer the vegetables and a slice of cheese between two slices.",
            "Toast on a pan or in a sandwich maker until golden.",
            "Cut diagonally and serve warm.",
        ],
        tags=["Quick", "Filling"],
        ingredients={"Bread": "4 slices", "Tomato": "1", "Onion": "1", "Capsicum": "1",
                     "Cheese": "2 slices", "Butter": "1 tbsp", "Salt": "to taste"},
        nutrition=dict(calories=260, protein=9, carbohydrates=30, fat=11, fibre=3, sugar=4, sodium=420),
    ),
    dict(
        name="Dal Tadka", category="Curry", meal_type="Lunch", food_type="Veg",
        time=30, difficulty="Easy", servings=4,
        description="Comforting yellow lentils tempered with cumin, garlic and dried chillies.",
        steps=[
            "Wash and pressure-cook toor dal with turmeric until soft.",
            "Mash the cooked dal lightly and set aside.",
            "In a small pan, heat oil and splutter cumin and mustard seeds.",
            "Add garlic and dried chilli; saute until golden and fragrant.",
            "Pour the tempering over the dal, add salt, and simmer for 2-3 minutes.",
            "Garnish with coriander leaves and serve with rice or roti.",
        ],
        tags=["Protein Rich", "Comfort Food"],
        ingredients={"Toor Dal": "1 cup", "Garlic": "4 cloves", "Cumin Seeds": "1/2 tsp",
                     "Mustard Seeds": "1/2 tsp", "Turmeric Powder": "1/2 tsp", "Oil": "1 tbsp",
                     "Salt": "to taste", "Coriander Leaves": "few"},
        nutrition=dict(calories=230, protein=12, carbohydrates=34, fat=5, fibre=8, sugar=2, sodium=300),
    ),
    dict(
        name="Fish Curry", category="Curry", meal_type="Dinner", food_type="Seafood",
        time=35, difficulty="Medium", servings=3,
        description="Fish simmered in a tangy, spiced coconut-tomato gravy.",
        steps=[
            "Clean and marinate the fish pieces with turmeric and salt.",
            "Heat oil and saute onions until golden.",
            "Add tomatoes, ginger-garlic paste and spices; cook until soft.",
            "Add water to form a gravy and bring to a gentle boil.",
            "Slide in the fish pieces and simmer for 8-10 minutes without stirring too much.",
            "Garnish with coriander leaves and serve hot with rice.",
        ],
        tags=["Spicy", "Coastal"],
        ingredients={"Fish": "500 g", "Onion": "2 medium", "Tomato": "2 medium",
                     "Garlic": "4 cloves", "Ginger": "1 inch", "Turmeric Powder": "1/2 tsp",
                     "Oil": "2 tbsp", "Salt": "to taste", "Coriander Leaves": "few"},
        nutrition=dict(calories=280, protein=26, carbohydrates=8, fat=16, fibre=2, sugar=3, sodium=410),
    ),
    dict(
        name="Spinach Paneer (Palak Paneer)", category="Curry", meal_type="Lunch", food_type="Veg",
        time=30, difficulty="Medium", servings=3,
        description="A nutritious, iron-rich curry of pureed spinach and soft paneer cubes.",
        steps=[
            "Blanch spinach leaves and blend to a smooth puree.",
            "Saute onions, garlic and ginger until fragrant.",
            "Add tomato and spices; cook briefly, then add the spinach puree.",
            "Simmer for 5 minutes, then add paneer cubes.",
            "Finish with a swirl of butter or cream and serve hot.",
        ],
        tags=["Healthy", "Iron Rich"],
        ingredients={"Spinach": "2 cups", "Paneer": "150 g", "Onion": "1 medium",
                     "Tomato": "1 medium", "Garlic": "3 cloves", "Butter": "1 tbsp", "Salt": "to taste"},
        nutrition=dict(calories=300, protein=14, carbohydrates=12, fat=22, fibre=4, sugar=4, sodium=340),
    ),
]


def init_db(seed=True):
    """Create tables and, on first run, seed reference data."""
    conn = get_db()
    conn.executescript(SCHEMA)
    conn.commit()

    if seed:
        cur = conn.execute("SELECT COUNT(*) AS c FROM ingredients")
        if cur.fetchone()["c"] == 0:
            _seed(conn)
    conn.close()


def _seed(conn):
    for name, category, emoji in INGREDIENTS:
        conn.execute(
            "INSERT OR IGNORE INTO ingredients (ingredient_name, category, emoji) VALUES (?,?,?)",
            (name, category, emoji),
        )
    conn.commit()

    name_to_id = {
        row["ingredient_name"]: row["ingredient_id"]
        for row in conn.execute("SELECT ingredient_id, ingredient_name FROM ingredients")
    }

    for r in RECIPES:
        cur = conn.execute(
            """INSERT INTO recipes
               (recipe_name, category, meal_type, food_type, cooking_time,
                difficulty, servings, description, instructions, tags)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (r["name"], r["category"], r["meal_type"], r["food_type"], r["time"],
             r["difficulty"], r["servings"], r["description"],
             json.dumps(r["steps"]), ",".join(r["tags"])),
        )
        recipe_id = cur.lastrowid

        for ing_name, qty in r["ingredients"].items():
            ing_id = name_to_id.get(ing_name)
            if ing_id is None:
                continue
            conn.execute(
                "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (?,?,?)",
                (recipe_id, ing_id, qty),
            )

        n = r["nutrition"]
        conn.execute(
            """INSERT INTO nutrition
               (recipe_id, calories, protein, carbohydrates, fat, fibre, sugar, sodium)
               VALUES (?,?,?,?,?,?,?,?)""",
            (recipe_id, n["calories"], n["protein"], n["carbohydrates"],
             n["fat"], n["fibre"], n["sugar"], n["sodium"]),
        )
    conn.commit()

    # A ready-to-use demo account: demo@kitchenkraft.app / demo1234
    conn.execute(
        "INSERT OR IGNORE INTO users (name, email, password_hash, food_preference) VALUES (?,?,?,?)",
        ("Demo Chef", "demo@kitchenkraft.app", generate_password_hash("demo1234"), "Veg"),
    )
    conn.commit()

    demo_id = conn.execute("SELECT user_id FROM users WHERE email='demo@kitchenkraft.app'").fetchone()["user_id"]
    for ing_name in ["Rice", "Onion", "Tomato", "Potato", "Egg", "Milk"]:
        ing_id = name_to_id.get(ing_name)
        if ing_id:
            conn.execute(
                "INSERT OR IGNORE INTO user_kitchen (user_id, ingredient_id, quantity) VALUES (?,?,1)",
                (demo_id, ing_id),
            )
    tomato_rice_id = conn.execute("SELECT recipe_id FROM recipes WHERE recipe_name='Tomato Rice'").fetchone()["recipe_id"]
    conn.execute(
        "INSERT OR IGNORE INTO cooking_history (user_id, recipe_id, cooked_date, rating) VALUES (?,?,?,5)",
        (demo_id, tomato_rice_id, str(date.today())),
    )
    conn.commit()


if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    print(f"Database created and seeded at {DB_PATH}")
