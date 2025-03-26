import pandas as pd
import os
from PIL import Image
import re
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Load the CSV file
df = pd.read_csv('dataset\Food Ingredients and Recipe Dataset with Image Name Mapping.csv')

# Path to the folder containing images
image_folder = os.path.abspath('static\Food Images')  # Use absolute path for consistency

# Function to clean the ingredients by removing quantities and measurements
def clean_ingredient_list(ingredient_list_str):
    pattern = r'(\d+[\d\/\.\,\-\–]*|\b(?:tsp|tbsp|cup|cups|oz|lb|kg|g|ml|l|quart|pinch|dash|clove|slice|pieces?|sprigs?|leaves?|bunch|handful|dozen)\b)'
    ingredients = eval(ingredient_list_str)
    cleaned_ingredients = []
    
    for ingredient in ingredients:
        cleaned_ingredient = re.sub(pattern, '', ingredient).strip()
        cleaned_ingredients.append(cleaned_ingredient)
    
    return ', '.join(cleaned_ingredients)

# Apply the cleaning function to the 'Ingredients' column to create a new 'Cleaned_Ingredients' column
df['Cleaned_Ingredients'] = df['Ingredients'].apply(clean_ingredient_list)

# Clean image names in the DataFrame
df['Image_Name'] = df['Image_Name'].str.strip()  # Remove any leading/trailing spaces

# Function to find matching recipes based on input ingredients
def find_matching_recipes(ingredients_input):
    ingredients_input = [ingredient.lower().strip() for ingredient in ingredients_input]

    def ingredients_match(recipe_ingredients, input_ingredients):
        recipe_ingredients = [ingredient.lower().strip() for ingredient in recipe_ingredients.split(',')]
        return all(ingredient in recipe_ingredients for ingredient in input_ingredients)

    matching_recipes = df[df['Cleaned_Ingredients'].apply(ingredients_match, args=(ingredients_input,))]

    if not matching_recipes.empty:
        print("\nMatching Recipes:")
        for index, row in matching_recipes.iterrows():
            print(f"- {row['Title']}")  # Display only titles
            
        selected_title = input("\nEnter the title of the recipe to see the instructions: ")
        
        selected_recipe = matching_recipes[matching_recipes['Title'].str.lower() == selected_title.lower()]

        if not selected_recipe.empty:
            # Select the first matching recipe
            row = selected_recipe.iloc[0]
            print(f"\nInstructions for '{row['Title']}':")
            print(row['Instructions'])  # Display instructions once

            # Get the image name and path for the selected recipe
            image_name = row['Image_Name']
            image_path = os.path.join(image_folder, image_name)

            # Append extensions if missing
            if not os.path.splitext(image_name)[1]:
                for ext in ['.jpg', '.png', '.jpeg']:
                    potential_image_path = image_path + ext
                    if os.path.exists(potential_image_path):
                        image_path = potential_image_path
                        break
                
            print(f"Looking for image: {image_path}")  # Print image path being looked for
                
            if os.path.exists(image_path):
                display_image(image_path)  # Display the image using the function
            else:
                print(f"Image not found: {image_name}")
        else:
            print("No recipe found with that title.")
    else:
        print("No matching recipes found.")

# Function to display the image using matplotlib
def display_image(image_path):
    if os.path.exists(image_path):
        print(f"Displaying image: {image_path}")
        img = mpimg.imread(image_path)
        plt.imshow(img)
        plt.axis('off')  # Hides the axis
        plt.show()
    else:
        print(f"Image not found: {image_path}")

# Get input from the user
input_ingredients = input("Enter ingredients separated by commas: ").split(',')
find_matching_recipes(input_ingredients)





