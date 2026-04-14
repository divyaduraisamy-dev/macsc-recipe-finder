"""
MACSC Food Pantry Recipe Finder - CSV Database Version
=======================================================
This app loads recipes from your 75,000+ recipe CSV file.

HOW TO RUN:
1. Install requirements: pip install streamlit pandas deep-translator
2. Save this file as app.py
3. Put your CSV file in the same folder, named "recipes.csv"
4. Run: streamlit run app.py

HOW TO DEPLOY ONLINE (Free):
1. Create account at streamlit.io/cloud
2. Upload this code + your CSV to GitHub
3. Connect Streamlit Cloud to your GitHub repo
4. Your app will be live at a public URL!
"""

import streamlit as st
import pandas as pd
import ast
import re

# Try to import translator (optional - for Spanish translation)
try:
    from deep_translator import GoogleTranslator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False

# =============================================================================
# CONFIGURATION
# =============================================================================
CSV_FILE = "recipes_trimmed.csv"  # Your recipe CSV file name
APP_TITLE = "MACSC Recipe Finder"

# =============================================================================
# CUSTOM STYLING - MACSC Brand Colors
# =============================================================================
# Primary Green: #355210
# Light Green: #accc90
# Dusty Rose: #ad8b81
# Rust/Terra Cotta: #a14329
# Warm Gray: #aeaa99

CUSTOM_CSS = """
<style>
    /* Override Streamlit's CSS custom properties at root */
    :root {
        --text-color: #2d2d2d !important;
        --font-color: #2d2d2d !important;
        --primary-color: #355210 !important;
    }

    /* Main app background */
    .stApp {
        background-color: #f5f3f0;
    }
    
    /* Headers */
    h1 {
        color: #355210 !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #accc90;
        padding-bottom: 10px;
    }
    
    h2, h3 {
        color: #355210 !important;
        font-weight: 600 !important;
    }
    
    /* All regular text - ensure readability */
    p, span, label, .stMarkdown {
        color: #2d2d2d !important;
    }
    
    /* ========================================================
       EXPANDER FIX - Streamlit 1.51 specific
       In 1.51, the expander header gets a dark background
       when opened/hovered. We force it back to white.
       ======================================================== */
    
    /* Force the expander container background */
    .stExpander,
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #aeaa99 !important;
        border-radius: 8px !important;
    }
    
    /* Force the summary/header background to NEVER go dark */
    summary,
    details summary,
    details[open] summary,
    details[open] > summary,
    .stExpander summary,
    .stExpander details summary,
    .stExpander details[open] summary,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details summary,
    [data-testid="stExpander"] details[open] summary,
    [data-testid="stExpanderToggleIcon"],
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
        border-left: 4px solid #355210 !important;
        border-radius: 8px !important;
    }
    
    /* Hover state - keep light */
    summary:hover,
    details summary:hover,
    details[open] summary:hover,
    .stExpander summary:hover,
    [data-testid="stExpander"] summary:hover {
        background-color: #f5f3f0 !important;
        background: #f5f3f0 !important;
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
    }
    
    /* Focus/active states */
    summary:focus,
    summary:active,
    summary:focus-visible,
    summary:focus-within,
    details[open] > summary:focus,
    details[open] > summary:active {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* All text inside summary headers */
    summary *,
    summary:hover *,
    summary:focus *,
    summary:active *,
    details[open] > summary *,
    details[open] > summary:hover *,
    .streamlit-expanderHeader *,
    .stExpander summary *,
    [data-testid="stExpander"] summary * {
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* SVG arrow icons */
    summary svg,
    summary:hover svg,
    details[open] > summary svg {
        fill: #2d2d2d !important;
        color: #2d2d2d !important;
        stroke: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
    }
    
    /* Expander content area */
    .streamlit-expanderContent,
    .stExpander [data-testid="stExpanderContent"],
    details > div {
        background-color: #ffffff !important;
        color: #2d2d2d !important;
    }
    
    /* ========================================================
       SIDEBAR - same treatment
       ======================================================== */
    [data-testid="stSidebar"] {
        background-color: #f0ede8 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
    }
    
    [data-testid="stSidebar"] summary,
    [data-testid="stSidebar"] details summary,
    [data-testid="stSidebar"] details[open] summary,
    [data-testid="stSidebar"] summary:hover,
    [data-testid="stSidebar"] details[open] summary:hover {
        background-color: #f0ede8 !important;
        background: #f0ede8 !important;
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
    }
    
    [data-testid="stSidebar"] summary *,
    [data-testid="stSidebar"] summary:hover *,
    [data-testid="stSidebar"] details[open] summary *,
    [data-testid="stSidebar"] summary svg {
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
        background: transparent !important;
    }

    /* ========================================================
       BUTTONS
       ======================================================== */
    .stButton > button {
        background-color: #355210 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #a14329 !important;
        box-shadow: 0 4px 12px rgba(161, 67, 41, 0.3) !important;
    }
    
    .stButton > button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background-color: #a14329 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #355210 !important;
    }
    
    /* ========================================================
       FORM ELEMENTS
       ======================================================== */
    .stCheckbox label,
    .stCheckbox label span {
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
    }
    
    .stRadio label,
    .stRadio div[role="radiogroup"] label span {
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
    }
    
    .stSelectbox label {
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
    }
    
    .stSlider label,
    .stSlider [data-baseweb="slider"] {
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
    }
    
    .stMultiSelect label {
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
    }
    
    .stTextInput label {
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
    }

    /* ========================================================
       METRICS - must override Streamlit 1.51 theme colors
       ======================================================== */
    [data-testid="metric-container"] {
        background-color: #ffffff !important;
        border-radius: 8px !important;
        padding: 10px !important;
        border: 1px solid #accc90 !important;
    }
    
    /* Metric labels (Prep, Cook, Difficulty, Health) */
    [data-testid="metric-container"] label,
    [data-testid="metric-container"] label *,
    [data-testid="metric-container"] [data-testid="stMetricLabel"],
    [data-testid="metric-container"] [data-testid="stMetricLabel"] * {
        color: #355210 !important;
        -webkit-text-fill-color: #355210 !important;
    }
    
    /* Metric values (the big numbers/text) - nuclear approach */
    [data-testid="metric-container"] [data-testid="stMetricValue"],
    [data-testid="metric-container"] [data-testid="stMetricValue"] *,
    [data-testid="metric-container"] [data-testid="stMetricValue"] div,
    [data-testid="metric-container"] [data-testid="stMetricValue"] span,
    [data-testid="metric-container"] [data-testid="stMetricValue"] p,
    [data-testid="metric-container"] div:nth-child(2),
    [data-testid="metric-container"] div:nth-child(2) *,
    [data-testid="metric-container"] > div > div:last-child,
    [data-testid="metric-container"] > div > div:last-child *,
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] *,
    .stMetric [data-testid="stMetricValue"],
    .stMetric [data-testid="stMetricValue"] * {
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
    }
    
    /* Catch-all: ANY text inside a metric container */
    [data-testid="metric-container"] * {
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
    }
    
    /* Then re-apply the green to just the label */
    [data-testid="metric-container"] label,
    [data-testid="metric-container"] label *,
    [data-testid="metric-container"] [data-testid="stMetricLabel"],
    [data-testid="metric-container"] [data-testid="stMetricLabel"] * {
        color: #355210 !important;
        -webkit-text-fill-color: #355210 !important;
    }

    /* ========================================================
       MESSAGES
       ======================================================== */
    .stSuccess {
        background-color: #e8f0dc !important;
        border-left: 4px solid #355210 !important;
        color: #2d2d2d !important;
    }
    
    .stSuccess p {
        color: #2d2d2d !important;
    }
    
    .stInfo {
        background-color: #f0ebe8 !important;
        border-left: 4px solid #ad8b81 !important;
        color: #2d2d2d !important;
    }
    
    .stInfo p {
        color: #2d2d2d !important;
    }
    
    .stWarning {
        background-color: #f5ebe8 !important;
        border-left: 4px solid #a14329 !important;
        color: #2d2d2d !important;
    }
    
    .stWarning p {
        color: #2d2d2d !important;
    }

    /* ========================================================
       LAYOUT
       ======================================================== */
    /* Dividers */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(to right, transparent, #accc90, transparent) !important;
        margin: 1rem 0 !important;
    }
    
    /* Category headers */
    .category-header {
        background: linear-gradient(90deg, #355210 0%, #4a6b1a 100%);
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        padding: 10px 16px;
        border-radius: 6px;
        margin: 20px 0 12px 0;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Ingredient indicators */
    .ingredient-have {
        color: #355210 !important;
        font-weight: 500;
    }
    
    .ingredient-need {
        color: #a14329 !important;
        font-weight: 600;
    }
    
    /* Selected ingredient tags */
    .selected-tag {
        background-color: #accc90;
        color: #355210;
        padding: 4px 12px;
        border-radius: 16px;
        margin: 2px;
        display: inline-block;
        font-size: 0.9rem;
    }
    
    /* Caption text */
    .stCaption {
        color: #666666 !important;
    }
    
    /* Show more/less category buttons - lighter and more visible */
    .show-more-btn button {
        background-color: #accc90 !important;
        color: #355210 !important;
        -webkit-text-fill-color: #355210 !important;
        font-weight: 600 !important;
        border: 1px solid #355210 !important;
    }
    
    .show-more-btn button:hover {
        background-color: #355210 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    .show-more-btn button * {
        color: inherit !important;
        -webkit-text-fill-color: inherit !important;
    }
    
    /* Category nav sidebar */
    .category-nav {
        position: sticky;
        top: 1rem;
        background-color: #ffffff;
        border: 1px solid #accc90;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }
    
    .category-nav-title {
        color: #355210;
        -webkit-text-fill-color: #355210;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 8px;
        border-bottom: 2px solid #accc90;
        padding-bottom: 6px;
    }
    
    /* Write/text elements */
    .stWrite {
        color: #2d2d2d !important;
    }
    
    /* Column text */
    [data-testid="column"] {
        color: #2d2d2d !important;
    }
    
    [data-testid="column"] p {
        color: #2d2d2d !important;
    }
</style>

<!-- JavaScript: force background + text color on expander HEADERS only -->
<script>
function fixExpanders() {
        el.style.setProperty('background-color', '#ffffff', 'important');
        el.style.setProperty('background', '#ffffff', 'important');
        el.style.setProperty('color', '#2d2d2d', 'important');
        el.style.setProperty('-webkit-text-fill-color', '#2d2d2d', 'important');
        el.querySelectorAll(':scope > *').forEach(function(child) {
            child.style.setProperty('color', '#2d2d2d', 'important');
            child.style.setProperty('-webkit-text-fill-color', '#2d2d2d', 'important');
            child.style.setProperty('background-color', 'transparent', 'important');
            child.style.setProperty('background', 'transparent', 'important');
            child.querySelectorAll('*').forEach(function(grandchild) {
                grandchild.style.setProperty('color', '#2d2d2d', 'important');
                grandchild.style.setProperty('-webkit-text-fill-color', '#2d2d2d', 'important');
                grandchild.style.setProperty('background-color', 'transparent', 'important');
                grandchild.style.setProperty('background', 'transparent', 'important');
            });
        });
    });
}

function fixMetrics() {
    // Force all metric values to be dark and visible
    document.querySelectorAll('[data-testid="metric-container"]').forEach(function(container) {
        container.querySelectorAll('*').forEach(function(el) {
            el.style.setProperty('color', '#2d2d2d', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#2d2d2d', 'important');
        });
        // Re-apply green to labels only
        container.querySelectorAll('[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *').forEach(function(el) {
            el.style.setProperty('color', '#355210', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#355210', 'important');
        });
        // Also target label elements
        container.querySelectorAll('label, label *').forEach(function(el) {
            el.style.setProperty('color', '#355210', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#355210', 'important');
        });
    });
}

function fixAll() {
    fixExpanders();
    fixMetrics();
}

document.addEventListener('click', function() {
    fixAll();
    setTimeout(fixAll, 50);
    setTimeout(fixAll, 150);
    setTimeout(fixAll, 300);
    setTimeout(fixAll, 500);
});

document.addEventListener('mouseover', function(e) {
    var summary = e.target.closest('summary');
    if (summary) { fixAll(); }
});
document.addEventListener('mouseout', function(e) {
    var summary = e.target.closest('summary');
    if (summary) {
        setTimeout(fixAll, 10);
        setTimeout(fixAll, 100);
    }
});

fixAll();
setTimeout(fixAll, 500);
setTimeout(fixAll, 1000);
setTimeout(fixAll, 2000);

var observer = new MutationObserver(function() {
    fixAll();
});
observer.observe(document.body, { childList: true, subtree: true, attributes: true });
</script>
"""

# =============================================================================
# TRANSLATIONS (Interface only - recipes stay in English)
# =============================================================================
TRANSLATIONS = {
    "en": {
        "title": "MACSC Recipe Finder",
        "subtitle": "Find recipes based on what you have!",
        "what_items": "What Ingredients Do You Have?",
        "select_help": "Select ingredients you got from the pantry",
        "your_items": "Your Selected Ingredients",
        "clear_all": "Clear All",
        "find_recipes": "Find Recipes",
        "filters": "Filters",
        "max_ingredients": "Maximum Ingredients in Recipe",
        "max_time": "Maximum Total Time (minutes)",
        "difficulty": "Difficulty Level",
        "dietary": "Dietary Preferences",
        "any": "Any",
        "easy": "Easy",
        "medium": "Medium", 
        "hard": "Hard",
        "found": "Found {count} recipes!",
        "no_recipes": "No recipes found. Try selecting different ingredients or adjusting filters.",
        "ingredients": "Ingredients",
        "directions": "Directions",
        "time": "Time",
        "prep": "Prep",
        "cook": "Cook",
        "mins": "mins",
        "you_have": "You have",
        "you_need": "You need",
        "match": "match",
        "show_more": "Show more recipes",
        "recipes_shown": "Showing {shown} of {total} recipes",
        "health_level": "Health Level",
        "cuisine": "Cuisine",
        "translating": "Translating...",
        "translation_note": "Recipes will be translated to Spanish when opened.",
        "translation_missing": "For Spanish translation, install: pip install deep-translator",
        "more_in_category": "and {count} more recipes in this category",
        "show_less": "Show less",
        "browse_categories": "Browse Categories",
        "jump_to": "Jump to category",
        "collapse_all": "Collapse All",
        "appliance": "Cooking Appliance",
        "stovetop": "Stovetop",
        "oven_appliance": "Oven",
        "microwave": "Microwave",
        "air_fryer": "Air Fryer",
        "slow_cooker": "Slow Cooker",
        "grill": "Grill",
        "no_cook": "No Cook / No Appliance",
        "type_ingredient": "Or type an ingredient",
        "add_ingredient": "Add",
    },
    "es": {
        "title": "Buscador de Recetas MACSC",
        "subtitle": "Encuentra recetas con lo que tienes!",
        "what_items": "Que Ingredientes Tienes?",
        "select_help": "Selecciona los ingredientes que recibiste",
        "your_items": "Ingredientes Seleccionados",
        "clear_all": "Borrar Todo",
        "find_recipes": "Buscar Recetas",
        "filters": "Filtros",
        "max_ingredients": "Maximo de Ingredientes en Receta",
        "max_time": "Tiempo Maximo Total (minutos)",
        "difficulty": "Nivel de Dificultad",
        "dietary": "Preferencias Dieteticas",
        "any": "Cualquiera",
        "easy": "Facil",
        "medium": "Medio",
        "hard": "Dificil",
        "found": "{count} recetas encontradas!",
        "no_recipes": "No se encontraron recetas. Intenta con otros ingredientes o filtros.",
        "ingredients": "Ingredientes",
        "directions": "Instrucciones",
        "time": "Tiempo",
        "prep": "Preparacion",
        "cook": "Coccion",
        "mins": "min",
        "you_have": "Tienes",
        "you_need": "Necesitas",
        "match": "coincidencia",
        "show_more": "Mostrar mas recetas",
        "recipes_shown": "Mostrando {shown} de {total} recetas",
        "health_level": "Nivel de Salud",
        "cuisine": "Cocina",
        "translating": "Traduciendo...",
        "translation_note": "Las recetas se traduciran al espanol cuando las abras.",
        "translation_missing": "Para traduccion al espanol, instala: pip install deep-translator",
        "more_in_category": "y {count} recetas mas en esta categoria",
        "show_less": "Mostrar menos",
        "browse_categories": "Explorar Categorias",
        "jump_to": "Ir a categoria",
        "collapse_all": "Cerrar Todo",
        "appliance": "Electrodomestico de Cocina",
        "stovetop": "Estufa",
        "oven_appliance": "Horno",
        "microwave": "Microondas",
        "air_fryer": "Freidora de Aire",
        "slow_cooker": "Olla de Coccion Lenta",
        "grill": "Parrilla",
        "no_cook": "Sin Coccion / Sin Electrodomestico",
        "type_ingredient": "O escribe un ingrediente",
        "add_ingredient": "Agregar",
    }
}

# =============================================================================
# PANTRY INGREDIENTS - What your food pantry typically provides
# =============================================================================
PANTRY_INGREDIENTS = {
    "Canned Vegetables / Vegetales": [
        "canned mixed vegetables", "canned green beans", "canned corn",
        "canned diced tomatoes", "canned tomato sauce", "canned tomatoes",
        "canned peas", "canned carrots", "tomato paste"
    ],
    "Canned Beans / Frijoles": [
        "canned black beans", "canned kidney beans", "canned pinto beans",
        "canned white beans", "canned red beans", "canned chickpeas",
        "black beans", "kidney beans", "pinto beans", "white beans"
    ],
    "Canned Soups / Sopas": [
        "cream of mushroom soup", "cream of chicken soup", "cream of celery soup",
        "chicken noodle soup", "tomato soup", "vegetable soup"
    ],
    "Canned Proteins / Proteínas": [
        "canned tuna", "canned chicken", "canned salmon", "tuna", "chicken"
    ],
    "Canned Fruits / Frutas": [
        "canned peaches", "canned pears", "applesauce", "canned fruit cocktail"
    ],
    "Pasta & Grains / Pasta y Granos": [
        "elbow pasta", "spaghetti", "pasta", "macaroni", "rice", "egg noodles",
        "penne", "rotini", "oats", "oatmeal"
    ],
    "Dairy & Eggs / Lácteos": [
        "milk", "butter", "cheese", "eggs", "cheddar cheese", "cream cheese",
        "sour cream", "yogurt"
    ],
    "Pantry Staples / Básicos": [
        "peanut butter", "vegetable oil", "olive oil", "flour", "sugar",
        "salt", "pepper", "garlic", "onion", "bread"
    ],
    "Seasonal Produce / Productos Frescos": [
        "potatoes", "onions", "carrots", "celery", "lettuce",
        "tomatoes", "bananas", "apples", "oranges"
    ],
}

# Flatten for easy searching
ALL_PANTRY_ITEMS = []
for items in PANTRY_INGREDIENTS.values():
    ALL_PANTRY_ITEMS.extend(items)


# =============================================================================
# TRANSLATION FUNCTIONS
# =============================================================================
@st.cache_data
def translate_text(text, target_lang='es'):
    """Translate text to target language using Google Translate."""
    if not TRANSLATION_AVAILABLE or not text or target_lang == 'en':
        return text
    try:
        translator = GoogleTranslator(source='en', target=target_lang)
        return translator.translate(text)
    except:
        return text

def translate_recipe(recipe, lang):
    """Translate recipe title, ingredients, and directions to target language."""
    if lang == 'en' or not TRANSLATION_AVAILABLE:
        return recipe
    
    # Create a copy to avoid modifying original
    translated = recipe.copy()
    
    # Translate title
    translated['recipe_title_display'] = translate_text(recipe['recipe_title'], lang)
    
    # Translate ingredients
    ingredients = recipe.get('ingredients_list', [])
    translated['ingredients_translated'] = [translate_text(ing, lang) for ing in ingredients]
    
    # Translate directions
    directions = recipe.get('directions_list', [])
    translated['directions_translated'] = [translate_text(step, lang) for step in directions]
    
    return translated


# =============================================================================
# CATEGORY GROUPING
# =============================================================================
def get_recipe_category(recipe):
    """Determine the category of a recipe based on its data."""
    category = str(recipe.get('category', '')).lower()
    subcategory = str(recipe.get('subcategory', '')).lower()
    title = str(recipe.get('recipe_title', '')).lower()
    course_list = str(recipe.get('course_list', '')).lower()
    
    combined = category + ' ' + subcategory + ' ' + title
    
    # Check for specific categories - order matters (more specific first)
    
    # Sandwiches, wraps, tacos go to their own category (check BEFORE breads)
    if any(word in combined for word in ['sandwich', 'wrap', 'taco', 'burrito', 'quesadilla', 'burger', 'sub ', 'hoagie', 'panini', 'pita pocket', 'gyro']):
        return 'Sandwiches & Wraps'
    
    if any(word in combined for word in ['soup', 'stew', 'chili', 'chowder']):
        return 'Soups & Stews'
    
    # Desserts - be strict, avoid false positives like "sweet potato" or "sweet chili"
    dessert_keywords = ['dessert', 'cake', 'cookie', 'cookies', 'pie', 'brownie', 
                        'candy', 'fudge', 'frosting', 'cupcake', 'pudding', 'cobbler',
                        'truffle', 'cheesecake', 'ice cream', 'sorbet', 'mousse',
                        'tart', 'pastry', 'pastries', 'macaron', 'tiramisu', 'custard']
    if any(word in combined for word in dessert_keywords):
        # Double check it's not a savory item with a misleading word
        savory_overrides = ['sweet potato', 'sweet corn', 'sweet chili', 'sweet onion',
                           'sweet pepper', 'sweet and sour', 'sweet & sour', 'pot pie',
                           'shepherd', 'chicken pie', 'turkey pie', 'meat pie',
                           'pie iron', 'pizza pie']
        if not any(override in combined for override in savory_overrides):
            return 'Desserts'
    
    if any(word in combined for word in ['breakfast', 'brunch', 'pancake', 'waffle', 'omelet', 'omelette']):
        return 'Breakfast'
    
    # Egg dishes - only classify as breakfast if clearly breakfast-style
    if 'egg' in combined and any(word in combined for word in ['scrambl', 'benedict', 'frittata', 'breakfast']):
        return 'Breakfast'
    
    if any(word in combined for word in ['salad']):
        return 'Salads'
    
    if any(word in combined for word in ['appetizer', 'snack', 'dip', 'finger food', 'spread']):
        return 'Appetizers & Snacks'
    
    # Breads - actual baked bread items, not sandwiches
    bread_keywords = ['bread', 'muffin', 'biscuit', 'cornbread', 'focaccia',
                      'bagel', 'scone', 'breadstick', 'dinner roll', 'yeast roll',
                      'banana bread', 'zucchini bread', 'pumpkin bread']
    if any(word in combined for word in bread_keywords):
        # Make sure it's not a sandwich or something using bread as an ingredient
        bread_overrides = ['bread bowl', 'bread crumb', 'breadcrumb', 'bread pudding',
                          'french bread pizza', 'garlic bread']
        # If it specifically says 'bread' in the title, check if the title is ABOUT bread
        if any(word in title for word in ['bread', 'muffin', 'biscuit', 'cornbread',
                                           'focaccia', 'scone', 'roll']):
            if not any(override in combined for override in bread_overrides):
                return 'Breads & Baked Goods'
        elif any(word in category + subcategory for word in bread_keywords):
            return 'Breads & Baked Goods'
    
    if any(word in combined for word in ['drink', 'beverage', 'smoothie', 'cocktail', 'lemonade', 'punch']):
        return 'Drinks'
    
    if any(word in combined for word in ['side', 'vegetable']):
        return 'Side Dishes'
    
    if any(word in category + subcategory + course_list for word in ['main', 'dinner', 'lunch', 'entrée', 'entree']):
        return 'Main Dishes'
    
    return 'Main Dishes'  # Default

CATEGORY_ORDER = [
    'Main Dishes',
    'Sandwiches & Wraps',
    'Soups & Stews', 
    'Salads',
    'Side Dishes',
    'Breakfast',
    'Appetizers & Snacks',
    'Breads & Baked Goods',
    'Desserts',
    'Drinks'
]

CATEGORY_TRANSLATIONS = {
    'Main Dishes': 'Platos Principales',
    'Sandwiches & Wraps': 'Sandwiches y Wraps',
    'Soups & Stews': 'Sopas y Guisos',
    'Salads': 'Ensaladas',
    'Side Dishes': 'Acompañamientos',
    'Breakfast': 'Desayuno',
    'Appetizers & Snacks': 'Aperitivos y Snacks',
    'Breads & Baked Goods': 'Panes y Horneados',
    'Desserts': 'Postres',
    'Drinks': 'Bebidas'
}


# =============================================================================
# DATA LOADING AND PROCESSING
# =============================================================================
@st.cache_data
def load_recipes(filepath):
    """Load and preprocess the recipe CSV."""
    try:
        df = pd.read_csv(filepath)
        
        # Calculate total time
        df['total_time'] = df['est_prep_time_min'].fillna(0) + df['est_cook_time_min'].fillna(0)
        
        # Parse ingredients list
        def parse_ingredients(ing_str):
            if pd.isna(ing_str):
                return []
            try:
                return ast.literal_eval(ing_str)
            except:
                return []
        
        df['ingredients_list'] = df['ingredients_raw'].apply(parse_ingredients)
        
        # Parse directions list  
        def parse_directions(dir_str):
            if pd.isna(dir_str):
                return []
            try:
                return ast.literal_eval(dir_str)
            except:
                return []
        
        df['directions_list'] = df['directions_raw'].apply(parse_directions)
        
        # Create searchable ingredient text (lowercase)
        df['ingredient_search'] = df['ingredient_text'].fillna('').str.lower()
        
        # Detect appliances from directions text
        directions_text = df['directions_raw'].fillna('').str.lower()
        
        df['uses_oven'] = directions_text.str.contains(
            'oven|bake |baking|broil|roast|preheat', regex=True
        )
        df['uses_stovetop'] = directions_text.str.contains(
            'stovetop|stove top|skillet|frying pan|saucepan|saute|sauté|boil|simmer|pan fry|panfry|wok|pot ', regex=True
        )
        df['uses_microwave'] = directions_text.str.contains(
            'microwave', regex=True
        )
        df['uses_air_fryer'] = directions_text.str.contains(
            'air fryer|air fry|airfryer|air-fryer', regex=True
        )
        df['uses_slow_cooker'] = directions_text.str.contains(
            'slow cooker|crock pot|crockpot|crock-pot', regex=True
        )
        df['uses_grill'] = directions_text.str.contains(
            'grill|grilling|barbecue|bbq', regex=True
        )
        # No-cook recipes (none of the above detected)
        df['no_cook'] = ~(df['uses_oven'] | df['uses_stovetop'] | df['uses_microwave'] | 
                          df['uses_air_fryer'] | df['uses_slow_cooker'] | df['uses_grill'])
        
        return df
    
    except FileNotFoundError:
        st.error(f"Could not find '{filepath}'. Please make sure the CSV file is in the same folder as app.py")
        return None
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return None


def find_matching_recipes(df, selected_ingredients, max_ingredients, max_time, difficulty, dietary_filters, health_level="any", cuisine_filter="any", appliance_filters=None):
    """Find recipes that match selected ingredients."""
    
    if not selected_ingredients:
        return pd.DataFrame()
    
    # Start with all recipes
    filtered = df.copy()
    
    # Filter by number of ingredients
    if max_ingredients < 20:
        filtered = filtered[filtered['num_ingredients'] <= max_ingredients]
    
    # Filter by total time
    if max_time < 120:
        filtered = filtered[filtered['total_time'] <= max_time]
    
    # Filter by difficulty
    if difficulty != "any":
        filtered = filtered[filtered['difficulty'] == difficulty]
    
    # Filter by health level
    if health_level != "any":
        filtered = filtered[filtered['health_level'] == health_level]
    
    # Filter by cuisine
    if cuisine_filter != "any":
        # cuisine_list is a string containing list of cuisines
        filtered = filtered[filtered['cuisine_list'].fillna('').str.lower().str.contains(cuisine_filter.lower())]
    
    # Filter by dietary preferences
    if 'vegetarian' in dietary_filters:
        filtered = filtered[filtered['is_vegetarian'] == True]
    if 'vegan' in dietary_filters:
        filtered = filtered[filtered['is_vegan'] == True]
    if 'gluten free' in dietary_filters:
        filtered = filtered[filtered['is_gluten_free'] == True]
    if 'dairy free' in dietary_filters:
        filtered = filtered[filtered['is_dairy_free'] == True]
    
    # Filter by appliance
    if appliance_filters:
        appliance_mask = pd.Series(False, index=filtered.index)
        for app in appliance_filters:
            if app == "stovetop":
                appliance_mask = appliance_mask | filtered['uses_stovetop']
            elif app == "oven":
                appliance_mask = appliance_mask | filtered['uses_oven']
            elif app == "microwave":
                appliance_mask = appliance_mask | filtered['uses_microwave']
            elif app == "air_fryer":
                appliance_mask = appliance_mask | filtered['uses_air_fryer']
            elif app == "slow_cooker":
                appliance_mask = appliance_mask | filtered['uses_slow_cooker']
            elif app == "grill":
                appliance_mask = appliance_mask | filtered['uses_grill']
            elif app == "no_cook":
                appliance_mask = appliance_mask | filtered['no_cook']
        filtered = filtered[appliance_mask]
    
    # Score recipes by ingredient matches
    def score_recipe(row):
        ingredient_text = row['ingredient_search']
        matches = 0
        matched_items = []
        
        for ing in selected_ingredients:
            # Create search variations
            ing_lower = ing.lower()
            ing_simple = ing_lower.replace('canned ', '')
            
            if ing_simple in ingredient_text or ing_lower in ingredient_text:
                matches += 1
                matched_items.append(ing)
        
        return matches, matched_items
    
    # Apply scoring
    scores = filtered.apply(score_recipe, axis=1)
    filtered['match_count'] = scores.apply(lambda x: x[0])
    filtered['matched_ingredients'] = scores.apply(lambda x: x[1])
    
    # Only keep recipes with at least 1 match
    filtered = filtered[filtered['match_count'] > 0]
    
    # Calculate match percentage
    filtered['match_percent'] = (filtered['match_count'] / filtered['num_ingredients'] * 100).round(0)
    
    # Sort by match count (descending), then by fewer total ingredients
    filtered = filtered.sort_values(
        by=['match_count', 'num_ingredients'], 
        ascending=[False, True]
    )
    
    return filtered


def find_all_recipes(df, max_ingredients, max_time, difficulty, dietary_filters, health_level="any", cuisine_filter="any", appliance_filters=None):
    """Find all recipes matching filters (no ingredient matching required)."""
    
    filtered = df.copy()
    
    # Filter by number of ingredients
    if max_ingredients < 20:
        filtered = filtered[filtered['num_ingredients'] <= max_ingredients]
    
    # Filter by total time
    if max_time < 120:
        filtered = filtered[filtered['total_time'] <= max_time]
    
    # Filter by difficulty
    if difficulty != "any":
        filtered = filtered[filtered['difficulty'] == difficulty]
    
    # Filter by health level
    if health_level != "any":
        filtered = filtered[filtered['health_level'] == health_level]
    
    # Filter by cuisine
    if cuisine_filter != "any":
        filtered = filtered[filtered['cuisine_list'].fillna('').str.lower().str.contains(cuisine_filter.lower())]
    
    # Filter by dietary preferences
    if 'vegetarian' in dietary_filters:
        filtered = filtered[filtered['is_vegetarian'] == True]
    if 'vegan' in dietary_filters:
        filtered = filtered[filtered['is_vegan'] == True]
    if 'gluten free' in dietary_filters:
        filtered = filtered[filtered['is_gluten_free'] == True]
    if 'dairy free' in dietary_filters:
        filtered = filtered[filtered['is_dairy_free'] == True]
    
    # Filter by appliance
    if appliance_filters:
        appliance_mask = pd.Series(False, index=filtered.index)
        for app in appliance_filters:
            if app == "stovetop":
                appliance_mask = appliance_mask | filtered['uses_stovetop']
            elif app == "oven":
                appliance_mask = appliance_mask | filtered['uses_oven']
            elif app == "microwave":
                appliance_mask = appliance_mask | filtered['uses_microwave']
            elif app == "air_fryer":
                appliance_mask = appliance_mask | filtered['uses_air_fryer']
            elif app == "slow_cooker":
                appliance_mask = appliance_mask | filtered['uses_slow_cooker']
            elif app == "grill":
                appliance_mask = appliance_mask | filtered['uses_grill']
            elif app == "no_cook":
                appliance_mask = appliance_mask | filtered['no_cook']
        filtered = filtered[appliance_mask]
    
    # No ingredient matching, so set defaults
    filtered['match_count'] = 0
    filtered['matched_ingredients'] = [[] for _ in range(len(filtered))]
    filtered['match_percent'] = 0.0
    
    # Sort by fewest ingredients (simplest recipes first)
    filtered = filtered.sort_values(by=['total_time', 'num_ingredients'], ascending=[True, True])
    
    return filtered


def _display_recipe_card(recipe, has_ingredients, lang, t, idx, category, section):
    """Display a single recipe as an expandable card."""
    title_display = recipe['recipe_title']
    time_display = f"{int(recipe['total_time'])} {t['mins']}" if pd.notna(recipe['total_time']) else ""
    
    if has_ingredients:
        match_pct = recipe['match_percent']
        match_count = recipe['match_count']
        total_ing = recipe['num_ingredients']
        header = (
            f"**{title_display}** -- "
            f"{int(match_pct)}% {t['match']} ({match_count}/{total_ing}) | {time_display}"
        )
    else:
        total_ing = recipe['num_ingredients']
        header = f"**{title_display}** -- {total_ing} ingredients | {time_display}"
    
    with st.expander(header):
        # Translate recipe if Spanish
        if lang == 'es' and TRANSLATION_AVAILABLE:
            with st.spinner(t["translating"]):
                recipe = translate_recipe(recipe, lang)
        
        # Time info row
        prep = recipe['est_prep_time_min']
        cook = recipe['est_cook_time_min']
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        col_t1.metric(t["prep"], f"{int(prep) if pd.notna(prep) else '?'} {t['mins']}")
        col_t2.metric(t["cook"], f"{int(cook) if pd.notna(cook) else '?'} {t['mins']}")
        col_t3.metric("Difficulty" if lang == 'en' else "Dificultad", recipe['difficulty'])
        col_t4.metric("Health" if lang == 'en' else "Salud", recipe.get('health_level', 'N/A'))
        
        st.divider()
        
        # Ingredients
        st.write(f"**{t['ingredients']}:**")
        
        matched = recipe.get('matched_ingredients', [])
        
        # Use translated ingredients if available
        if lang == 'es' and 'ingredients_translated' in recipe:
            ingredients = recipe['ingredients_translated']
        else:
            ingredients = recipe['ingredients_list']
        
        original_ingredients = recipe['ingredients_list']
        
        # Two column layout for ingredients
        col1, col2 = st.columns(2)
        for i, ing in enumerate(ingredients):
            orig_ing = original_ingredients[i] if i < len(original_ingredients) else ing
            target_col = col1 if i % 2 == 0 else col2
            
            if has_ingredients and matched:
                ing_lower = orig_ing.lower()
                is_match = any(
                    sel.lower().replace('canned ', '') in ing_lower 
                    for sel in matched
                )
                if is_match:
                    target_col.markdown(f"<span style='color: #2c5530;'>&#10003; {ing}</span>", unsafe_allow_html=True)
                else:
                    target_col.markdown(f"<span style='color: #8b4513;'><b>+ {ing}</b></span>", unsafe_allow_html=True)
            else:
                target_col.write(f"- {ing}")
        
        st.divider()
        
        # Directions
        st.write(f"**{t['directions']}:**")
        
        if lang == 'es' and 'directions_translated' in recipe:
            directions = recipe['directions_translated']
        else:
            directions = recipe['directions_list']
        
        for i, step in enumerate(directions, 1):
            st.write(f"{i}. {step}")


# =============================================================================
# MAIN APP
# =============================================================================
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="", layout="wide")
    
    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Initialize session state
    if 'selected_ingredients' not in st.session_state:
        st.session_state.selected_ingredients = []
    if 'lang' not in st.session_state:
        st.session_state.lang = 'en'
    if 'recipes_to_show' not in st.session_state:
        st.session_state.recipes_to_show = 10
    
    # Language toggle
    col1, col2 = st.columns([6, 1])
    with col2:
        lang_choice = st.radio("Language", ["EN", "ES"], horizontal=True, label_visibility="collapsed")
        st.session_state.lang = 'en' if lang_choice == "EN" else 'es'
    
    lang = st.session_state.lang
    t = TRANSLATIONS[lang]
    
    # Header
    st.title(t["title"])
    st.write(t["subtitle"])
    
    # Load recipes
    df = load_recipes(CSV_FILE)
    
    if df is None:
        st.stop()
    
    st.success(f"Loaded {len(df):,} recipes")
    
    # Two-column layout
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader(t["what_items"])
        st.caption(t["select_help"])
        
        # Show selected ingredients
        if st.session_state.selected_ingredients:
            st.write(f"**{t['your_items']}:** {len(st.session_state.selected_ingredients)}")
            
            # Display as removable tags
            for ing in st.session_state.selected_ingredients:
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"• {ing}")
                if col_b.button("X", key=f"remove_{ing}"):
                    st.session_state.selected_ingredients.remove(ing)
                    st.rerun()
            
            if st.button(t["clear_all"]):
                st.session_state.selected_ingredients = []
                st.rerun()
            
            st.divider()
        
        # Text input for typing a custom ingredient
        typed_ingredient = st.text_input(
            t["type_ingredient"],
            key="ingredient_text_input",
            placeholder="e.g. chicken, rice, lemon..."
        )
        if typed_ingredient and typed_ingredient.strip():
            cleaned = typed_ingredient.strip().lower()
            if cleaned not in [i.lower() for i in st.session_state.selected_ingredients]:
                if st.button(t["add_ingredient"] + f': "{cleaned}"', key="add_typed_ingredient"):
                    st.session_state.selected_ingredients.append(cleaned)
                    st.rerun()
        
        st.divider()
        
        # Ingredient selection by category
        for category, items in PANTRY_INGREDIENTS.items():
            with st.expander(category):
                for item in items:
                    is_selected = item in st.session_state.selected_ingredients
                    # Use category + item for unique key to avoid duplicates
                    unique_key = f"cb_{category}_{item}"
                    if st.checkbox(item, value=is_selected, key=unique_key):
                        if item not in st.session_state.selected_ingredients:
                            st.session_state.selected_ingredients.append(item)
                            st.rerun()
                    elif item in st.session_state.selected_ingredients:
                        st.session_state.selected_ingredients.remove(item)
                        st.rerun()
        
        st.divider()
        
        # Filters
        st.subheader(t["filters"])
        
        max_ingredients = st.slider(
            t["max_ingredients"], 
            min_value=3, max_value=20, value=12
        )
        
        max_time = st.slider(
            t["max_time"],
            min_value=10, max_value=120, value=60
        )
        
        difficulty_options = {
            t["any"]: "any",
            t["easy"]: "easy", 
            t["medium"]: "medium",
            t["hard"]: "hard"
        }
        difficulty_choice = st.selectbox(t["difficulty"], list(difficulty_options.keys()))
        difficulty = difficulty_options[difficulty_choice]
        
        dietary_filters = st.multiselect(
            t["dietary"],
            ["vegetarian", "vegan", "gluten free", "dairy free"]
        )
        
        # Health level filter
        health_options = {
            t["any"]: "any",
            "Healthy": "healthy",
            "Moderate": "moderate",
            "Indulgent": "indulgent"
        }
        health_choice = st.selectbox(t["health_level"], list(health_options.keys()))
        health_level = health_options[health_choice]
        
        # Cuisine filter
        cuisine_options = [
            "any", "american", "asian", "chinese", "european", "french", 
            "greek", "indian", "italian", "japanese", "korean", "latin american",
            "mediterranean", "mexican", "middle eastern", "southern", "thai"
        ]
        cuisine_display = [c.title() if c != "any" else t["any"] for c in cuisine_options]
        cuisine_choice = st.selectbox(t["cuisine"], cuisine_display)
        cuisine_filter = cuisine_options[cuisine_display.index(cuisine_choice)]
        
        # Appliance filter
        appliance_options = {
            t["stovetop"]: "stovetop",
            t["oven_appliance"]: "oven",
            t["microwave"]: "microwave",
            t["air_fryer"]: "air_fryer",
            t["slow_cooker"]: "slow_cooker",
            t["grill"]: "grill",
            t["no_cook"]: "no_cook",
        }
        appliance_filters = st.multiselect(
            t["appliance"],
            list(appliance_options.keys())
        )
        selected_appliances = [appliance_options[a] for a in appliance_filters]
        
        # Search button
        search_clicked = st.button(t["find_recipes"], type="primary", use_container_width=True)
    
    with col_right:
        if search_clicked or st.session_state.get('last_search'):
            st.session_state.last_search = True
            
            # Find matching recipes - works with or without ingredients
            has_ingredients = len(st.session_state.selected_ingredients) > 0
            
            if has_ingredients:
                results = find_matching_recipes(
                    df,
                    st.session_state.selected_ingredients,
                    max_ingredients,
                    max_time,
                    difficulty,
                    dietary_filters,
                    health_level,
                    cuisine_filter,
                    selected_appliances
                )
            else:
                # No ingredients selected - show all recipes matching filters
                results = find_all_recipes(
                    df,
                    max_ingredients,
                    max_time,
                    difficulty,
                    dietary_filters,
                    health_level,
                    cuisine_filter,
                    selected_appliances
                )
            
            if len(results) == 0:
                st.warning(t["no_recipes"])
            else:
                st.success(t["found"].format(count=len(results)))
                
                # Add category to results
                results['display_category'] = results.apply(get_recipe_category, axis=1)
                
                # Sort results: group into time buckets then shuffle within each
                # bucket so the list feels varied, not just a wall of identical times.
                # Buckets: 0-15 min, 15-30, 30-45, 45-60, 60-90, 90+
                import numpy as np
                
                def time_bucket(t_val):
                    if pd.isna(t_val) or t_val <= 0:
                        return 6  # unknown goes last
                    if t_val <= 15:
                        return 0
                    if t_val <= 30:
                        return 1
                    if t_val <= 45:
                        return 2
                    if t_val <= 60:
                        return 3
                    if t_val <= 90:
                        return 4
                    return 5
                
                results['_time_bucket'] = results['total_time'].apply(time_bucket)
                
                # Shuffle within each category + time bucket so results vary
                results = (
                    results
                    .groupby(['display_category', '_time_bucket'], group_keys=False)
                    .apply(lambda g: g.sample(frac=1, random_state=None))
                )
                
                # Then sort by bucket so faster recipes still come first
                results = results.sort_values(
                    by=['_time_bucket'],
                    ascending=[True],
                    na_position='last'
                )
                
                # Show translation notice if Spanish selected
                if lang == 'es':
                    if TRANSLATION_AVAILABLE:
                        st.info(t["translation_note"])
                    else:
                        st.warning(t["translation_missing"])
                
                # Initialize expanded categories in session state
                if 'expanded_categories' not in st.session_state:
                    st.session_state.expanded_categories = set()
                
                # Build list of active categories for navigation
                active_categories = []
                for category in CATEGORY_ORDER:
                    cat_recipes = results[results['display_category'] == category]
                    if len(cat_recipes) > 0:
                        cat_display = CATEGORY_TRANSLATIONS.get(category, category) if lang == 'es' else category
                        active_categories.append((category, cat_display, len(cat_recipes)))
                
                # Show category navigation panel when any category is expanded
                has_expanded = len(st.session_state.expanded_categories) > 0
                
                if has_expanded:
                    st.markdown(f"<div class='category-nav'><div class='category-nav-title'>{t['browse_categories']}</div></div>", unsafe_allow_html=True)
                    nav_cols = st.columns(min(len(active_categories), 4))
                    for i, (cat_key, cat_display, cat_count) in enumerate(active_categories):
                        col_idx = i % min(len(active_categories), 4)
                        is_exp = cat_key in st.session_state.expanded_categories
                        label = f"{cat_display} ({cat_count})"
                        if is_exp:
                            label += " [open]"
                        if nav_cols[col_idx].button(label, key=f"nav_{cat_key}"):
                            if is_exp:
                                st.session_state.expanded_categories.discard(cat_key)
                            else:
                                st.session_state.expanded_categories.add(cat_key)
                            st.rerun()
                    
                    # Collapse all button
                    if st.button(t["collapse_all"], key="collapse_all_btn"):
                        st.session_state.expanded_categories = set()
                        st.rerun()
                    
                    st.divider()
                
                # Group recipes by category
                for category in CATEGORY_ORDER:
                    category_recipes = results[results['display_category'] == category]
                    
                    if len(category_recipes) == 0:
                        continue
                    
                    # Category header
                    category_display = CATEGORY_TRANSLATIONS.get(category, category) if lang == 'es' else category
                    
                    is_expanded = category in st.session_state.expanded_categories
                    
                    # Show first 5 recipes as preview
                    preview_count = min(5, len(category_recipes))
                    
                    st.markdown(f"<div class='category-header'>{category_display} ({len(category_recipes)})</div>", unsafe_allow_html=True)
                    
                    # Show preview recipes (first 5, sorted by time)
                    preview_recipes = category_recipes.head(preview_count)
                    
                    for idx, (_, recipe) in enumerate(preview_recipes.iterrows()):
                        _display_recipe_card(recipe, has_ingredients, lang, t, idx, category, "preview")
                    
                    # If there are more recipes, show expand/collapse button
                    if len(category_recipes) > preview_count:
                        remaining = len(category_recipes) - preview_count
                        
                        if is_expanded:
                            # Show all remaining recipes
                            remaining_recipes = category_recipes.iloc[preview_count:]
                            for idx, (_, recipe) in enumerate(remaining_recipes.iterrows()):
                                _display_recipe_card(recipe, has_ingredients, lang, t, idx, category, "full")
                            
                            # Styled show-less button
                            st.markdown("<div class='show-more-btn'>", unsafe_allow_html=True)
                            if st.button(t.get("show_less", "Show less"), key=f"collapse_{category}"):
                                st.session_state.expanded_categories.discard(category)
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            # Styled show-more button
                            st.markdown("<div class='show-more-btn'>", unsafe_allow_html=True)
                            if st.button(
                                t["more_in_category"].format(count=remaining) + " -- " + t.get("show_more", "Show more recipes"),
                                key=f"expand_{category}"
                            ):
                                st.session_state.expanded_categories.add(category)
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
