document.addEventListener('DOMContentLoaded', () => {
    const recipes = JSON.parse(localStorage.getItem('recipes')) || [];
    
    // Display existing recipes
    displayRecipes(recipes);

    document.getElementById('recipeForm').addEventListener('submit', (e) => {
        e.preventDefault();
        
        const recipeName = document.getElementById('recipeName').value;
        const ingredients = document.getElementById('ingredients').value.split(', ');
        const instructions = document.getElementById('instructions').value;

        recipes.push({ name: recipeName, ingredients: ingredients, instructions: instructions });
        localStorage.setItem('recipes', JSON.stringify(recipes));
        
        displayRecipes(recipes);
    });

    function displayRecipes(recipes) {
        const recipesListElement = document.getElementById('recipesList');
        recipesListElement.innerHTML = '';
        
        for (const recipe of recipes) {
            const card = `
                <div class="card">
                    <h3>${recipe.name}</h3>
                    <p>Ingredients: ${recipe.ingredients.join(', ')}</p>
                    <p>Instructions:</p>
                    <pre>${recipe.instructions}</pre>
                </div>
            `;
            recipesListElement.innerHTML += card;
        }
    }
});
