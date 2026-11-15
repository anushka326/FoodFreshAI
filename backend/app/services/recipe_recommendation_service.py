"""
FoodFresh AI — Pantry-Aware Recipe Recommendation Service
Pure Python service (no FastAPI imports). Matches pantry items to a curated
recipe database and returns ranked recommendations by urgency and match score.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("foodfresh.recipe_recommendation")

# ---------------------------------------------------------------------------
# Recipe Database — 24 diverse recipes
# ---------------------------------------------------------------------------
RECIPE_DATABASE: List[Dict[str, Any]] = [
    {
        "id": "r001",
        "name": "Classic Tomato Omelette",
        "category": "quick",
        "prep_time_minutes": 10,
        "image_url": None,
        "image_emoji": "🍳",
        "reason_template": "You have {matched} on hand — perfect for a quick breakfast or light meal.",
        "required_ingredients": ["egg", "tomato", "onion"],
        "steps": [
            "Dice the tomato and onion into small pieces.",
            "Beat 2 eggs with a pinch of salt and pepper.",
            "Heat a non-stick pan over medium heat with a little oil or butter.",
            "Sauté the onion for 1 minute, then add tomato and cook 1 more minute.",
            "Pour in the egg mixture and cook until set, folding in half.",
            "Serve hot with toast or alone.",
        ],
    },
    {
        "id": "r002",
        "name": "Banana Yogurt Smoothie",
        "category": "quick",
        "prep_time_minutes": 5,
        "image_url": None,
        "image_emoji": "🥤",
        "reason_template": "Use up {matched} before they over-ripen in this creamy, no-cook smoothie.",
        "required_ingredients": ["banana", "yogurt", "milk"],
        "steps": [
            "Peel and slice the banana.",
            "Add banana, yogurt, and milk to a blender.",
            "Blend on high for 30 seconds until smooth.",
            "Pour into a glass and serve immediately.",
            "Optional: add a drizzle of honey or a pinch of cinnamon.",
        ],
    },
    {
        "id": "r003",
        "name": "Garlic Spinach Stir-Fry",
        "category": "quick",
        "prep_time_minutes": 10,
        "image_url": None,
        "image_emoji": "🥬",
        "reason_template": "Save {matched} from wilting with this 10-minute, iron-rich side dish.",
        "required_ingredients": ["spinach", "garlic", "onion"],
        "steps": [
            "Wash spinach leaves thoroughly and drain.",
            "Mince 3-4 cloves of garlic and slice the onion thinly.",
            "Heat 1 tbsp oil in a wok or pan over high heat.",
            "Add garlic and onion; stir-fry for 1 minute.",
            "Add spinach in batches, tossing continuously until wilted (2-3 min).",
            "Season with salt, pepper, and a splash of soy sauce. Serve immediately.",
        ],
    },
    {
        "id": "r004",
        "name": "Potato & Carrot Soup",
        "category": "best_match",
        "prep_time_minutes": 30,
        "image_url": None,
        "image_emoji": "🍲",
        "reason_template": "Warm up with a hearty soup using {matched} from your pantry.",
        "required_ingredients": ["potato", "carrot", "onion", "garlic"],
        "steps": [
            "Peel and cube 2 potatoes and 2 carrots; dice the onion and mince garlic.",
            "Heat 1 tbsp oil in a large pot; sauté onion and garlic until soft (3 min).",
            "Add potatoes and carrots; stir to coat.",
            "Pour in 4 cups of water or broth; bring to a boil.",
            "Reduce heat and simmer for 20 minutes until vegetables are tender.",
            "Season with salt and pepper. Blend half the soup for a creamy texture if desired.",
        ],
    },
    {
        "id": "r005",
        "name": "Chicken & Mushroom Rice Bowl",
        "category": "best_match",
        "prep_time_minutes": 35,
        "image_url": None,
        "image_emoji": "🍚",
        "reason_template": "A satisfying bowl featuring {matched} — a complete one-pot meal.",
        "required_ingredients": ["chicken", "mushroom", "rice", "garlic", "onion"],
        "steps": [
            "Cook 1 cup rice according to package instructions.",
            "Slice chicken breast into strips; slice mushrooms.",
            "In a pan, heat oil and sauté onion and garlic until golden.",
            "Add chicken strips; cook until white and sealed (5 min).",
            "Add mushrooms and cook a further 4 minutes.",
            "Season with soy sauce, salt, and pepper.",
            "Serve chicken and mushrooms over hot rice.",
        ],
    },
    {
        "id": "r006",
        "name": "Apple Cinnamon Oatmeal",
        "category": "quick",
        "prep_time_minutes": 10,
        "image_url": None,
        "image_emoji": "🍎",
        "reason_template": "Turn {matched} into a warm, nourishing breakfast in minutes.",
        "required_ingredients": ["apple", "milk"],
        "steps": [
            "Peel and dice one apple into small cubes.",
            "Bring 1 cup of milk to a gentle simmer in a saucepan.",
            "Stir in ½ cup rolled oats and diced apple.",
            "Cook 5 minutes, stirring occasionally, until oats are creamy.",
            "Add a pinch of cinnamon and a teaspoon of honey.",
            "Serve hot.",
        ],
    },
    {
        "id": "r007",
        "name": "Tomato Pasta Arrabbiata",
        "category": "best_match",
        "prep_time_minutes": 25,
        "image_url": None,
        "image_emoji": "🍝",
        "reason_template": "Use {matched} in a classic spicy Italian pasta sauce.",
        "required_ingredients": ["tomato", "pasta", "garlic", "onion"],
        "steps": [
            "Cook pasta in salted boiling water until al dente; drain and reserve ½ cup pasta water.",
            "Dice tomatoes; mince garlic; chop onion.",
            "Heat 2 tbsp olive oil in a pan; add garlic and a pinch of chili flakes, cook 1 min.",
            "Add onion and cook until translucent (3 min).",
            "Add tomatoes and simmer 10 minutes, stirring occasionally.",
            "Toss cooked pasta in the sauce, adding pasta water if needed.",
            "Season with salt and serve with fresh basil if available.",
        ],
    },
    {
        "id": "r008",
        "name": "Stuffed Bell Peppers",
        "category": "best_match",
        "prep_time_minutes": 40,
        "image_url": None,
        "image_emoji": "🫑",
        "reason_template": "Rescue {matched} with this colourful, filling baked dish.",
        "required_ingredients": ["bell pepper", "rice", "tomato", "onion"],
        "steps": [
            "Preheat oven to 180°C (350°F). Cook ½ cup rice until just done.",
            "Slice the tops off bell peppers and remove seeds.",
            "Sauté diced onion and tomato in a pan for 5 minutes; mix with cooked rice.",
            "Season filling with salt, pepper, and dried herbs.",
            "Stuff each pepper with the rice mixture and place in a baking dish.",
            "Add a splash of water to the dish; bake 25 minutes until peppers are tender.",
        ],
    },
    {
        "id": "r009",
        "name": "Cucumber Yogurt Salad (Raita)",
        "category": "quick",
        "cuisine": "Indian",
        "prep_time_minutes": 8,
        "image_url": None,
        "image_emoji": "🥗",
        "youtube_url": "https://www.youtube.com/results?search_query=cucumber+raita+recipe",
        "reason_template": "Cool down with a fresh {matched} salad — ready in under 10 minutes.",
        "required_ingredients": ["cucumber", "yogurt", "garlic"],
        "steps": [
            "Peel and grate or finely dice the cucumber; squeeze out excess water.",
            "In a bowl, combine cucumber with 1 cup plain yogurt.",
            "Grate or mince one clove of garlic; add to bowl.",
            "Season with salt, a pinch of cumin, and fresh mint if available.",
            "Stir well, refrigerate for 5 minutes, and serve chilled.",
        ],
    },
    {
        "id": "r010",
        "name": "Lemon Garlic Broccoli",
        "category": "quick",
        "prep_time_minutes": 12,
        "image_url": None,
        "image_emoji": "🥦",
        "reason_template": "A zingy side dish that uses {matched} before they lose crunch.",
        "required_ingredients": ["broccoli", "garlic", "lemon"],
        "steps": [
            "Cut broccoli into florets; mince 2 cloves of garlic.",
            "Blanch broccoli in salted boiling water for 2 minutes; drain.",
            "Heat 1 tbsp olive oil in a pan; add garlic and cook 30 seconds.",
            "Add broccoli and toss to coat; cook 2 more minutes.",
            "Squeeze the juice of half a lemon over the top.",
            "Season with salt and pepper; serve immediately.",
        ],
    },
    {
        "id": "r011",
        "name": "Corn & Spinach Frittata",
        "category": "best_match",
        "prep_time_minutes": 20,
        "image_url": None,
        "image_emoji": "🥚",
        "reason_template": "A protein-packed brunch featuring {matched} — oven-finished for a fluffy result.",
        "required_ingredients": ["egg", "corn", "spinach", "onion"],
        "steps": [
            "Preheat oven to 190°C (375°F).",
            "Whisk 4 eggs with salt and pepper in a bowl.",
            "In an oven-safe pan, sauté onion in oil 3 minutes; add corn and spinach, cook 2 min.",
            "Pour egg mixture over vegetables; cook on the stove until edges set (2 min).",
            "Transfer pan to oven and bake 8-10 minutes until the top is set and golden.",
            "Slice and serve directly from the pan.",
        ],
    },
    {
        "id": "r012",
        "name": "Chicken Vegetable Stir-Fry",
        "category": "best_match",
        "prep_time_minutes": 20,
        "image_url": None,
        "image_emoji": "🍗",
        "reason_template": "A high-protein stir-fry that makes the most of {matched}.",
        "required_ingredients": ["chicken", "broccoli", "carrot", "garlic", "onion"],
        "steps": [
            "Slice chicken breast thin; chop broccoli into small florets; julienne carrot.",
            "Mix 2 tbsp soy sauce, 1 tsp sesame oil, and 1 tsp cornstarch in a small bowl.",
            "Heat wok or large pan over high heat; add oil.",
            "Add chicken and stir-fry until cooked through (4-5 min); remove and set aside.",
            "In same pan, stir-fry onion, garlic, broccoli, and carrot for 3 minutes.",
            "Return chicken to pan; pour sauce over and toss everything for 1 minute.",
            "Serve over rice or noodles.",
        ],
    },
    {
        "id": "r013",
        "name": "French Toast",
        "category": "quick",
        "prep_time_minutes": 10,
        "image_url": None,
        "image_emoji": "🍞",
        "reason_template": "Transform {matched} into a golden, satisfying breakfast in 10 minutes.",
        "required_ingredients": ["bread", "egg", "milk"],
        "steps": [
            "Beat 2 eggs with 3 tbsp milk, a pinch of salt, and a pinch of cinnamon.",
            "Dip each bread slice in the egg mixture, ensuring both sides are coated.",
            "Heat butter in a non-stick pan over medium heat.",
            "Cook each slice 2-3 minutes per side until golden brown.",
            "Serve with honey, maple syrup, or fresh fruit.",
        ],
    },
    {
        "id": "r014",
        "name": "Tomato Egg Scramble",
        "category": "quick",
        "prep_time_minutes": 8,
        "image_url": None,
        "image_emoji": "🍳",
        "reason_template": "Whip up {matched} into a quick, nutritious scramble.",
        "required_ingredients": ["egg", "tomato"],
        "steps": [
            "Dice the tomato into small chunks.",
            "Beat 2-3 eggs with a pinch of salt.",
            "Heat oil in a pan; cook tomatoes for 1 minute.",
            "Pour in eggs and scramble gently until just set.",
            "Season with pepper and serve with bread.",
        ],
    },
    {
        "id": "r015",
        "name": "Banana Pancakes",
        "category": "quick",
        "prep_time_minutes": 15,
        "image_url": None,
        "image_emoji": "🥞",
        "reason_template": "Use overripe {matched} in these fluffy 3-ingredient pancakes.",
        "required_ingredients": ["banana", "egg", "milk"],
        "steps": [
            "Mash 1 ripe banana in a bowl until smooth.",
            "Beat in 2 eggs and 2 tbsp milk.",
            "Heat a non-stick pan over medium-low heat with a little butter.",
            "Pour small rounds of batter and cook 2 minutes until bubbles form.",
            "Flip and cook 1 more minute until golden.",
            "Serve with honey or fresh fruit.",
        ],
    },
    {
        "id": "r016",
        "name": "Mushroom Garlic Pasta",
        "category": "best_match",
        "prep_time_minutes": 20,
        "image_url": None,
        "image_emoji": "🍄",
        "reason_template": "A rich, earthy pasta that showcases {matched} at their best.",
        "required_ingredients": ["mushroom", "pasta", "garlic", "onion"],
        "steps": [
            "Cook pasta in salted water until al dente; reserve ½ cup pasta water before draining.",
            "Slice mushrooms; mince garlic; dice onion.",
            "Heat 2 tbsp butter or oil in a pan; sauté onion and garlic until soft.",
            "Add mushrooms and cook 5-6 minutes until golden.",
            "Toss in drained pasta and a splash of pasta water; mix well.",
            "Season with salt, pepper, and fresh parsley if available.",
        ],
    },
    {
        "id": "r017",
        "name": "Carrot Ginger Soup",
        "category": "use_soon",
        "prep_time_minutes": 25,
        "image_url": None,
        "image_emoji": "🥕",
        "reason_template": "A velvety, warming soup that makes the best of {matched} before they lose freshness.",
        "required_ingredients": ["carrot", "onion", "garlic"],
        "steps": [
            "Peel and chop 4 large carrots; dice onion; mince garlic.",
            "Heat 1 tbsp oil in a large pot; sauté onion and garlic 3 minutes.",
            "Add carrots and stir to coat; pour in 3 cups water or broth.",
            "Bring to boil, add a 1-inch piece of grated ginger, reduce and simmer 15 minutes.",
            "Blend until smooth using an immersion blender.",
            "Season with salt and pepper; serve with crusty bread.",
        ],
    },
    {
        "id": "r018",
        "name": "Corn Chowder",
        "category": "best_match",
        "prep_time_minutes": 30,
        "image_url": None,
        "image_emoji": "🌽",
        "reason_template": "A comforting chowder built around {matched} — filling and easy.",
        "required_ingredients": ["corn", "potato", "onion", "milk"],
        "steps": [
            "Dice potato into 1 cm cubes; dice onion; strip corn kernels from cob if fresh.",
            "In a large pot, sauté onion in butter until soft (3 min).",
            "Add potato and corn; pour in 2 cups water and bring to a boil.",
            "Reduce heat and simmer 15 minutes until potato is tender.",
            "Stir in 1 cup milk; simmer gently 5 more minutes (do not boil).",
            "Season with salt, pepper, and a pinch of paprika.",
        ],
    },
    {
        "id": "r019",
        "name": "Lemon Honey Spinach Salad",
        "category": "quick",
        "prep_time_minutes": 8,
        "image_url": None,
        "image_emoji": "🥗",
        "reason_template": "Dress up {matched} with a bright lemon honey vinaigrette.",
        "required_ingredients": ["spinach", "lemon", "cucumber"],
        "steps": [
            "Wash and dry spinach; slice cucumber into thin rounds.",
            "In a small bowl, whisk juice of 1 lemon, 1 tsp honey, 2 tbsp olive oil, salt, and pepper.",
            "Combine spinach and cucumber in a large bowl.",
            "Drizzle dressing over and toss gently.",
            "Serve immediately.",
        ],
    },
    {
        "id": "r020",
        "name": "Tomato Bread Bruschetta",
        "category": "use_soon",
        "prep_time_minutes": 10,
        "image_url": None,
        "image_emoji": "🥖",
        "reason_template": "Use up {matched} in this classic Italian appetiser before they go off.",
        "required_ingredients": ["tomato", "bread", "garlic"],
        "steps": [
            "Dice tomatoes finely; mince 1 clove of garlic.",
            "Mix tomatoes, garlic, a drizzle of olive oil, salt, and pepper.",
            "Toast or grill slices of bread until golden.",
            "Rub each slice lightly with a cut garlic clove.",
            "Spoon the tomato mixture on top and serve immediately.",
        ],
    },
    {
        "id": "r021",
        "name": "Tropical Sunshine Fruit Salad",
        "category": "quick",
        "prep_time_minutes": 10,
        "image_url": None,
        "image_emoji": "🥭",
        "reason_template": "Toss {matched} into a revitalising tropical fruit bowl.",
        "required_ingredients": ["mango", "banana", "orange"],
        "steps": [
            "Peel and dice mango and banana into bite-sized pieces.",
            "Peel and segment orange, removing seeds.",
            "Gently toss all prepared fruits together in a bowl.",
            "Drizzle with a squeeze of fresh lemon or honey if desired.",
            "Serve chilled.",
        ],
    },
    {
        "id": "r022",
        "name": "Cooling Melon Citrus Medley",
        "category": "quick",
        "prep_time_minutes": 10,
        "image_url": None,
        "image_emoji": "🍉",
        "reason_template": "Refresh your day with sweet, hydrating {matched}.",
        "required_ingredients": ["watermelon", "cantaloupe", "lemon"],
        "steps": [
            "Scoop or cube fresh watermelon and cantaloupe into a serving bowl.",
            "Squeeze fresh lemon juice over the fruit to balance the sweetness.",
            "Add fresh mint leaves if available.",
            "Toss gently and serve chilled.",
        ],
    },
    {
        "id": "r023",
        "name": "Creamy Mango Lassi / Smoothie",
        "category": "quick",
        "cuisine": "Indian",
        "prep_time_minutes": 5,
        "image_url": None,
        "image_emoji": "🥤",
        "youtube_url": "https://www.youtube.com/results?search_query=mango+lassi+authentic+recipe",
        "reason_template": "Blend your {matched} into a sweet, silky traditional beverage.",
        "required_ingredients": ["mango", "yogurt", "milk"],
        "steps": [
            "Peel and cube ripe mango.",
            "Add mango cubes, 1 cup yogurt, and ½ cup milk to blender.",
            "Blend on high until silky smooth.",
            "Add a pinch of cardamom or a teaspoon of sugar if desired.",
            "Pour into glasses and serve chilled.",
        ],
    },
    {
        "id": "r024",
        "name": "Pomegranate Citrus Salad",
        "category": "quick",
        "cuisine": "Global",
        "prep_time_minutes": 10,
        "image_url": None,
        "image_emoji": "🥗",
        "youtube_url": "https://www.youtube.com/results?search_query=pomegranate+citrus+salad+recipe",
        "reason_template": "Brighten your table with antioxidant-rich {matched}.",
        "required_ingredients": ["pomegranate", "orange", "cucumber"],
        "steps": [
            "Seed the pomegranate and segment the orange.",
            "Thinly slice cucumber into half-moons.",
            "Combine pomegranate arils, orange slices, and cucumber in a bowl.",
            "Lightly season with a dash of olive oil, salt, and pepper.",
            "Serve as a crisp, refreshing appetizer.",
        ],
    },
    {
        "id": "r025",
        "name": "Aloo Gobi Matar (Spiced Potato, Cauliflower & Peas)",
        "category": "best_match",
        "cuisine": "Indian",
        "prep_time_minutes": 25,
        "image_url": None,
        "image_emoji": "🥘",
        "youtube_url": "https://www.youtube.com/results?search_query=aloo+gobi+matar+recipe",
        "reason_template": "Turn {matched} into a beloved North Indian curry loaded with fragrant ground spices.",
        "required_ingredients": ["potato", "onion", "tomato", "garlic"],
        "steps": [
            "Heat 2 tbsp cooking or mustard oil in a pan; add 1 tsp cumin seeds and let them splutter.",
            "Add finely chopped onion, minced garlic, and grated ginger; sauté 3-4 minutes until golden.",
            "Add chopped tomatoes, ½ tsp turmeric, 1 tsp red chili powder, and 1 tbsp coriander powder; cook until oil glimmers on the edges.",
            "Add cubed potatoes, cauliflower florets, and green peas; toss thoroughly to coat in the rich masala.",
            "Cover with a lid and cook on low heat for 12-15 minutes, stirring occasionally until potatoes are fork-tender.",
            "Sprinkle garam masala and chopped fresh coriander. Serve hot with phulkas, roti, or steamed rice.",
        ],
    },
    {
        "id": "r026",
        "name": "Homestyle Palak Paneer / Palak Saag",
        "category": "best_match",
        "cuisine": "Indian",
        "prep_time_minutes": 25,
        "image_url": None,
        "image_emoji": "🥬",
        "youtube_url": "https://www.youtube.com/results?search_query=palak+paneer+dhabastyle+recipe",
        "reason_template": "Rescue {matched} by blending into a vibrant, iron-rich spiced Indian spinach gravy.",
        "required_ingredients": ["spinach", "tomato", "onion", "garlic"],
        "steps": [
            "Blanch fresh spinach in boiling salted water for 2 minutes, then plunge into ice water to preserve bright green vibrancy.",
            "Purée the blanched spinach in a blender until silky smooth.",
            "Heat 1 tbsp ghee or oil in a pan; add cumin seeds, chopped onions, and minced garlic; cook until aromatic.",
            "Add chopped tomatoes, turmeric, and garam masala; simmer until tomatoes break down completely.",
            "Pour in the spinach purée and simmer on low for 5 minutes. Stir in 2 tbsp milk or cream.",
            "Fold in paneer or tofu cubes and season with salt. Serve warm with garlic naan or jeera rice.",
        ],
    },
    {
        "id": "r027",
        "name": "Mumbai Street-Style Anda Bhurji",
        "category": "quick",
        "cuisine": "Indian",
        "prep_time_minutes": 10,
        "image_url": None,
        "image_emoji": "🍳",
        "youtube_url": "https://www.youtube.com/results?search_query=mumbai+street+style+anda+bhurji+recipe",
        "reason_template": "Scramble {matched} into spicy, buttery street-style scrambled eggs in under 10 minutes.",
        "required_ingredients": ["egg", "onion", "tomato", "garlic"],
        "steps": [
            "Finely dice onions, tomatoes, and green chilies; mince garlic.",
            "Melt 1.5 tbsp butter or oil in a pan; sauté onions and garlic until translucent (2 min).",
            "Add tomatoes, turmeric, pav bhaji masala or garam masala, and red chili powder; cook until soft.",
            "Whisk 3 eggs with a pinch of salt; pour directly into the bubbling masala.",
            "Scramble continuously on medium heat for 2-3 minutes until soft, fluffy curds form.",
            "Garnish with lots of chopped fresh coriander and a squeeze of fresh lemon. Serve with toasted pav or roti.",
        ],
    },
    {
        "id": "r028",
        "name": "Jeera Aloo (Cumin Spiced Potatoes)",
        "category": "quick",
        "cuisine": "Indian",
        "prep_time_minutes": 15,
        "image_url": None,
        "image_emoji": "🥔",
        "youtube_url": "https://www.youtube.com/results?search_query=jeera+aloo+recipe",
        "reason_template": "Toss {matched} with roasted cumin seeds and tangy amchur for a quick Indian staple.",
        "required_ingredients": ["potato", "garlic", "lemon"],
        "steps": [
            "Boil or steam potatoes until tender; peel and cut into bite-sized cubes.",
            "Heat 2 tbsp oil or ghee in a pan; add 1 tbsp whole cumin seeds (jeera) and let crackle until deeply aromatic.",
            "Add minced garlic, slit green chilies, ½ tsp turmeric, and salt.",
            "Tumble the potato cubes into the pan, tossing gently so every piece is coated in roasted cumin.",
            "Roast on medium heat for 5-6 minutes until edges turn delightfully crisp and golden.",
            "Finish with fresh lemon juice and chopped cilantro. Serve warm.",
        ],
    },
    {
        "id": "r029",
        "name": "Tomato Saar / Rasam (Spiced Tomato Pepper Broth)",
        "category": "quick",
        "cuisine": "Indian",
        "prep_time_minutes": 15,
        "image_url": None,
        "image_emoji": "🥣",
        "youtube_url": "https://www.youtube.com/results?search_query=tomato+rasam+recipe",
        "reason_template": "Simmer ripe {matched} into a tangy, immune-boosting South/West Indian tomato broth.",
        "required_ingredients": ["tomato", "garlic"],
        "steps": [
            "Boil 3 ripe tomatoes until skins crack, peel, and crush or blend into a smooth pulp with 1 cup water.",
            "In a saucepan, heat 1 tsp ghee or coconut oil; add mustard seeds, cumin, crushed garlic cloves, and curry leaves.",
            "Once seeds splutter, pour in the tomato purée, adding black pepper powder, turmeric, and salt.",
            "Simmer gently for 5 minutes until flavors meld into a fragrant, zesty broth.",
            "Finish with a squeeze of fresh lemon and fresh cilantro.",
            "Sip as a comforting hot soup or pour over warm rice.",
        ],
    },
    {
        "id": "r030",
        "name": "Dhaba-Style Dal Tadka",
        "category": "best_match",
        "cuisine": "Indian",
        "prep_time_minutes": 25,
        "image_url": None,
        "image_emoji": "🍲",
        "youtube_url": "https://www.youtube.com/results?search_query=dal+tadka+dhaba+style+recipe",
        "reason_template": "Temper {matched} into a golden, aromatic lentil curry with sizzling garlic ghee tadka.",
        "required_ingredients": ["tomato", "onion", "garlic"],
        "steps": [
            "Boil yellow lentils (toor or moong dal) with turmeric and salt until creamy and soft.",
            "In a skillet, heat 2 tbsp ghee; add cumin seeds, dried red chilies, and generous minced garlic.",
            "Add finely chopped onions and sauté until golden brown (3 min).",
            "Add chopped tomatoes and cook until soft and oil begins to separate.",
            "Pour the sizzling tadka over the cooked dal; simmer together for 4-5 minutes.",
            "Garnish with chopped cilantro and serve with hot basmati rice or chapati.",
        ],
    },
    {
        "id": "r031",
        "name": "Kanda Batata Poha (Savory Flaked Rice with Potatoes)",
        "category": "quick",
        "cuisine": "Indian",
        "prep_time_minutes": 15,
        "image_url": None,
        "image_emoji": "🍛",
        "youtube_url": "https://www.youtube.com/results?search_query=kanda+batata+poha+recipe",
        "reason_template": "Combine {matched} into the classic Maharashtrian breakfast with lemon and fresh herbs.",
        "required_ingredients": ["potato", "onion", "lemon"],
        "steps": [
            "Rinse 2 cups thick flattened rice (poha) gently in a colander; drain completely and rest 5 minutes.",
            "Heat 1.5 tbsp oil in a pan; add mustard seeds, cumin seeds, curry leaves, and a pinch of hing.",
            "Add finely diced potatoes and cook 3-4 minutes until tender and crisp.",
            "Add sliced onions and green chilies; sauté until soft and lightly caramelized.",
            "Stir in ½ tsp turmeric powder and salt, then gently fold in the softened poha.",
            "Cover on low heat for 2 minutes to steam. Garnish with chopped coriander, roasted peanuts, and lemon juice.",
        ],
    },
    {
        "id": "r032",
        "name": "Gajar Ka Halwa (Slow-Simmered Carrot Cardamom Pudding)",
        "category": "best_match",
        "cuisine": "Indian",
        "prep_time_minutes": 35,
        "image_url": None,
        "image_emoji": "🥕",
        "youtube_url": "https://www.youtube.com/results?search_query=gajar+ka+halwa+recipe",
        "reason_template": "Celebrate your fresh {matched} by slow-cooking into traditional Indian carrot halwa.",
        "required_ingredients": ["carrot", "milk"],
        "steps": [
            "Grate 4-5 fresh carrots coarsely.",
            "Heat 2 tbsp ghee in a heavy kadai; add grated carrots and sauté 5 minutes until moisture reduces.",
            "Pour in 2 cups milk; simmer over medium-low heat stirring occasionally until milk fully reduces (about 20 min).",
            "Add 3 tbsp sugar or jaggery and 1 tbsp ghee; cook 5 minutes until glossy and thick.",
            "Stir in ½ tsp freshly ground cardamom powder and toasted sliced almonds or cashews.",
            "Serve warm as a comforting royal Indian dessert.",
        ],
    },
    {
        "id": "r033",
        "name": "Makai Palak (Sweet Corn in Spiced Spinach Gravy)",
        "category": "best_match",
        "cuisine": "Indian",
        "prep_time_minutes": 25,
        "image_url": None,
        "image_emoji": "🌽",
        "youtube_url": "https://www.youtube.com/results?search_query=makai+palak+curry+recipe",
        "reason_template": "Pair crunchy sweet {matched} with velvety spinach in this North Indian restaurant specialty.",
        "required_ingredients": ["corn", "spinach", "onion", "garlic", "milk"],
        "steps": [
            "Blanch spinach leaves for 2 minutes and purée into a smooth paste.",
            "Steam sweet corn kernels until juicy and tender.",
            "Heat 1 tbsp butter or oil in a pan; sauté cumin, chopped onions, and minced garlic until light brown.",
            "Add the spinach purée, corn kernels, garam masala, turmeric, and salt; simmer 4 minutes.",
            "Stir in 3 tbsp milk or fresh cream for a rich, velvety texture.",
            "Serve hot with butter naan, paratha, or jeera rice.",
        ],
    },
    {
        "id": "r034",
        "name": "Traditional Aamras (Chilled Cardamom Mango Purée)",
        "category": "quick",
        "cuisine": "Indian",
        "prep_time_minutes": 10,
        "image_url": None,
        "image_emoji": "🥭",
        "youtube_url": "https://www.youtube.com/results?search_query=aamras+traditional+recipe",
        "reason_template": "Extract pure summer joy from ripe {matched} in this authentic chilled Indian mango pulp.",
        "required_ingredients": ["mango", "milk"],
        "steps": [
            "Wash, peel, and cube sweet ripe mangoes (Alphonso, Kesar, or Dasheri).",
            "Add mango cubes to a blender with 3 tbsp chilled milk and 1 tbsp sugar or honey if needed.",
            "Add a fragrant pinch of ground cardamom and a few strands of saffron.",
            "Blend until velvety and thick (do not over-dilute).",
            "Chill in the refrigerator for 20 minutes.",
            "Serve cold with hot fried puris or enjoy with a spoon.",
        ],
    },
    {
        "id": "r035",
        "name": "Besan Shimla Mirch (Spiced Bell Peppers with Gram Flour)",
        "category": "quick",
        "cuisine": "Indian",
        "prep_time_minutes": 15,
        "image_url": None,
        "image_emoji": "🫑",
        "youtube_url": "https://www.youtube.com/results?search_query=besan+shimla+mirch+ki+sabzi",
        "reason_template": "Coat crisp {matched} in roasted spiced besan for a flavorful dry Indian side dish.",
        "required_ingredients": ["bell pepper", "onion", "garlic"],
        "steps": [
            "Cut bell peppers (capsicum) into 1-inch squares; slice onions.",
            "Dry roast 3 tbsp gram flour (besan) in a pan on low heat until nutty and fragrant (3 min); set aside.",
            "Heat 2 tbsp oil in the pan; add mustard seeds, cumin seeds, and minced garlic.",
            "Add onions and bell peppers; sauté on medium-high heat for 4 minutes until crisp-tender.",
            "Add turmeric, red chili powder, coriander powder, amchur (dry mango powder), and salt.",
            "Sprinkle the roasted besan over the peppers, add 1 tbsp water, and cover for 2 minutes to let the spiced flour coat every piece. Serve with phulkas.",
        ],
    },
    {
        "id": "r036",
        "name": "Dhaba-Style Mushroom Masala",
        "category": "best_match",
        "cuisine": "Indian",
        "prep_time_minutes": 25,
        "image_url": None,
        "image_emoji": "🍄",
        "youtube_url": "https://www.youtube.com/results?search_query=mushroom+masala+dhaba+style+recipe",
        "reason_template": "Simmer earthy {matched} in a robust onion-tomato masala with crushed fenugreek leaves.",
        "required_ingredients": ["mushroom", "onion", "tomato", "garlic"],
        "steps": [
            "Clean and slice mushrooms into thick halves.",
            "Heat 2 tbsp oil in a pan; sauté chopped onions and garlic paste until golden brown.",
            "Add puréed tomatoes, turmeric, coriander powder, cumin, and Kashmiri chili powder; cook until oil releases.",
            "Add the mushrooms and stir-fry on high heat for 3 minutes as they release their savory juices.",
            "Add ½ cup water, cover and simmer for 6-8 minutes until the gravy thickens.",
            "Crush roasted kasuri methi (fenugreek leaves) between your palms and stir in with garam masala. Serve hot with roti or rice.",
        ],
    },
    {
        "id": "r037",
        "name": "Kachumber Salad (Crunchy Indian Chaat Medley)",
        "category": "quick",
        "cuisine": "Indian",
        "prep_time_minutes": 8,
        "image_url": None,
        "image_emoji": "🥗",
        "youtube_url": "https://www.youtube.com/results?search_query=kachumber+salad+recipe",
        "reason_template": "Chop {matched} into a refreshing, crunchy Indian salad tossed with chaat masala and lemon.",
        "required_ingredients": ["cucumber", "tomato", "onion", "lemon"],
        "steps": [
            "Finely dice cucumber, firm tomatoes, and red onion into uniform small cubes.",
            "Transfer all chopped vegetables to a bowl.",
            "Add finely chopped green chili and a handful of fresh coriander.",
            "Season with chaat masala (½ tsp), roasted cumin powder, black salt, and freshly squeezed lemon juice.",
            "Toss lightly right before serving to maintain crisp freshness.",
            "Serve alongside curries, pulao, or biryani.",
        ],
    },
    {
        "id": "r038",
        "name": "Apple Cardamom Kheer (Warm Apple Milk Pudding)",
        "category": "quick",
        "cuisine": "Indian",
        "prep_time_minutes": 20,
        "image_url": None,
        "image_emoji": "🍎",
        "youtube_url": "https://www.youtube.com/results?search_query=apple+kheer+recipe",
        "reason_template": "Turn crisp {matched} into a velvety, cardamom-scented festive milk pudding.",
        "required_ingredients": ["apple", "milk"],
        "steps": [
            "Simmer 2 cups milk in a heavy saucepan for 10 minutes until slightly thickened.",
            "Peel and grate 2 sweet apples.",
            "In a separate small pan, heat 1 tsp ghee, add grated apples and sauté with 2 tbsp sugar for 4-5 minutes until tender and moisture dries (this prevents milk from separating).",
            "Allow sautéed apples to cool slightly, then stir into the warm reduced milk.",
            "Season with freshly ground green cardamom powder and slivered pistachios.",
            "Serve warm or chilled as a nutritious, comforting dessert.",
        ],
    },
    {
        "id": "r039",
        "name": "Tariwali Egg Curry (Spiced Tomato Onion Gravy)",
        "category": "best_match",
        "cuisine": "Indian",
        "prep_time_minutes": 25,
        "image_url": None,
        "image_emoji": "🥚",
        "youtube_url": "https://www.youtube.com/results?search_query=tariwali+anda+curry+recipe",
        "reason_template": "Nestle {matched} in a homestyle spiced onion-tomato gravy with fried boiled eggs.",
        "required_ingredients": ["egg", "onion", "tomato", "garlic"],
        "steps": [
            "Hard boil eggs, peel them, and make shallow slits on the sides.",
            "Heat 1 tbsp oil in a pan with a pinch of turmeric and chili; shallow-fry eggs for 2 minutes until golden blistered, then set aside.",
            "In the same pan, sauté finely chopped onions and garlic paste until golden brown.",
            "Add tomato purée, ginger, cumin, coriander, and garam masala; cook until oil separates.",
            "Add 1 cup water, bring to a gentle boil, then lower the fried eggs into the bubbling gravy.",
            "Simmer for 5 minutes. Garnish with chopped fresh coriander and serve with steamed rice or paratha.",
        ],
    },
    {
        "id": "r040",
        "name": "Vegetable Pulao (Fragrant One-Pot Spiced Basmati Rice)",
        "category": "best_match",
        "cuisine": "Indian",
        "prep_time_minutes": 25,
        "image_url": None,
        "image_emoji": "🍚",
        "youtube_url": "https://www.youtube.com/results?search_query=veg+pulao+recipe",
        "reason_template": "Infuse basmati rice with whole spices, ghee, and colorful {matched} in one pot.",
        "required_ingredients": ["rice", "carrot", "potato", "onion", "garlic"],
        "steps": [
            "Rinse and soak 1 cup basmati rice for 20 minutes; drain.",
            "Heat 2 tbsp ghee or oil in a pot; add whole spices (bay leaf, cinnamon, cloves, cardamom).",
            "Sauté sliced onions and garlic paste until golden and aromatic.",
            "Add diced carrots, potatoes, and any other available pantry vegetables (peas, corn).",
            "Add the soaked rice and gently sauté for 1 minute to coat each grain in ghee.",
            "Pour in 2 cups warm water and salt to taste; bring to a boil, then cover and cook on lowest heat for 12 minutes until water is absorbed.",
            "Rest 5 minutes, fluff with a fork, and serve hot with raita.",
        ],
    },
]


# ---------------------------------------------------------------------------
# Ingredient normalisation and flexible matching helpers
# ---------------------------------------------------------------------------
import re

CANONICAL_INGREDIENTS: List[str] = [
    "tomato", "egg", "onion", "banana", "yogurt", "milk", "spinach", "garlic",
    "potato", "carrot", "chicken", "mushroom", "rice", "apple", "pasta",
    "bell pepper", "cucumber", "broccoli", "lemon", "corn", "bread",
    "mango", "orange", "watermelon", "cantaloupe", "pomegranate",
]

_INGREDIENT_ALIASES: Dict[str, str] = {
    "eggs": "egg",
    "tomatoes": "tomato",
    "apples": "apple",
    "bananas": "banana",
    "onions": "onion",
    "potatoes": "potato",
    "carrots": "carrot",
    "lemons": "lemon",
    "mushrooms": "mushroom",
    "bell peppers": "bell pepper",
    "peppers": "bell pepper",
    "capsicum": "bell pepper",
    "capsicums": "bell pepper",
    "broccolis": "broccoli",
    "corns": "corn",
    "chickens": "chicken",
    "poultry": "chicken",
    "yoghurt": "yogurt",
    "curd": "yogurt",
    "dahi": "yogurt",
    "breads": "bread",
    "toast": "bread",
    "loaf": "bread",
    "milks": "milk",
    "spinaches": "spinach",
    "cucumbers": "cucumber",
    "garlics": "garlic",
    "pastas": "pasta",
    "noodles": "pasta",
    "spaghetti": "pasta",
    "macaroni": "pasta",
    "penne": "pasta",
    "rices": "rice",
    "mangoes": "mango",
    "oranges": "orange",
    "watermelons": "watermelon",
    "cantaloupes": "cantaloupe",
    "pomegranates": "pomegranate",
    "limes": "lemon",
    "lime": "lemon",
    "maize": "corn",
}

_URGENT_PRIORITIES: Set[str] = {"VERY_HIGH", "HIGH"}


def match_food_to_ingredient(food_name: str) -> Optional[str]:
    """
    Given a food name stored in the user's pantry (e.g. 'Ripe Tomato', 'Fresh Apple',
    'Baby Spinach', 'Bell Pepper (Green)', 'Capsicum', 'Chicken Breast', 'Sourdough Bread'),
    resolves it to one of the canonical recipe ingredients. Returns None if unmapped.
    """
    if not food_name or not str(food_name).strip():
        return None

    clean = re.sub(r"[^a-z0-9\s]", " ", str(food_name).strip().lower())
    words = clean.split()
    if not words:
        return None

    # 1. Multi-word canonical match (e.g. 'bell pepper' inside 'green bell pepper')
    for c in CANONICAL_INGREDIENTS:
        if " " in c and c in clean:
            return c

    # 2. Exact alias match for full phrase
    if clean in _INGREDIENT_ALIASES:
        return _INGREDIENT_ALIASES[clean]

    # 3. Word-level alias match
    for word in words:
        if word in _INGREDIENT_ALIASES:
            return _INGREDIENT_ALIASES[word]

    # 4. Single-word canonical match against individual words or common inflections
    for c in CANONICAL_INGREDIENTS:
        if " " not in c:
            for w in words:
                if w == c or w == f"{c}s" or w == f"{c}es":
                    return c
                if c.endswith("y") and w == f"{c[:-1]}ies":
                    return c

    return None


# ---------------------------------------------------------------------------
# Core recommendation logic
# ---------------------------------------------------------------------------

def generate_recipe_recommendations(pantry_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Given a list of enriched pantry items directly from the authenticated user's database,
    generate dynamic recipe recommendations.

    - Uses actual user pantry records (foodName, remainingDays, eatFirstPriority, quantity, etc.)
    - Strictly returns 0 matched recipes when pantry is empty (no dummy or fallback recipes)
    - Prioritizes recipes using ingredients that are nearing expiry or marked Eat First HIGH/VERY_HIGH
    """
    total_items = len(pantry_items) if pantry_items else 0

    if not pantry_items:
        return {
            "best_match": [],
            "use_soon": [],
            "quick": [],
            "all": [],
            "pantry_summary": {
                "total_items": 0,
                "expiring_soon_count": 0,
                "matched_recipes_count": 0,
            },
        }

    # --- Index user's actual pantry items by mapped canonical ingredient ---
    # Map: canonical_ing -> list of pantry item records
    pantry_ingredient_map: Dict[str, List[Dict[str, Any]]] = {}
    expiring_ingredients: Set[str] = set()

    for item in pantry_items:
        raw_name = item.get("foodName") or item.get("food_name") or ""
        matched_ing = match_food_to_ingredient(raw_name)
        if not matched_ing:
            continue

        remaining = item.get("remainingDays")
        priority = item.get("eatFirstPriority") or "NORMAL"
        is_urgent = (
            (remaining is not None and remaining <= 3)
            or priority in _URGENT_PRIORITIES
        )

        metadata = item.get("metadata") or {}
        storage_ctx = metadata.get("storageContext") or {}
        qty = item.get("quantity") or metadata.get("quantity") or storage_ctx.get("quantity")

        cleaned_record = {
            "id": item.get("id"),
            "foodName": raw_name,
            "ingredient": matched_ing,
            "remainingDays": remaining,
            "qualityPeriod": item.get("qualityPeriod"),
            "eatFirstPriority": priority,
            "eatFirstReason": item.get("eatFirstReason") or "",
            "freshnessState": item.get("freshnessState") or item.get("status") or "Fresh",
            "quantity": qty,
            "imageSrc": item.get("imageSrc"),
            "storageEnvironment": item.get("storageEnvironment"),
            "isUrgent": is_urgent,
        }

        pantry_ingredient_map.setdefault(matched_ing, []).append(cleaned_record)
        if is_urgent:
            expiring_ingredients.add(matched_ing)

    # Sort items per ingredient so the most urgent item is selected first
    for ing, items in pantry_ingredient_map.items():
        items.sort(
            key=lambda x: (
                0 if x["isUrgent"] else 1,
                x["remainingDays"] if x["remainingDays"] is not None else 999,
            )
        )

    available_canonical_set = set(pantry_ingredient_map.keys())
    expiring_soon_count = len(expiring_ingredients)

    # --- Score each recipe ---
    matched_recipes: List[Dict[str, Any]] = []

    for recipe in RECIPE_DATABASE:
        req = set(recipe["required_ingredients"])
        available_keys = req & available_canonical_set
        missing_keys = req - available_canonical_set

        if not available_keys:
            continue  # 0 user ingredients match → skip

        match_score_raw = len(available_keys) / len(req)
        if match_score_raw < 0.30:
            continue  # below 30% threshold

        match_score = int(round(match_score_raw * 100))

        # Collect the user's actual pantry item objects for matched ingredients
        matched_user_items: List[Dict[str, Any]] = []
        user_food_names: List[str] = []
        has_urgent_item = False

        for k in sorted(available_keys):
            best_pantry_item = pantry_ingredient_map[k][0]
            matched_user_items.append(best_pantry_item)
            user_food_names.append(best_pantry_item["foodName"])
            if best_pantry_item["isUrgent"]:
                has_urgent_item = True

        # Determine effective category
        effective_category = recipe["category"]
        if has_urgent_item:
            effective_category = "use_soon"

        # Build dynamic, personalized reason referencing actual food names & expiry info
        if has_urgent_item:
            urgent_desc = ", ".join(
                f"{p['foodName']} ("
                + (f"{p['remainingDays']}d left" if p['remainingDays'] is not None else "expiring soon")
                + (f" • {p['eatFirstPriority']} priority" if p['eatFirstPriority'] and p['eatFirstPriority'] != 'NORMAL' else "")
                + ")"
                for p in matched_user_items
                if p["isUrgent"]
            )
            reason = f"High Priority: Helps you consume {urgent_desc} before quality degrades."
        else:
            actual_names_str = ", ".join(user_food_names)
            reason = recipe["reason_template"].format(matched=actual_names_str)

        result = {
            "id": recipe["id"],
            "name": recipe["name"],
            "category": effective_category,
            "cuisine": recipe.get("cuisine", "Global"),
            "prep_time_minutes": recipe["prep_time_minutes"],
            "steps": recipe["steps"],
            "required_ingredients": recipe["required_ingredients"],
            "available_ingredients": user_food_names,
            "missing_ingredients": sorted(missing_keys),
            "matched_pantry_items": matched_user_items,
            "match_score": match_score,
            "reason": reason,
            "image_emoji": recipe["image_emoji"],
            "youtube_url": recipe.get("youtube_url") or f"https://www.youtube.com/results?search_query={recipe['name'].lower().replace(' ', '+')}+recipe",
            "expiry_urgency": has_urgent_item,
        }
        matched_recipes.append(result)

    # --- Sort all matched recipes ---
    # Priority: use_soon (expiry_urgency=True) first → highest score → shortest prep time
    def sort_key(r: Dict[str, Any]):
        urgency_rank = 0 if r["expiry_urgency"] else 1
        category_rank = {"use_soon": 0, "best_match": 1, "quick": 2}.get(r["category"], 3)
        return (urgency_rank, category_rank, -r["match_score"], r["prep_time_minutes"])

    matched_recipes.sort(key=sort_key)

    # --- Group by category & cuisine ---
    best_match = [r for r in matched_recipes if r["category"] == "best_match"]
    use_soon = [r for r in matched_recipes if r["category"] == "use_soon"]
    quick = [r for r in matched_recipes if r["category"] == "quick"]
    indian = [r for r in matched_recipes if r.get("cuisine") == "Indian"]

    logger.info(
        "Recipe recommendations generated from %d pantry items: total_matches=%d, use_soon=%d, best_match=%d, quick=%d, indian=%d",
        total_items,
        len(matched_recipes),
        len(use_soon),
        len(best_match),
        len(quick),
        len(indian),
    )

    return {
        "best_match": best_match,
        "use_soon": use_soon,
        "quick": quick,
        "indian": indian,
        "all": matched_recipes,
        "pantry_summary": {
            "total_items": total_items,
            "expiring_soon_count": expiring_soon_count,
            "matched_recipes_count": len(matched_recipes),
            "indian_recipes_count": len(indian),
        },
    }
