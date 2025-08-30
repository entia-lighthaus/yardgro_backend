# YardGro Backend API
This project is a Django RESTful backend for the YardGro marketplace, supporting user authentication, product management, categories, GroRoulette spins (budget gamification system with greedy algorithm), baskets, and orders.

# Table of Contents
1. Authentication
2. Categories
3. Products
4. GroRoulette™
5. Basket & Orders
6. User Journey Example

===========================================================================================

# 1. Authentication
The authentication endpoints allow different user types: buyers (company or household), farmers, and recyclers to register and log in. During registration, users specify their role and provide relevant details (such as company name, address, or location).
This flexible registration system ensures each user type can access features tailored to their needs.

Endpoints:

POST /api/users/register/ — Register a new user.
POST /api/users/login/ — Login and obtain a token.

Request Example
# 1.1 Register: As a Buyer(Company/Business)
    {  
  "username": "ThePlace_Restaurant",
  "email": "dplace@gmail.com",
  "password": "testtest1234",
  "role": "buyer",
  "buyer_type": "company",
  "company_name": "The Place Restaurant",
  "address": "oba oyekan estate"
    }

Response Example:

    {
  "id": 1,
  "username": "user1",
  "email": "dplace@gmail.com",
  "token": "..."
    }


# 1.2. Register: As a Buyer(Individual/Household)
    {  
    "username": "MayIheuwa",
    "email": "mihe@gmail.com",
    "password": "testtest1234",
    "role": "buyer",
    "buyer_type": "household",
    "address": "oba oyekan estate"
    }

# 1.3. Register: As a Farmer
    {  
    "username": "greenfarms",
    "email": "gf@gmail.com",
    "password": "testtest1234",
    "role": "farmer",
    "location": "Ibrahim Estate, Sokoto",
    "company_name": "Green Farms Sokoto"
    }

# 1.4. Register: As a Recycler
    {  
    "username": "Wecyclers",
    "email": "wc@gmail.com",
    "password": "testtest1234",
    "role": "recycler",
    "location": "Isheri, Lagos",
    "company_name": "Wecyclers NG"
    }

===================================================================================

# 2. Categories
The category endpoints allow users (admin and farmers only) to manage product categories in the marketplace. Users can list all categories, create new ones, or delete existing categories by ID. Buyers can peruse through all the categories and their nested products, linked by a one-to-many relationship.

Endpoints:

GET /api/marketplace/categories/ — List all categories.
POST /api/marketplace/categories/ — Create a new category.
DELETE /api/marketplace/categories/<id>/ - Delete a category by its ID.

In Postman, a body request test example can be (Create):
{
  "name": "Vegetables",
  "description": "Fresh and organic vegetables"
}
==================================================================================

# 3. Products
Endpoints:

GET /api/marketplace/products/ — List all products.
POST /api/marketplace/products/ — Add a new product.
POST /api/marketplace/products/<product_id>/favorite/ — Add product to favorites.
DELETE /api/marketplace/products/<product_id>/ - Delete a product
POST /api/marketplace/products/rate/ — Rate a product.

Request Example (Rate):
{
  "product": 123,
  "rating": 5,
  "review": "Great product, I will buy again!"
}
=================================================================================

# 4. GroRoulette™
GroRoulette™ is a gamified budgeting tool that lets buyer users spin for a list of products based on their preferences, purchase histories, and budget. When the roulette generates items in a spin, users can increase or reduce the quantities of products generated. By reducing a product quantity, it allows the budget to accomodate a wider range of products drastically, with a greedy algorithm. Additionally, users can either select some items they prefer to add to their basket, whle ignoring the rest. If they want all the items on the spin list, they can add all spin items to the basket instead.

Endpoints:

POST /api/groroulette/spins/ — Generate a new spin.
GET /api/groroulette/spins/ — List all spins.
GET /api/groroulette/spins/<spin_id>/ — Get details of a specific spin.
PATCH /api/groroulette/spin/items/<item_id>/ — Update quantity or selection of a spin item.
POST /api/groroulette/spins/<spin_id>/add-to-basket/ — Add selected spin items to basket.
POST /api/groroulette/spins/<spin_id>/add-all-to-basket/ — Add all spin items to basket.



# 4.2. GroRoulette User Preferences
When generating a GroRoulette spin, users can specify their preferences to personalize the product recommendations. Preferences may include dietary restrictions, allergies, preferred product categories, excluded brands, and a maximum budget. These preferences help the GroRoulette algorithm select items that best fit the user's needs and constraints, ensuring a more relevant and satisfying shopping experience.

The endpoint for updating GroRoulette user preferences is:
PATCH /api/groroulette/preferences/

Request Body Example (Update Preferences):
{
  "dietary_restrictions": ["vegetarian", "gluten_free"],
  "allergies": ["nuts"],
  "preferred_categories": [1, 2, 10],
  "excluded_brands": ["BrandA"],
  "max_budget_default": 68000
}

By setting these preferences, users can tailor their spins to match their lifestyle, health requirements, and shopping goals.
=================================================================================

# 5. Basket & Orders

# 5.1. Basket Endpoints:
The Basket acts as a temporary cart where users can add products or GroRoulette spin items before finalizing their purchase. Users can review, update, or remove items in their basket. When ready, users checkout the basket, which creates a permanent Order containing all basket items.

GET /api/orders/baskets/ — View user's basket.
POST /api/orders/baskets/<basket_id>/checkout/ — Checkout basket and create an order.

# 5.2. Order Endpoints:

GET /api/orders/ — List all orders.
GET /api/orders/<order_id>/ — View order details.

This flow ensures users can manage their selections before committing to a purchase, supporting both direct marketplace shopping and GroRoulette spins.
======================================================================================

# USER JOURNEY EXAMPLE
Register & Login
- Register via /api/users/register/
- Login via /api/users/login/ to get your token.
- Create a Category: POST to /api/marketplace/categories/ with category details.
- Add a Product: POST to /api/marketplace/products/ with product details.
- Spin GroRoulette: POST to /api/groroulette/spins/ with your budget and preferences.
- Select Spin Items: PATCH /api/groroulette/spin/items/<item_id>/ with:
- Add Spin Items to Basket: POST /api/groroulette/spins/<spin_id>/add-to-basket/ (selected items)
or
POST /api/groroulette/spins/<spin_id>/add-all-to-basket/ (all items)

- Checkout Basket: POST /api/orders/baskets/<basket_id>/checkout/

Notes
All endpoints require authentication.

