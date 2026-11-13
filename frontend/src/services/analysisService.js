/**
 * Food Analysis Service (FoodFresh AI Inference & Result Interface)
 *
 * Connects the Analyze Food frontend to the real trained EfficientNet-B0
 * Food Recognition model endpoint (POST /api/food-recognition/predict).
 *
 * Conforms to the FoodFresh AI pipeline architecture:
 * - Real food recognition from trained checkpoint (source: 'ml', model: 'EfficientNet-B0').
 * - Freshness, Shelf-Life, and Priority remain in explicit neutral pending states ('not analyzed yet').
 * - No fake or hardcoded mock scores.
 */

import { ENDPOINTS } from '../config/api.js';

/**
 * Converts a data URL, object URL, or file reference to a File object for multipart upload.
 * @param {string|File|Blob} imageSource
 * @param {string} [filename='food_image.jpg']
 * @returns {Promise<File>}
 */
async function toUploadFile(imageSource, filename = 'food_image.jpg') {
  if (imageSource instanceof File) {
    return imageSource;
  }
  if (imageSource instanceof Blob) {
    return new File([imageSource], filename, { type: imageSource.type || 'image/jpeg' });
  }
  if (typeof imageSource === 'string') {
    // Handle Data URL or Blob URL or relative asset URL
    try {
      const response = await fetch(imageSource);
      const blob = await response.blob();
      const mime = blob.type || 'image/jpeg';
      const ext = mime.includes('png') ? 'png' : 'jpg';
      return new File([blob], `food_image.${ext}`, { type: mime });
    } catch (err) {
      throw new Error('Could not process the selected image for upload.');
    }
  }
  throw new Error('Please select a valid food image.');
}

export const analysisService = {
  /**
   * Create an initial blank FoodAnalysisResult structure
   * @returns {object}
   */
  createInitialResult() {
    return {
      id: '',
      detectedFood: null,
      recognitionConfidence: null,
      topPredictions: null,
      freshness: {
        label: null,
        confidence: null,
      },
      shelfLife: {
        minDays: null,
        maxDays: null,
      },
      eatFirstPriority: null,
      analysisStatus: 'not_analyzed',
      source: 'none',
      model: 'EfficientNet-B0',
      modelVersion: 'v2',
      storageContext: null,
      imageSrc: null,
      analyzedAt: '',
      message: '',
    };
  },

  /**
   * Analyze a single food photo using the trained Food Recognition model
   * @param {File|string} imageSource - User-uploaded image data URI or File
   * @param {object} pantryContext - { storage: 'countertop'|'fridge', daysInPantry: number }
   * @returns {Promise<object>} FoodAnalysisResult
   */
  async analyzeSingleFood(imageSource, pantryContext = {}) {
    if (!imageSource) {
      throw new Error('Please upload or capture a food image first.');
    }

    // Convert source to File
    const file = await toUploadFile(imageSource);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('storage_type', pantryContext.storage || 'countertop');
    formData.append('days_stored', String(pantryContext.daysInPantry != null ? pantryContext.daysInPantry : 0));

    let response;
    try {
      response = await fetch(ENDPOINTS.FOOD_RECOGNITION, {
        method: 'POST',
        body: formData,
      });
    } catch (networkErr) {
      throw new Error('Food analysis service is currently unavailable. Please try again.');
    }

    // Handle HTTP non-200 responses
    if (!response.ok) {
      let errPayload = null;
      try {
        errPayload = await response.json();
      } catch {
        // Ignored
      }

      if (response.status === 503 || errPayload?.status === 'model_unavailable') {
        throw new Error('Food recognition model is currently unavailable.');
      } else if (response.status === 400 || errPayload?.status === 'invalid_image') {
        throw new Error(errPayload?.message || 'Please select a valid food image.');
      } else {
        throw new Error(errPayload?.detail || errPayload?.message || 'Food analysis could not be completed.');
      }
    }

    const data = await response.json();

    if (!data.success && data.status !== 'low_confidence') {
      throw new Error(data.message || 'Food recognition could not be completed.');
    }

    // Normalize confidence values to 0.0 - 1.0 internally
    const rawConfPercent = typeof data.recognitionConfidence === 'number' ? data.recognitionConfidence : null;
    const normalizedConf = rawConfPercent != null ? rawConfPercent / 100.0 : null;

    const topPredictions = (data.topPredictions || []).map((pred) => ({
      food: pred.food,
      confidence: typeof pred.confidence === 'number' ? pred.confidence / 100.0 : 0.0,
      percentage: typeof pred.confidence === 'number' ? `${pred.confidence.toFixed(1)}%` : '0.0%',
      rawConfidence: pred.confidence,
    }));

    // When model is not configured / disconnected
    if (data.status === 'model_not_configured') {
      return {
        id: 'anls_' + Date.now(),
        detectedFood: null,
        recognitionConfidence: null,
        rawConfidencePercent: null,
        topPredictions: [],
        freshness: {
          label: null,
          confidence: null,
          status: 'unavailable',
          source: 'nathansekar/food-freshness-detector',
        },
        shelfLife: {
          status: 'unavailable',
          minDays: null,
          maxDays: null,
          source: 'USDA FoodKeeper',
        },
        eatFirstPriority: {
          status: 'unavailable',
          priority: null,
          score: null,
          reason: 'Eat First requires an available shelf-life estimate.',
        },
        analysisStatus: 'disconnected',
        source: 'none',
        model: null,
        modelVersion: null,
        status: 'model_not_configured',
        storageContext: {
          storage: pantryContext.storage || 'countertop',
          daysInPantry: Number(pantryContext.daysInPantry) || 0,
        },
        imageSrc: imageSource,
        analyzedAt: new Date().toISOString(),
        message: data.message || 'Food recognition model is disconnected. Awaiting integration of new pretrained model.',
      };
    }

    return {
      id: 'anls_' + Date.now(),
      detectedFood: data.detectedFood || null,
      recognitionConfidence: normalizedConf,
      rawConfidencePercent: rawConfPercent,
      topPredictions: topPredictions,
      detectedObjects: (data.detectedObjects || []).map((obj) => ({
        label: obj.label,
        confidence: typeof obj.confidence === 'number' ? obj.confidence : null,
        box: obj.box || null,
      })),
      foodRecognition: data.foodRecognition || {},
      freshness: {
        label: data.freshness?.label || null,
        confidence: data.freshness?.confidence != null
          ? data.freshness.confidence / 100.0
          : data.freshness?.score != null ? data.freshness.score / 100.0 : null,
        score: data.freshness?.score != null ? data.freshness.score : null,
        status: data.freshness?.status || (data.freshness?.label ? 'success' : 'unavailable'),
        source: data.freshness?.source || data.freshness?.modelVersion || 'nathansekar/food-freshness-detector',
        modelVersion: data.freshness?.modelVersion || 'nathansekar/food-freshness-detector',
      },
      shelfLife: {
        status: data.shelfLife?.status || 'unavailable',
        food: data.shelfLife?.food || null,
        storageType: data.shelfLife?.storageType || pantryContext.storage || 'countertop',
        daysStored: data.shelfLife?.daysStored != null ? data.shelfLife.daysStored : Number(pantryContext.daysInPantry) || 0,
        referenceDuration: data.shelfLife?.referenceDuration || null,
        remaining: data.shelfLife?.remaining || null,
        minDays: data.shelfLife?.remaining?.minDays != null ? data.shelfLife.remaining.minDays : null,
        maxDays: data.shelfLife?.remaining?.maxDays != null ? data.shelfLife.remaining.maxDays : null,
        unit: data.shelfLife?.unit || 'days',
        source: data.shelfLife?.source || 'USDA FoodKeeper',
        isEstimate: data.shelfLife?.isEstimate ?? true,
        heuristicApplied: data.shelfLife?.heuristicApplied ?? false,
        reason: data.shelfLife?.reason || null,
        tips: data.shelfLife?.tips || null,
        message: data.shelfLife?.reason || null,
      },
      eatFirstPriority: {
        status: data.eatFirstPriority?.status || 'unavailable',
        priority: data.eatFirstPriority?.priority || null,
        score: data.eatFirstPriority?.score != null ? data.eatFirstPriority.score : null,
        urgencyLabel: data.eatFirstPriority?.urgencyLabel || null,
        reason: data.eatFirstPriority?.reason || null,
      },
      analysisStatus: data.analysisStatus || (data.status === 'low_confidence' ? 'partial' : 'complete'),
      source: data.source || 'ml',
      model: data.model || 'Master Hybrid Vision',
      modelVersion: data.modelVersion || 'Hybrid Pretrained V1',
      modelVersions: data.modelVersions || {},
      status: data.analysisStatus || data.status,
      storageContext: {
        storage: pantryContext.storage || 'countertop',
        daysInPantry: Number(pantryContext.daysInPantry) || 0,
      },
      imageSrc: imageSource,
      analyzedAt: new Date().toISOString(),
      message: data.message || (data.detectedFood ? `Recognized as ${data.detectedFood} with ${rawConfPercent}% confidence.` : 'Analysis complete.'),
    };

  },

  /**
   * Multi-item comparison stub for future stages
   * @param {Array<File|string>} items
   * @returns {Promise<Array<object>>}
   */
  async compareMultipleFoods(items = []) {
    await new Promise((res) => setTimeout(res, 400));
    return [];
  },
};

export default analysisService;
