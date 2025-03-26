from flask import Flask, render_template, request
import os
import pandas as pd
import re

app = Flask(__name__)

# Load the CSV file
df = pd.read_csv('dataset/Food Ingredients and Recipe Dataset with Image Name Mapping.csv')

# Path to the folder containing images
image_folder = os.path.abspath('static/Food Images')

# Function to clean the ingredients by removing quantities and measurements
def clean_ingredient_list(ingredient_list_str):
    pattern = r'(\d+[\d\/\.\,\-\–]*|\b(?:tsp|tbsp|cup|cups|oz|lb|kg|g|ml|l|quart|pinch|dash|clove|slice|pieces?|sprigs?|leaves?|bunch|handful|dozen)\b)'
    ingredients = eval(ingredient_list_str)
    cleaned_ingredients = [re.sub(pattern, '', ingredient).strip() for ingredient in ingredients]
    return ', '.join(cleaned_ingredients)

# Apply the cleaning function to the 'Ingredients' column to create a new 'Cleaned_Ingredients' column
df['Cleaned_Ingredients'] = df['Ingredients'].apply(clean_ingredient_list)

# Home page route to search recipes by ingredients
@app.route('/', methods=['GET', 'POST'])
def index():
    recipes = None
    instructions = None
    image_url = None
    
    if request.method == 'POST':
        ingredients_input = request.form.get('ingredients')
        ingredients_list = [ingredient.lower().strip() for ingredient in ingredients_input.split(',')]
        
        # Filter matching recipes based on ingredients
        def ingredients_match(recipe_ingredients, input_ingredients):
            recipe_ingredients = [ingredient.lower().strip() for ingredient in recipe_ingredients.split(',')]
            return all(ingredient in recipe_ingredients for ingredient in input_ingredients)

        matching_recipes = df[df['Cleaned_Ingredients'].apply(ingredients_match, args=(ingredients_list,))]

        if not matching_recipes.empty:
            recipes = matching_recipes['Title'].tolist()  # Get matching recipe titles
        else:
            recipes = []

    return render_template('index.html', recipes=recipes, instructions=instructions, image_url=image_url)

# Route to get the instructions and image for the selected recipe
@app.route('/get_instructions', methods=['POST'])
def get_instructions():
    recipe_title = request.form.get('recipe_title')
    selected_recipe = df[df['Title'].str.lower() == recipe_title.lower()]

    if not selected_recipe.empty:
        instructions = selected_recipe.iloc[0]['Instructions']
        image_name = selected_recipe.iloc[0]['Image_Name']
        image_path = os.path.join(image_folder, image_name)

        if os.path.exists(image_path):
            image_url = f"/static/Food Images/{image_name}"
            return render_template('index.html', recipe_title=recipe_title, instructions=instructions, image_url=image_url)
        else:
            return render_template('index.html', recipe_title=recipe_title, instructions=instructions, image_url=None)
    else:
        return render_template('index.html', recipe_title=recipe_title, instructions="No instructions found.", image_url=None)

if __name__ == '__main__':
    app.run(debug=True)
