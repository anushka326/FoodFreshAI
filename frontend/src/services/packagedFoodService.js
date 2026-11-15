/**
 * FoodFresh AI — Packaged Food & Barcode Service
 * Manages Barcode lookup, Label OCR extraction, and Pantry saving.
 */

import { ENDPOINTS } from '../config/api.js';
import { getAuthHeaders } from './storageUtils.js';

export const packagedFoodService = {
  /**
   * Look up product information via barcode (Open Food Facts + local catalog)
   */
  async lookupBarcode(barcode) {
    if (!barcode) return { success: false, found: false, message: 'Barcode is required.' };
    try {
      const res = await fetch(ENDPOINTS.PACKAGED_FOOD_BARCODE, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ barcode: String(barcode).trim() }),
      });
      if (!res.ok) {
        throw new Error(`Barcode lookup failed (${res.status})`);
      }
      return await res.json();
    } catch (err) {
      console.warn('Barcode lookup request error:', err);
      return {
        success: false,
        found: false,
        message: 'Could not connect to barcode database. Please use OCR or enter manually.',
      };
    }
  },

  /**
   * Scan and decode barcode directly from an image, resolving product catalog data
   */
  async scanBarcodeImage(imageB64) {
    if (!imageB64) return { success: false, found: false, message: 'No image provided.' };
    try {
      const res = await fetch(ENDPOINTS.PACKAGED_FOOD_SCAN_IMAGE, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ image: imageB64 }),
      });
      if (!res.ok) {
        throw new Error(`Image barcode scan failed (${res.status})`);
      }
      return await res.json();
    } catch (err) {
      console.warn('Image barcode scan request error:', err);
      return {
        success: false,
        found: false,
        message: 'Could not process barcode from image. Please enter manually.',
      };
    }
  },

  /**
   * Perform label OCR on an uploaded or camera-captured packaging image
   */
  async extractLabelOcr(imageB64) {
    if (!imageB64) return { success: false, error: 'No image provided.' };
    try {
      const res = await fetch(ENDPOINTS.PACKAGED_FOOD_OCR, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ image: imageB64 }),
      });
      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `OCR extraction failed (${res.status})`);
      }
      return await res.json();
    } catch (err) {
      console.warn('OCR extraction request error:', err);
      return {
        success: false,
        error: err.message || 'OCR extraction encountered an error. Please enter details manually.',
        extracted: {
          product_name: null,
          brand: null,
          manufacturing_date: null,
          expiry_date: null,
          ingredients: null,
          storage_instructions: null,
          nutrition: null,
        },
      };
    }
  },

  /**
   * Save verified packaged food record into the user's authentic pantry database
   */
  async saveToPantry(verifiedData) {
    if (!verifiedData || !verifiedData.productName) {
      throw new Error('Product name is required to save to pantry.');
    }

    const storageEnv = verifiedData.storageEnvironment || 'Pantry Shelf';
    const isFridge = storageEnv.toLowerCase().includes('fridge') || storageEnv.toLowerCase().includes('refrigerat');
    const isFreezer = storageEnv.toLowerCase().includes('freez');

    const pantryPayload = {
      foodName: verifiedData.productName.trim(),
      cultivar: verifiedData.brand
        ? `${verifiedData.productName.trim()} • ${verifiedData.brand.trim()}`
        : `${verifiedData.productName.trim()} • Packaged`,
      status: 'Packaged Good',
      statusCategory: 'fresh',
      qualityScore: 90,
      storageEnvironment: storageEnv,
      storageType: isFridge ? 'fridge' : (isFreezer ? 'freezer' : 'countertop'),
      guidance: verifiedData.storageInstructions || 'Store unopened in optimal pantry conditions.',
      imageSrc: verifiedData.imageSrc || '/src/assets/food/cutting-board-sourdough.jpg',
      barcode: verifiedData.barcode || null,
      brand: verifiedData.brand || null,
      itemType: 'packaged',
      mfgDate: verifiedData.mfgDate || null,
      expiryDate: verifiedData.expiryDate || null,
      estimatedEndAt: verifiedData.expiryDate ? `${verifiedData.expiryDate}T23:59:59+00:00` : null,
      ingredients: verifiedData.ingredients || null,
      nutrition: verifiedData.nutrition || null,
      storageInstructions: verifiedData.storageInstructions || null,
    };

    const res = await fetch(ENDPOINTS.PANTRY_HISTORY, {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ item: pantryPayload }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to save packaged food to pantry.');
    }

    return await res.json();
  },
};

export default packagedFoodService;

