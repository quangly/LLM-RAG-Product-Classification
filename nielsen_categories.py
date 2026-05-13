# nielsen_categories.py
#
# This file defines the Nielsen grocery taxonomy used as the RAG knowledge base.
# In a real integration you would pull this from the Nielsen API or a licensed
# data export.  Here we define it statically so the project runs without any
# external data feed.
#
# Structure: each entry has
#   id        - stable identifier used as the primary key in SQLite
#   department - top-level Nielsen department (broadest grouping)
#   category   - mid-level category
#   subcategory- leaf-level classification (what we assign to each product)
#   text       - the full path string that gets embedded into a vector.
#                Richer text → better semantic matches, so we build the path
#                as "Department > Category > Subcategory".

NIELSEN_CATEGORIES = [
    # ── DAIRY ────────────────────────────────────────────────────────────────
    {
        "id": "dairy_fluid_milk",
        "department": "Dairy",
        "category": "Milk & Cream",
        "subcategory": "Fluid Milk",
        "text": "Dairy > Milk & Cream > Fluid Milk",
    },
    {
        "id": "dairy_cream",
        "department": "Dairy",
        "category": "Milk & Cream",
        "subcategory": "Cream & Half & Half",
        "text": "Dairy > Milk & Cream > Cream & Half & Half",
    },
    {
        "id": "dairy_butter",
        "department": "Dairy",
        "category": "Butter & Margarine",
        "subcategory": "Butter",
        "text": "Dairy > Butter & Margarine > Butter",
    },
    {
        "id": "dairy_nat_cheese",
        "department": "Dairy",
        "category": "Cheese",
        "subcategory": "Natural Cheese",
        "text": "Dairy > Cheese > Natural Cheese",
    },
    {
        "id": "dairy_proc_cheese",
        "department": "Dairy",
        "category": "Cheese",
        "subcategory": "Processed Cheese",
        "text": "Dairy > Cheese > Processed Cheese",
    },
    {
        "id": "dairy_yogurt",
        "department": "Dairy",
        "category": "Yogurt",
        "subcategory": "Refrigerated Yogurt",
        "text": "Dairy > Yogurt > Refrigerated Yogurt",
    },
    {
        "id": "dairy_eggs",
        "department": "Dairy",
        "category": "Eggs",
        "subcategory": "Shell Eggs",
        "text": "Dairy > Eggs > Shell Eggs",
    },
    {
        "id": "dairy_alt_milk",
        "department": "Dairy",
        "category": "Refrigerated Alternative Milk",
        "subcategory": "Almond, Oat & Soy Milk",
        "text": "Dairy > Refrigerated Alternative Milk > Almond, Oat & Soy Milk",
    },

    # ── MEAT ─────────────────────────────────────────────────────────────────
    {
        "id": "meat_ground_beef",
        "department": "Meat",
        "category": "Beef",
        "subcategory": "Ground Beef",
        "text": "Meat > Beef > Ground Beef",
    },
    {
        "id": "meat_beef_steak",
        "department": "Meat",
        "category": "Beef",
        "subcategory": "Beef Steak",
        "text": "Meat > Beef > Beef Steak",
    },
    {
        "id": "meat_chicken",
        "department": "Meat",
        "category": "Poultry",
        "subcategory": "Fresh Chicken",
        "text": "Meat > Poultry > Fresh Chicken",
    },
    {
        "id": "meat_turkey",
        "department": "Meat",
        "category": "Poultry",
        "subcategory": "Fresh Turkey",
        "text": "Meat > Poultry > Fresh Turkey",
    },
    {
        "id": "meat_pork",
        "department": "Meat",
        "category": "Pork",
        "subcategory": "Fresh Pork",
        "text": "Meat > Pork > Fresh Pork",
    },
    {
        "id": "meat_bacon",
        "department": "Meat",
        "category": "Pork",
        "subcategory": "Bacon",
        "text": "Meat > Pork > Bacon",
    },
    {
        "id": "meat_sausage",
        "department": "Meat",
        "category": "Processed Meats",
        "subcategory": "Sausage & Hot Dogs",
        "text": "Meat > Processed Meats > Sausage & Hot Dogs",
    },
    {
        "id": "meat_deli",
        "department": "Meat",
        "category": "Processed Meats",
        "subcategory": "Deli Meats & Cold Cuts",
        "text": "Meat > Processed Meats > Deli Meats & Cold Cuts",
    },
    {
        "id": "meat_seafood",
        "department": "Meat",
        "category": "Seafood",
        "subcategory": "Fresh Fish & Shellfish",
        "text": "Meat > Seafood > Fresh Fish & Shellfish",
    },

    # ── BAKERY ───────────────────────────────────────────────────────────────
    {
        "id": "bakery_sliced_bread",
        "department": "Bakery",
        "category": "Bread & Rolls",
        "subcategory": "Sliced Bread",
        "text": "Bakery > Bread & Rolls > Sliced Bread",
    },
    {
        "id": "bakery_rolls",
        "department": "Bakery",
        "category": "Bread & Rolls",
        "subcategory": "Dinner Rolls & Buns",
        "text": "Bakery > Bread & Rolls > Dinner Rolls & Buns",
    },
    {
        "id": "bakery_cakes",
        "department": "Bakery",
        "category": "Sweet Goods",
        "subcategory": "Cakes & Pies",
        "text": "Bakery > Sweet Goods > Cakes & Pies",
    },
    {
        "id": "bakery_muffins",
        "department": "Bakery",
        "category": "Sweet Goods",
        "subcategory": "Muffins & Donuts",
        "text": "Bakery > Sweet Goods > Muffins & Donuts",
    },
    {
        "id": "bakery_tortillas",
        "department": "Bakery",
        "category": "Tortillas & Wraps",
        "subcategory": "Flour & Corn Tortillas",
        "text": "Bakery > Tortillas & Wraps > Flour & Corn Tortillas",
    },

    # ── PRODUCE ──────────────────────────────────────────────────────────────
    {
        "id": "produce_fresh_veg",
        "department": "Produce",
        "category": "Vegetables",
        "subcategory": "Fresh Vegetables",
        "text": "Produce > Vegetables > Fresh Vegetables",
    },
    {
        "id": "produce_salad",
        "department": "Produce",
        "category": "Vegetables",
        "subcategory": "Packaged Salad & Greens",
        "text": "Produce > Vegetables > Packaged Salad & Greens",
    },
    {
        "id": "produce_fresh_fruit",
        "department": "Produce",
        "category": "Fruit",
        "subcategory": "Fresh Fruit",
        "text": "Produce > Fruit > Fresh Fruit",
    },
    {
        "id": "produce_berries",
        "department": "Produce",
        "category": "Fruit",
        "subcategory": "Fresh Berries",
        "text": "Produce > Fruit > Fresh Berries",
    },
    {
        "id": "produce_herbs",
        "department": "Produce",
        "category": "Herbs & Spices",
        "subcategory": "Fresh Herbs",
        "text": "Produce > Herbs & Spices > Fresh Herbs",
    },

    # ── CANNED & PACKAGED GOODS ───────────────────────────────────────────────
    {
        "id": "canned_vegetables",
        "department": "Canned & Packaged",
        "category": "Canned Vegetables",
        "subcategory": "Canned Tomatoes & Vegetables",
        "text": "Canned & Packaged > Canned Vegetables > Canned Tomatoes & Vegetables",
    },
    {
        "id": "canned_fruit",
        "department": "Canned & Packaged",
        "category": "Canned Fruit",
        "subcategory": "Canned Fruit & Applesauce",
        "text": "Canned & Packaged > Canned Fruit > Canned Fruit & Applesauce",
    },
    {
        "id": "canned_beans",
        "department": "Canned & Packaged",
        "category": "Canned Beans & Legumes",
        "subcategory": "Canned Beans",
        "text": "Canned & Packaged > Canned Beans & Legumes > Canned Beans",
    },
    {
        "id": "canned_soup",
        "department": "Canned & Packaged",
        "category": "Soup",
        "subcategory": "Canned & Boxed Soup",
        "text": "Canned & Packaged > Soup > Canned & Boxed Soup",
    },
    {
        "id": "canned_tuna",
        "department": "Canned & Packaged",
        "category": "Canned Seafood",
        "subcategory": "Canned Tuna & Salmon",
        "text": "Canned & Packaged > Canned Seafood > Canned Tuna & Salmon",
    },
    {
        "id": "canned_pasta",
        "department": "Canned & Packaged",
        "category": "Pasta, Rice & Grains",
        "subcategory": "Dry Pasta",
        "text": "Canned & Packaged > Pasta, Rice & Grains > Dry Pasta",
    },
    {
        "id": "canned_rice",
        "department": "Canned & Packaged",
        "category": "Pasta, Rice & Grains",
        "subcategory": "Rice & Grains",
        "text": "Canned & Packaged > Pasta, Rice & Grains > Rice & Grains",
    },

    # ── SAUCES & CONDIMENTS ───────────────────────────────────────────────────
    {
        "id": "condiments_pasta_sauce",
        "department": "Condiments & Sauces",
        "category": "Pasta Sauce",
        "subcategory": "Tomato & Marinara Sauce",
        "text": "Condiments & Sauces > Pasta Sauce > Tomato & Marinara Sauce",
    },
    {
        "id": "condiments_salsa",
        "department": "Condiments & Sauces",
        "category": "Salsa & Dips",
        "subcategory": "Salsa",
        "text": "Condiments & Sauces > Salsa & Dips > Salsa",
    },
    {
        "id": "condiments_ketchup",
        "department": "Condiments & Sauces",
        "category": "Ketchup & Mustard",
        "subcategory": "Ketchup",
        "text": "Condiments & Sauces > Ketchup & Mustard > Ketchup",
    },
    {
        "id": "condiments_mayo",
        "department": "Condiments & Sauces",
        "category": "Mayonnaise & Spreads",
        "subcategory": "Mayonnaise",
        "text": "Condiments & Sauces > Mayonnaise & Spreads > Mayonnaise",
    },
    {
        "id": "condiments_dressing",
        "department": "Condiments & Sauces",
        "category": "Salad Dressing",
        "subcategory": "Refrigerated & Shelf Stable Dressing",
        "text": "Condiments & Sauces > Salad Dressing > Refrigerated & Shelf Stable Dressing",
    },
    {
        "id": "condiments_soy",
        "department": "Condiments & Sauces",
        "category": "Asian Sauces",
        "subcategory": "Soy & Teriyaki Sauce",
        "text": "Condiments & Sauces > Asian Sauces > Soy & Teriyaki Sauce",
    },
    {
        "id": "condiments_hot_sauce",
        "department": "Condiments & Sauces",
        "category": "Hot Sauce & Peppers",
        "subcategory": "Hot Sauce",
        "text": "Condiments & Sauces > Hot Sauce & Peppers > Hot Sauce",
    },

    # ── FROZEN ────────────────────────────────────────────────────────────────
    {
        "id": "frozen_vegetables",
        "department": "Frozen",
        "category": "Frozen Vegetables",
        "subcategory": "Frozen Plain Vegetables",
        "text": "Frozen > Frozen Vegetables > Frozen Plain Vegetables",
    },
    {
        "id": "frozen_fruit",
        "department": "Frozen",
        "category": "Frozen Fruit",
        "subcategory": "Frozen Berries & Fruit",
        "text": "Frozen > Frozen Fruit > Frozen Berries & Fruit",
    },
    {
        "id": "frozen_meals",
        "department": "Frozen",
        "category": "Frozen Meals",
        "subcategory": "Single Serve Frozen Entrees",
        "text": "Frozen > Frozen Meals > Single Serve Frozen Entrees",
    },
    {
        "id": "frozen_pizza",
        "department": "Frozen",
        "category": "Frozen Pizza",
        "subcategory": "Frozen Pizza",
        "text": "Frozen > Frozen Pizza > Frozen Pizza",
    },
    {
        "id": "frozen_icecream",
        "department": "Frozen",
        "category": "Ice Cream & Novelties",
        "subcategory": "Ice Cream",
        "text": "Frozen > Ice Cream & Novelties > Ice Cream",
    },

    # ── BEVERAGES ────────────────────────────────────────────────────────────
    {
        "id": "bev_water",
        "department": "Beverages",
        "category": "Water",
        "subcategory": "Bottled Water & Sparkling Water",
        "text": "Beverages > Water > Bottled Water & Sparkling Water",
    },
    {
        "id": "bev_juice",
        "department": "Beverages",
        "category": "Juice",
        "subcategory": "Refrigerated Juice",
        "text": "Beverages > Juice > Refrigerated Juice",
    },
    {
        "id": "bev_soda",
        "department": "Beverages",
        "category": "Carbonated Soft Drinks",
        "subcategory": "Regular & Diet Soda",
        "text": "Beverages > Carbonated Soft Drinks > Regular & Diet Soda",
    },
    {
        "id": "bev_coffee",
        "department": "Beverages",
        "category": "Coffee",
        "subcategory": "Ground & Whole Bean Coffee",
        "text": "Beverages > Coffee > Ground & Whole Bean Coffee",
    },
    {
        "id": "bev_tea",
        "department": "Beverages",
        "category": "Tea",
        "subcategory": "Bagged & Loose Leaf Tea",
        "text": "Beverages > Tea > Bagged & Loose Leaf Tea",
    },

    # ── SNACKS ────────────────────────────────────────────────────────────────
    {
        "id": "snacks_chips",
        "department": "Snacks",
        "category": "Salty Snacks",
        "subcategory": "Potato Chips & Crisps",
        "text": "Snacks > Salty Snacks > Potato Chips & Crisps",
    },
    {
        "id": "snacks_crackers",
        "department": "Snacks",
        "category": "Crackers",
        "subcategory": "Crackers & Crispbreads",
        "text": "Snacks > Crackers > Crackers & Crispbreads",
    },
    {
        "id": "snacks_cookies",
        "department": "Snacks",
        "category": "Cookies",
        "subcategory": "Cookies & Snack Cakes",
        "text": "Snacks > Cookies > Cookies & Snack Cakes",
    },
    {
        "id": "snacks_nuts",
        "department": "Snacks",
        "category": "Nuts & Seeds",
        "subcategory": "Mixed & Flavored Nuts",
        "text": "Snacks > Nuts & Seeds > Mixed & Flavored Nuts",
    },

    # ── BREAKFAST & CEREAL ────────────────────────────────────────────────────
    {
        "id": "breakfast_cereal",
        "department": "Breakfast & Cereal",
        "category": "Cereal",
        "subcategory": "Cold Cereal",
        "text": "Breakfast & Cereal > Cereal > Cold Cereal",
    },
    {
        "id": "breakfast_oatmeal",
        "department": "Breakfast & Cereal",
        "category": "Hot Cereal",
        "subcategory": "Oatmeal & Porridge",
        "text": "Breakfast & Cereal > Hot Cereal > Oatmeal & Porridge",
    },
    {
        "id": "breakfast_pancake",
        "department": "Breakfast & Cereal",
        "category": "Pancake & Waffle",
        "subcategory": "Pancake Mix & Syrup",
        "text": "Breakfast & Cereal > Pancake & Waffle > Pancake Mix & Syrup",
    },
]
