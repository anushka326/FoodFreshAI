/**
 * Food Analysis Service (Client-Side State Engine)
 * 
 * Prepares frontend components for future FastAPI & ML pipeline integration.
 */

import { FOOD_ASSETS } from '../assets/food/index.js';

export const analysisService = {
  /**
   * Analyze a single uploaded food photo
   * @param {File|string} imageSource - File object or image data URI
   * @param {object} pantryContext - { storage: 'countertop'|'fridge', daysInPantry: number, sampleHint: string }
   * @returns {Promise<object>} Analysis result structure
   */
  async analyzeSingleFood(imageSource, pantryContext = {}) {
    // Simulated processing delay
    await new Promise((res) => setTimeout(res, 800));

    const sample = (pantryContext.sampleHint || '').toLowerCase();
    const isFridge = pantryContext.storage === 'fridge';
    const days = Number(pantryContext.daysInPantry) || 0;

    if (sample === 'tomato' || (typeof imageSource === 'string' && imageSource.includes('tomato'))) {
      return {
        id: 'anls_' + Date.now(),
        foodName: 'Ripe Vine Tomato',
        cultivar: 'Cluster Vine • Solanum lycopersicum',
        scientificName: 'Solanum lycopersicum',
        confidence: 0.95,
        qualityScore: Math.max(40, 75 - days * 5),
        status: days > 3 ? 'Needs Attention' : 'Semi-Fresh (Softening)',
        statusCategory: days > 3 ? 'attention' : 'semi',
        qualityPeriod: days > 3 ? 'Consume within 24h' : '1–2 days left',
        storageSuggestion: isFridge ? 'Crisper Chill (may diminish aroma)' : 'Ambient Countertop (~21°C)',
        refrigeratedExtension: 'Can blend into sauce and freeze for 3 months',
        priorityRank: 'Priority 1 (Eat First)',
        visualObservation: 'Skin softening observed near stem shoulder. Slight epidermal yielding with high juiciness.',
        culinaryGuidance: {
          snacking: 'Best roasted or reduced into fresh pasta marinara before skin splits.',
          storageProtocol: 'Store stem-side down at room temperature to reduce moisture loss and delay fungal entry.',
          recipeIdea: 'Fresh Rustic Pomodoro with Basil',
        },
        ecoImpact: {
          potentialWasteAvoidanceDollar: 1.80,
          co2eSavingsKg: 0.4,
        },
        imageSrc: imageSource || FOOD_ASSETS.vineTomatoes,
        analyzedAt: new Date().toISOString(),
      };
    }

    if (sample === 'banana' || (typeof imageSource === 'string' && imageSource.includes('banana'))) {
      return {
        id: 'anls_' + Date.now(),
        foodName: 'Cavendish Banana',
        cultivar: 'Tropical • Musa acuminata',
        scientificName: 'Musa acuminata',
        confidence: 0.97,
        qualityScore: Math.max(35, 60 - days * 6),
        status: 'Needs Attention (High Sugar)',
        statusCategory: 'attention',
        qualityPeriod: 'Consume within 24h',
        storageSuggestion: 'Countertop Ambient (isolate from other fruit)',
        refrigeratedExtension: 'Peel and freeze in airtight container for up to 6 months',
        priorityRank: 'Priority 1 (Eat First)',
        visualObservation: 'Sugar spots actively expanding across peel crest. Flesh softening, starches transitioning rapidly to fructose.',
        culinaryGuidance: {
          snacking: 'Peak sweetness reached. Ideal for morning smoothies, oat bowls, or banana bread baking.',
          storageProtocol: 'Keep separated from citrus and apples to prevent ethylene compounding.',
          recipeIdea: 'Oat Skillet Banana Pancake',
        },
        ecoImpact: {
          potentialWasteAvoidanceDollar: 0.90,
          co2eSavingsKg: 0.25,
        },
        imageSrc: imageSource || FOOD_ASSETS.cavendishBananas,
        analyzedAt: new Date().toISOString(),
      };
    }

    if (sample === 'bowl' || sample === 'avocado' || (typeof imageSource === 'string' && imageSource.includes('avocado'))) {
      return {
        id: 'anls_' + Date.now(),
        foodName: 'Hass Avocado',
        cultivar: 'Peak Creaminess • Persea americana',
        scientificName: 'Persea americana',
        confidence: 0.93,
        qualityScore: Math.max(50, 88 - days * 4),
        status: 'Fresh (Peak Ripeness)',
        statusCategory: 'fresh',
        qualityPeriod: '2–3 days left',
        storageSuggestion: isFridge ? 'Crisper Drawer Chill (~4°C)' : 'Ambient Countertop',
        refrigeratedExtension: 'Chilling can preserve peak texture for an additional 4–5 days',
        priorityRank: 'Priority 2 (Can Wait)',
        visualObservation: 'Yields slightly to gentle thumb pressure. Clean stem cap with vibrant green under-button.',
        culinaryGuidance: {
          snacking: 'Buttery texture makes it ideal for slicing over warm sourdough, mashing for guacamole, or dicing into grain bowls.',
          storageProtocol: 'If cut in half, keep the pit in place and brush surface with lemon juice or olive oil to slow enzymatic browning.',
          recipeIdea: 'Artisan Avocado Toast with Flaky Salt',
        },
        ecoImpact: {
          potentialWasteAvoidanceDollar: 2.20,
          co2eSavingsKg: 0.5,
        },
        imageSrc: imageSource || FOOD_ASSETS.countertopBowl,
        analyzedAt: new Date().toISOString(),
      };
    }

    // Default: Honeycrisp Apple or Custom Uploaded Produce
    return {
      id: 'anls_' + Date.now(),
      foodName: sample === 'apple' ? 'Honeycrisp Apple' : 'Fresh Kitchen Produce',
      cultivar: sample === 'apple' ? 'Orchard Fresh • Malus domestica' : 'Countertop Fresh Harvest',
      scientificName: 'Malus domestica',
      confidence: 0.96,
      qualityScore: Math.max(55, 92 - days * 3),
      status: 'Fresh (Grade A)',
      statusCategory: 'fresh',
      qualityPeriod: `${Math.max(2, 5 - days)} days left`,
      storageSuggestion: isFridge ? 'Crisper Chill (~4°C / 39°F)' : 'Ambient Countertop (~21°C / 70°F)',
      refrigeratedExtension: 'Can extend to 2+ weeks if refrigerated in a perforated bag',
      priorityRank: 'Priority 3 (Can Wait)',
      visualObservation: 'Tight cellular firmness, clean skin pigmentation, and intact epidermal tension.',
      culinaryGuidance: {
        snacking: 'Crisp cell structure makes it ideal for raw snacking with almond butter, slicing into fresh salads, or packing into lunchboxes.',
        storageProtocol: 'Keep separated from delicate greens. Apples naturally emit ethylene gas which can hasten aging in adjacent leafy greens.',
        recipeIdea: 'Cinnamon Spiced Baked Apple Slices',
      },
      ecoImpact: {
        potentialWasteAvoidanceDollar: 1.40,
        co2eSavingsKg: 0.3,
      },
      imageSrc: imageSource || FOOD_ASSETS.honeycrispAppleCut,
      analyzedAt: new Date().toISOString(),
    };
  },

  /**
   * Analyze multiple food items for comparison and Eat First prioritization
   * @param {Array<File|string>} items 
   * @returns {Promise<Array<object>>} Ranked list of foods
   */
  async compareMultipleFoods(items = []) {
    await new Promise((res) => setTimeout(res, 900));

    return [
      {
        rank: 1,
        priorityLabel: 'Eat First',
        badgeColor: 'tertiary',
        name: 'Ripe Vine Tomato',
        cultivar: 'Cluster Vine • Solanum lycopersicum',
        estimatedWindow: '1–2 days',
        status: 'Semi-Fresh (Softening)',
        statusCategory: 'semi',
        qualityScore: 68,
        observation: 'Skin softening observed near stem shoulder. Highly vulnerable to skin splitting.',
        recommendation: 'Best for roasting, quick pasta sauce, or fresh salad today.',
        imageSrc: FOOD_ASSETS.vineTomatoes,
      },
      {
        rank: 2,
        priorityLabel: 'Next in Line',
        badgeColor: 'warning',
        name: 'Cavendish Banana',
        cultivar: 'Tropical • High Sugar Spotting',
        estimatedWindow: 'Consume within 24h',
        status: 'Needs Attention',
        statusCategory: 'attention',
        qualityScore: 50,
        observation: 'Sugar spotting starting on crest. Excellent sweetness, near peak flavor.',
        recommendation: 'Ideal for banana bread, morning smoothies, or oat skillet bake.',
        imageSrc: FOOD_ASSETS.cavendishBananas,
      },
      {
        rank: 3,
        priorityLabel: 'Can Wait',
        badgeColor: 'success',
        name: 'Honeycrisp Apple',
        cultivar: 'Orchard Fresh • Malus domestica',
        estimatedWindow: '4–5 days left',
        status: 'Fresh',
        statusCategory: 'fresh',
        qualityScore: 92,
        observation: 'Dense cellular crunch intact. Safe for prolonged countertop or crisper storage.',
        recommendation: 'Can wait. Keep away from ethylene-emitting bananas.',
        imageSrc: FOOD_ASSETS.honeycrispAppleCut,
      },
    ];
  },
};

export default analysisService;
