import React, { useState, useRef, useEffect } from 'react';
import { BrowserMultiFormatReader } from '@zxing/library';
import { packagedFoodService } from '../../services/packagedFoodService.js';
import { Toast } from '../../components/common/Toast.jsx';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';

export function PackagedFoodScannerPage({ navigate }) {
  const [activeTab, setActiveTab] = useState('barcode'); // 'barcode' | 'ocr' | 'manual'
  const [barcodeInput, setBarcodeInput] = useState('');
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [isProcessingOcr, setIsProcessingOcr] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [lookupMessage, setLookupMessage] = useState(null);

  // Form reference for smooth scrolling when data is extracted
  const formRef = useRef(null);

  // Camera state for live barcode scan or photo snap
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);

  // Toast notifications
  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3500);
  };

  // Uploaded image preview
  const [uploadedImageSrc, setUploadedImageSrc] = useState(null);

  // Verified / Editable Product Data for Pre-Save Review (Requirement 4)
  const [formData, setFormData] = useState({
    productName: '',
    brand: '',
    barcode: '',
    expiryDate: '',
    mfgDate: '',
    storageEnvironment: 'Pantry Shelf',
    storageInstructions: '',
    ingredients: '',
    nutrition: {
      calories: '',
      protein: '',
      carbs: '',
      fat: '',
    },
    imageSrc: '',
  });

  // Track whether form has been populated by a scan
  const [hasScannedData, setHasScannedData] = useState(false);

  useEffect(() => {
    return () => {
      stopCameraStream();
    };
  }, []);

  const stopCameraStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setIsCameraActive(false);
  };

  const startCamera = async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setIsCameraActive(true);

      // If native BarcodeDetector API is supported, attempt live video scanning
      if ('BarcodeDetector' in window) {
        initLiveBarcodeDetection();
      }
    } catch (err) {
      console.warn('Camera access denied or unavailable:', err);
      setCameraError('Camera access unavailable. Please upload an image or enter details manually.');
      setIsCameraActive(false);
    }
  };

  const initLiveBarcodeDetection = async () => {
    try {
      const detector = new window.BarcodeDetector({
        formats: ['ean_13', 'ean_8', 'upc_a', 'upc_e', 'code_128', 'qr_code'],
      });

      const scanLoop = async () => {
        if (!streamRef.current || !videoRef.current) return;
        try {
          const barcodes = await detector.detect(videoRef.current);
          if (barcodes.length > 0) {
            const rawVal = barcodes[0].rawValue;
            stopCameraStream();
            setBarcodeInput(rawVal);
            handleBarcodeLookup(rawVal);
            return;
          }
        } catch {}
        if (streamRef.current) {
          requestAnimationFrame(scanLoop);
        }
      };

      requestAnimationFrame(scanLoop);
    } catch (e) {
      console.log('Native BarcodeDetector not active, fallback to snapshot mode.');
    }
  };

  const calculateEstimatedExpiry = (days) => {
    if (!days) return '';
    const d = new Date();
    d.setDate(d.getDate() + Number(days));
    return d.toISOString().split('T')[0];
  };

  const captureCameraFrame = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
    stopCameraStream();
    setUploadedImageSrc(dataUrl);

    if (activeTab === 'ocr') {
      handleOcrExtraction(dataUrl);
    } else {
      triggerToast('Photo captured! Scanning for barcode...');
      handleScanImage(dataUrl);
    }
  };

  // Dedicated unified Scan Barcode function (from uploaded image or camera snapshot)
  const handleScanImage = async (imgToScan) => {
    const targetImage = imgToScan || uploadedImageSrc;
    if (!targetImage) {
      triggerToast('Please upload or capture a photo first.');
      return;
    }

    setIsScanning(true);
    setLookupMessage({
      type: 'info',
      text: 'Scanning barcode from image...',
    });

    try {
      // 1. Try client-side barcode decoding with @zxing/library
      let detectedBarcode = null;
      try {
        const reader = new BrowserMultiFormatReader();
        const zxResult = await reader.decodeFromImageUrl(targetImage);
        if (zxResult && zxResult.getText()) {
          detectedBarcode = zxResult.getText().trim();
          console.log('[ZXing Client] Detected barcode:', detectedBarcode);
        }
      } catch (clientErr) {
        console.log('[ZXing Client] Client-side reader pass:', clientErr);
      }

      // If client detected a barcode, look it up immediately!
      if (detectedBarcode) {
        setBarcodeInput(detectedBarcode);
        await handleBarcodeLookup(detectedBarcode);
        setIsScanning(false);
        return;
      }

      // 2. Try server-side barcode decoding pass (zxing-cpp)
      const scanRes = await packagedFoodService.scanBarcodeImage(targetImage);
      if (scanRes && scanRes.found && scanRes.product) {
        const p = scanRes.product;
        const code = scanRes.barcode || p.barcode || '';
        if (code) setBarcodeInput(code);

        const estExp = p.expiry_date || calculateEstimatedExpiry(p.default_shelf_life_days);
        const todayStr = new Date().toISOString().split('T')[0];

        setFormData((prev) => ({
          ...prev,
          productName: p.product_name || prev.productName,
          brand: p.brand || prev.brand,
          barcode: code || prev.barcode,
          expiryDate: estExp || prev.expiryDate,
          mfgDate: p.mfg_date || prev.mfgDate || todayStr,
          storageEnvironment: p.storage_environment || prev.storageEnvironment || 'Pantry Shelf',
          storageInstructions: p.storage_instructions || prev.storageInstructions,
          ingredients: p.ingredients || prev.ingredients,
          nutrition: {
            calories: p.nutrition?.calories ?? prev.nutrition?.calories ?? '',
            protein: p.nutrition?.protein ?? prev.nutrition?.protein ?? '',
            carbs: p.nutrition?.carbs ?? prev.nutrition?.carbs ?? '',
            fat: p.nutrition?.fat ?? prev.nutrition?.fat ?? '',
          },
          imageSrc: targetImage || p.image_url || prev.imageSrc,
        }));
        setHasScannedData(true);
        triggerToast(`Found: ${p.product_name}! Details loaded into form.`);
        setLookupMessage({
          type: 'success',
          text: scanRes.message || `Retrieved details for "${p.product_name}". Please verify dates below.`,
        });

        setTimeout(() => {
          formRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 150);
        setIsScanning(false);
        return;
      }

      if (scanRes && scanRes.barcode) {
        setBarcodeInput(scanRes.barcode);
        await handleBarcodeLookup(scanRes.barcode);
        setIsScanning(false);
        return;
      }

      // If no barcode was detected in the image, inform the user clearly
      setLookupMessage({
        type: 'warning',
        text: scanRes?.message || 'No barcode detected in image. If this is a product label or packaging, switch to the "Label OCR" tab or enter details manually below.',
      });
      setHasScannedData(true);
    } catch (err) {
      console.warn('Scan barcode error:', err);
      setLookupMessage({
        type: 'error',
        text: 'Failed to scan barcode from image. Please try again, switch to Label OCR, or enter details manually.',
      });
      setHasScannedData(true);
    } finally {
      setIsScanning(false);
    }
  };

  // Handle Barcode Image Upload (auto-trigger scan immediately)
  const handleBarcodeImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async (ev) => {
      const b64 = ev.target.result;
      setUploadedImageSrc(b64);
      triggerToast('Image uploaded. Scanning barcode and product details...');
      handleScanImage(b64);
    };
    reader.readAsDataURL(file);
  };

  // Handle Label OCR Image Upload
  const handleOcrImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const b64 = ev.target.result;
      setUploadedImageSrc(b64);
      handleOcrExtraction(b64);
    };
    reader.readAsDataURL(file);
  };

  // Perform Barcode Lookup (Requirement 2)
  const handleBarcodeLookup = async (codeToLookup) => {
    const code = (codeToLookup || barcodeInput).trim();
    if (!code) {
      triggerToast('Please enter or scan a barcode.');
      return;
    }

    setIsLookingUp(true);
    setLookupMessage(null);

    try {
      const res = await packagedFoodService.lookupBarcode(code);
      if (res.found && res.product) {
        const p = res.product;
        const estExp = p.expiry_date || calculateEstimatedExpiry(p.default_shelf_life_days);
        const todayStr = new Date().toISOString().split('T')[0];

        setFormData((prev) => ({
          ...prev,
          productName: p.product_name || prev.productName,
          brand: p.brand || prev.brand,
          barcode: code,
          expiryDate: estExp || prev.expiryDate,
          mfgDate: p.mfg_date || prev.mfgDate || todayStr,
          storageEnvironment: p.storage_environment || prev.storageEnvironment || 'Pantry Shelf',
          storageInstructions: p.storage_instructions || prev.storageInstructions,
          ingredients: p.ingredients || prev.ingredients,
          nutrition: {
            calories: p.nutrition?.calories ?? prev.nutrition.calories ?? '',
            protein: p.nutrition?.protein ?? prev.nutrition.protein ?? '',
            carbs: p.nutrition?.carbs ?? prev.nutrition.carbs ?? '',
            fat: p.nutrition?.fat ?? prev.nutrition.fat ?? '',
          },
          imageSrc: p.image_url || uploadedImageSrc || prev.imageSrc,
        }));
        setHasScannedData(true);
        triggerToast(`Found: ${p.product_name}! Please verify dates before saving.`);
        setLookupMessage({
          type: 'success',
          text: `Retrieved details for "${p.product_name}" from ${p.source || 'Product Catalog'}. Please verify or adjust dates below.`,
        });

        setTimeout(() => {
          formRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 150);
      } else {
        // Requirement 7: If barcode lookup fails, suggest OCR or manual entry
        setLookupMessage({
          type: 'warning',
          text: res.message || `Barcode ${code} was not found in catalog. Switch to Packaging Label OCR or enter details manually below.`,
        });
        setFormData((prev) => ({ ...prev, barcode: code }));
        setHasScannedData(true);
      }
    } catch (err) {
      setLookupMessage({
        type: 'error',
        text: 'Could not connect to barcode database. Please check connection or enter details manually.',
      });
      setHasScannedData(true);
    } finally {
      setIsLookingUp(false);
    }
  };

  // Perform Label OCR Extraction (Requirement 3)
  const handleOcrExtraction = async (imageB64) => {
    const targetImage = imageB64 || uploadedImageSrc;
    if (!targetImage) {
      triggerToast('Please upload or capture a label photo first.');
      return;
    }

    setIsProcessingOcr(true);
    setLookupMessage(null);

    try {
      const res = await packagedFoodService.extractLabelOcr(targetImage);
      if (res.success && res.extracted) {
        const ext = res.extracted;
        const hasExtractedData = Boolean(
          ext.product_name ||
          ext.brand ||
          ext.expiry_date ||
          ext.manufacturing_date ||
          ext.ingredients ||
          ext.storage_instructions ||
          ext.barcode
        );

        if (hasExtractedData) {
          setFormData((prev) => ({
            ...prev,
            productName: ext.product_name || prev.productName,
            brand: ext.brand || prev.brand,
            barcode: ext.barcode || prev.barcode,
            expiryDate: ext.expiry_date || prev.expiryDate,
            mfgDate: ext.manufacturing_date || prev.mfgDate,
            storageEnvironment: ext.storage_environment || prev.storageEnvironment || 'Pantry Shelf',
            storageInstructions: ext.storage_instructions || prev.storageInstructions,
            ingredients: ext.ingredients || prev.ingredients,
            nutrition: {
              calories: ext.nutrition?.calories ?? prev.nutrition.calories ?? '',
              protein: ext.nutrition?.protein ?? prev.nutrition.protein ?? '',
              carbs: ext.nutrition?.carbs ?? prev.nutrition.carbs ?? '',
              fat: ext.nutrition?.fat ?? prev.nutrition.fat ?? '',
            },
            imageSrc: targetImage || prev.imageSrc,
          }));
          setHasScannedData(true);

          const foundDate = ext.expiry_date ? ` Expiry date: ${ext.expiry_date}.` : ' Please enter expiry date.';
          triggerToast(`OCR extracted ${ext.product_name || 'details'}!${foundDate}`);
          setLookupMessage({
            type: 'success',
            text: `Extracted details for "${ext.product_name || 'packaged item'}". Please review and verify the details below before saving.`,
          });

          setTimeout(() => {
            formRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }, 150);
        } else {
          setLookupMessage({
            type: 'warning',
            text: res.error || 'No legible product text or dates detected on this label. Please enter details manually or try a clearer photo.',
          });
          setHasScannedData(true);
        }
      } else {
        setLookupMessage({
          type: 'warning',
          text: res.error || 'Could not parse text clearly. Please enter product details manually.',
        });
        setHasScannedData(true);
      }
    } catch (err) {
      console.error('OCR Error:', err);
      const errMsg = err?.response?.data?.detail || err?.message || 'OCR extraction encountered an error.';
      setLookupMessage({
        type: 'error',
        text: `OCR extraction failed: ${errMsg}. Please enter product details manually below.`,
      });
      setHasScannedData(true);
    } finally {
      setIsProcessingOcr(false);
    }
  };

  // Save to Pantry (Requirement 4 & 5)
  const handleSaveToPantry = async (e) => {
    e.preventDefault();
    if (!formData.productName.trim()) {
      triggerToast('Product Name is required.');
      return;
    }

    setIsSaving(true);
    try {
      await packagedFoodService.saveToPantry({
        ...formData,
        imageSrc: uploadedImageSrc || formData.imageSrc,
      });

      triggerToast(`Saved "${formData.productName}" to your pantry!`);
      // Reset form or navigate to history
      setTimeout(() => {
        navigate('/history');
      }, 1200);
    } catch (err) {
      triggerToast(err.message || 'Failed to save item to pantry.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleClear = () => {
    setFormData({
      productName: '',
      brand: '',
      barcode: '',
      expiryDate: '',
      mfgDate: '',
      storageEnvironment: 'Pantry Shelf',
      storageInstructions: '',
      ingredients: '',
      nutrition: { calories: '', protein: '', carbs: '', fat: '' },
      imageSrc: '',
    });
    setBarcodeInput('');
    setUploadedImageSrc(null);
    setHasScannedData(false);
    setLookupMessage(null);
    stopCameraStream();
  };

  return (
    <div className="space-y-8 pb-16 font-sans">
      <Toast message={toastMessage} visible={showToast} />

      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="text-2xl">📦</span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
              Packaged Food Scanner
            </h1>
            <span className="px-2.5 py-0.5 rounded-full bg-secondary-container text-on-secondary-container text-[11px] font-bold uppercase tracking-wider">
              Barcode + OCR
            </span>
          </div>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1 leading-relaxed">
            Scan product barcodes or snap packaging labels with OCR to auto-extract expiry dates, storage instructions, and nutrition into your pantry.
          </p>
        </div>

        <button
          type="button"
          onClick={() => navigate('/history')}
          className="px-4 py-2 rounded-full bg-surface-container-high hover:bg-surface-container text-primary text-xs font-bold transition-all flex items-center gap-1.5 self-start sm:self-auto cursor-pointer"
        >
          <span className="material-symbols-outlined text-[16px]">inventory_2</span>
          <span>View Pantry</span>
        </button>
      </div>

      {/* ── Scanning Mode Selector Tabs ── */}
      <div className="p-1 rounded-2xl bg-surface-container-low max-w-md flex items-center gap-1 border border-surface-container-high/60">
        <button
          type="button"
          onClick={() => {
            setActiveTab('barcode');
            stopCameraStream();
          }}
          className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
            activeTab === 'barcode'
              ? 'bg-white text-primary shadow-xs'
              : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">barcode_scanner</span>
          <span>Barcode Scan</span>
        </button>

        <button
          type="button"
          onClick={() => {
            setActiveTab('ocr');
            stopCameraStream();
          }}
          className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
            activeTab === 'ocr'
              ? 'bg-white text-primary shadow-xs'
              : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">document_scanner</span>
          <span>Label OCR</span>
        </button>

        <button
          type="button"
          onClick={() => {
            setActiveTab('manual');
            stopCameraStream();
            setHasScannedData(true);
          }}
          className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
            activeTab === 'manual'
              ? 'bg-white text-primary shadow-xs'
              : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">edit_note</span>
          <span>Manual Entry</span>
        </button>
      </div>

      {/* ── Mode 1: Barcode Scanning Panel ── */}
      {activeTab === 'barcode' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs space-y-5">
            <div className="flex items-center gap-2 text-sm font-bold text-primary">
              <span className="material-symbols-outlined text-secondary text-[20px]">photo_camera</span>
              <span>Camera Barcode Scanner</span>
            </div>

            {/* Video Viewport / Snapshot Area */}
            <div className="relative aspect-4/3 rounded-2xl bg-surface-container overflow-hidden border border-surface-container-high flex items-center justify-center">
              {isCameraActive ? (
                <>
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                  />
                  {/* Viewport Reticle / Targeting Box */}
                  <div className="absolute inset-8 border-2 border-secondary/80 rounded-2xl pointer-events-none flex items-center justify-center">
                    <div className="w-full h-0.5 bg-red-500 animate-pulse" />
                  </div>
                </>
              ) : uploadedImageSrc ? (
                <div className="relative w-full h-full flex items-center justify-center">
                  <img
                    src={uploadedImageSrc}
                    alt="Scanned item"
                    className="w-full h-full object-contain p-2"
                  />
                  {/* Floating quick-scan button directly on the image */}
                  <div className="absolute top-3 right-3 z-10">
                    <button
                      type="button"
                      onClick={() => handleScanImage(uploadedImageSrc)}
                      disabled={isScanning || isLookingUp}
                      className="px-3 py-1.5 rounded-full bg-primary/90 hover:bg-primary text-white text-xs font-bold shadow-md flex items-center gap-1.5 backdrop-blur-sm transition-all active:scale-95 cursor-pointer"
                    >
                      <span className="material-symbols-outlined text-[15px]">barcode_scanner</span>
                      <span>{isScanning ? 'Scanning...' : 'Scan Image'}</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center p-6 text-on-surface-variant">
                  <span className="material-symbols-outlined text-4xl text-on-surface-variant/40 block mb-2">
                    barcode_scanner
                  </span>
                  <p className="text-xs">Point your camera at a product barcode or upload a barcode image.</p>
                </div>
              )}
            </div>

            {cameraError && (
              <p className="text-xs text-error font-medium">{cameraError}</p>
            )}

            {/* Camera Actions */}
            <div className="flex flex-wrap items-center gap-2">
              {/* Prominent Scan Barcode button */}
              <button
                type="button"
                onClick={() => handleScanImage(uploadedImageSrc)}
                disabled={isScanning || isLookingUp || !uploadedImageSrc}
                className={`px-4 py-2.5 rounded-full font-bold text-xs shadow-2xs flex items-center gap-1.5 transition-all cursor-pointer ${
                  uploadedImageSrc
                    ? 'bg-primary text-white hover:bg-primary-container ring-2 ring-primary/20'
                    : 'bg-surface-container text-on-surface-variant/50 cursor-not-allowed opacity-60'
                }`}
                title={uploadedImageSrc ? 'Scan and extract barcode from this image' : 'Upload or capture an image to scan'}
              >
                {isScanning ? (
                  <>
                    <span className="material-symbols-outlined text-[16px] animate-spin">sync</span>
                    <span>Scanning Barcode...</span>
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-[16px]">barcode_scanner</span>
                    <span>Scan Barcode</span>
                  </>
                )}
              </button>

              {!isCameraActive ? (
                <button
                  type="button"
                  onClick={startCamera}
                  className="px-4 py-2.5 rounded-full bg-secondary text-white hover:bg-secondary/90 font-bold text-xs shadow-2xs flex items-center gap-1.5 transition-all cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[16px]">videocam</span>
                  <span>Start Camera</span>
                </button>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={captureCameraFrame}
                    className="px-4 py-2.5 rounded-full bg-primary text-white hover:bg-primary-container font-bold text-xs shadow-2xs flex items-center gap-1.5 transition-all cursor-pointer"
                  >
                    <span className="material-symbols-outlined text-[16px]">camera</span>
                    <span>Capture Photo</span>
                  </button>
                  <button
                    type="button"
                    onClick={stopCameraStream}
                    className="px-3.5 py-2.5 rounded-full bg-surface-container-high text-on-surface text-xs font-bold hover:bg-surface-container transition-all cursor-pointer"
                  >
                    Stop
                  </button>
                </>
              )}

              {/* Upload image button */}
              <label className="px-4 py-2.5 rounded-full bg-surface-container hover:bg-surface-container-high text-primary font-bold text-xs flex items-center gap-1.5 transition-all cursor-pointer">
                <span className="material-symbols-outlined text-[16px]">upload_file</span>
                <span>Upload Barcode Image</span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleBarcodeImageUpload}
                  className="hidden"
                />
              </label>
            </div>
          </div>

          {/* Direct Barcode Entry & Lookup Box */}
          <div className="p-6 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm font-bold text-primary">
                <span className="material-symbols-outlined text-secondary text-[20px]">search</span>
                <span>Direct Barcode Lookup</span>
              </div>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Enter the 8, 12, or 13-digit barcode number printed on any packaged grocery or food item.
              </p>

              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={barcodeInput}
                  onChange={(e) => setBarcodeInput(e.target.value)}
                  placeholder="e.g. 3017620422003 or 0011110417009"
                  className="flex-1 px-4 py-3 rounded-2xl bg-surface-container-lowest border border-surface-container-high focus:border-secondary focus:outline-none text-xs sm:text-sm font-mono"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleBarcodeLookup();
                    }
                  }}
                />
                <button
                  type="button"
                  disabled={isLookingUp || !barcodeInput.trim()}
                  onClick={() => handleBarcodeLookup()}
                  className="px-5 py-3 rounded-2xl bg-primary text-white hover:bg-primary-container disabled:opacity-50 text-xs font-bold shadow-2xs transition-all flex items-center gap-1.5 cursor-pointer shrink-0"
                >
                  {isLookingUp ? (
                    <>
                      <span className="material-symbols-outlined text-[16px] animate-spin">sync</span>
                      <span>Searching...</span>
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-[16px]">search</span>
                      <span>Look Up</span>
                    </>
                  )}
                </button>
              </div>

              {/* Lookup Feedback Notice */}
              {lookupMessage && (
                <div
                  className={`p-3.5 rounded-2xl text-xs flex items-start gap-2.5 ${
                    lookupMessage.type === 'success'
                      ? 'bg-emerald-50 text-emerald-900 border border-emerald-200'
                      : lookupMessage.type === 'warning'
                      ? 'bg-amber-50 text-amber-900 border border-amber-200'
                      : 'bg-red-50 text-red-900 border border-red-200'
                  }`}
                >
                  <span className="material-symbols-outlined text-[18px] shrink-0 mt-0.5">
                    {lookupMessage.type === 'success' ? 'check_circle' : 'info'}
                  </span>
                  <div>
                    <p className="font-semibold">{lookupMessage.text}</p>
                    {lookupMessage.type === 'warning' && (
                      <button
                        type="button"
                        onClick={() => setActiveTab('ocr')}
                        className="mt-2 inline-flex items-center gap-1 text-xs font-bold text-secondary underline cursor-pointer"
                      >
                        <span>Switch to Packaging Label OCR</span>
                        <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Quick Demo Barcodes for instant testing */}
            <div className="pt-4 border-t border-surface-container-low">
              <span className="text-[11px] font-bold text-on-surface-variant block mb-2">
                Quick Test Samples:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {[
                  { label: "Hershey's Syrup", code: '034000000449' },
                  { label: 'Nutella Spread', code: '3017620422003' },
                  { label: 'Organic Milk', code: '0011110417009' },
                  { label: 'Rolled Oats', code: '0041190005085' },
                  { label: 'Penne Pasta', code: '8076809513753' },
                ].map((s) => (
                  <button
                    key={s.code}
                    type="button"
                    onClick={() => {
                      setBarcodeInput(s.code);
                      handleBarcodeLookup(s.code);
                    }}
                    className="px-2.5 py-1 rounded-full bg-surface-container-low hover:bg-surface-container text-[11px] text-primary font-medium transition-colors cursor-pointer"
                  >
                    {s.label} ({s.code.slice(-4)})
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Mode 2: Label OCR Panel ── */}
      {activeTab === 'ocr' && (
        <div className="p-6 sm:p-8 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs space-y-6">
          <div className="max-w-xl">
            <div className="flex items-center gap-2 text-sm font-bold text-primary mb-1">
              <span className="material-symbols-outlined text-secondary text-[20px]">document_scanner</span>
              <span>Packaging Label OCR Extraction</span>
            </div>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Upload or snap a photo of the product container label, expiry stamp (EXP / Best Before), or nutrition table.
              Our OCR extracts the text for your review without hallucinating missing dates.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            {/* Image Preview & Upload Dropzone */}
            <div className="aspect-4/3 rounded-2xl bg-surface-container-low border-2 border-dashed border-surface-container-high flex flex-col items-center justify-center p-4 overflow-hidden relative">
              {isCameraActive ? (
                <>
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover rounded-xl"
                  />
                  <div className="absolute bottom-3 flex gap-2">
                    <button
                      type="button"
                      onClick={captureCameraFrame}
                      className="px-4 py-2 rounded-full bg-primary text-white text-xs font-bold shadow-md cursor-pointer"
                    >
                      Capture Photo
                    </button>
                    <button
                      type="button"
                      onClick={stopCameraStream}
                      className="px-3 py-2 rounded-full bg-surface-container text-on-surface text-xs font-bold cursor-pointer"
                    >
                      Cancel
                    </button>
                  </div>
                </>
              ) : uploadedImageSrc ? (
                <img
                  src={uploadedImageSrc}
                  alt="Packaging label"
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="text-center p-6 space-y-3">
                  <span className="material-symbols-outlined text-4xl text-primary/40 block">
                    add_photo_alternate
                  </span>
                  <p className="text-xs text-on-surface-variant max-w-xs">
                    Take or upload a crisp photo of the label showing the product name, dates, or ingredients.
                  </p>
                  <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
                    <button
                      type="button"
                      onClick={startCamera}
                      className="px-4 py-2 rounded-full bg-secondary text-white hover:bg-secondary/90 text-xs font-bold shadow-2xs cursor-pointer flex items-center gap-1.5"
                    >
                      <span className="material-symbols-outlined text-[16px]">videocam</span>
                      <span>Use Camera</span>
                    </button>
                    <label className="px-4 py-2 rounded-full bg-surface-container hover:bg-surface-container-high text-primary text-xs font-bold cursor-pointer flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[16px]">upload_file</span>
                      <span>Upload Photo</span>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleOcrImageUpload}
                        className="hidden"
                      />
                    </label>
                  </div>
                </div>
              )}
            </div>

            {/* OCR Processing Card */}
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-surface-container-low border border-surface-container-high/60 space-y-2">
                <span className="text-xs font-bold text-primary block">Supported Label Elements:</span>
                <ul className="text-[11px] text-on-surface-variant space-y-1 list-disc list-inside">
                  <li>Expiry Date (EXP, Best Before, BB, Use By)</li>
                  <li>Manufacturing Date (MFG, PKD)</li>
                  <li>Product Title & Brand details</li>
                  <li>Ingredients list & allergen notices</li>
                  <li>Storage guidance (e.g. "Refrigerate after opening")</li>
                  <li>Nutrition facts (Calories, Protein, Carbs, Fat)</li>
                </ul>
              </div>

              {uploadedImageSrc && !isCameraActive && (
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    disabled={isProcessingOcr}
                    onClick={() => handleOcrExtraction(uploadedImageSrc)}
                    className="flex-1 py-3 px-4 rounded-2xl bg-primary text-white hover:bg-primary-container disabled:opacity-50 text-xs font-bold shadow-sm transition-all flex items-center justify-center gap-2 cursor-pointer"
                  >
                    {isProcessingOcr ? (
                      <>
                        <span className="material-symbols-outlined text-[16px] animate-spin">sync</span>
                        <span>Extracting Label Text via OCR...</span>
                      </>
                    ) : (
                      <>
                        <span className="material-symbols-outlined text-[16px]">document_scanner</span>
                        <span>Re-run OCR Extraction</span>
                      </>
                    )}
                  </button>
                  <label className="p-3 rounded-2xl bg-surface-container hover:bg-surface-container-high text-primary text-xs font-bold cursor-pointer">
                    <span className="material-symbols-outlined text-[18px]">photo_camera</span>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleOcrImageUpload}
                      className="hidden"
                    />
                  </label>
                </div>
              )}

              {lookupMessage && (
                <div
                  className={`p-3.5 rounded-2xl text-xs flex items-start gap-2.5 ${
                    lookupMessage.type === 'success'
                      ? 'bg-emerald-50 text-emerald-900 border border-emerald-200'
                      : lookupMessage.type === 'error'
                      ? 'bg-red-50 text-red-900 border border-red-200'
                      : 'bg-amber-50 text-amber-900 border border-amber-200'
                  }`}
                >
                  <span className="material-symbols-outlined text-[18px] shrink-0 mt-0.5">
                    {lookupMessage.type === 'success' ? 'check_circle' : lookupMessage.type === 'error' ? 'error' : 'info'}
                  </span>
                  <p className="font-semibold">{lookupMessage.text}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Pre-Save Review & Correction Form (Requirement 4, 7, 8) ── */}
      <form
          ref={formRef}
          onSubmit={handleSaveToPantry}
          className="p-6 sm:p-8 rounded-3xl bg-white border border-surface-container-high shadow-sm space-y-6 animate-in fade-in slide-in-from-bottom duration-300"
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-surface-container-low">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl">📋</span>
                <h2 className="text-lg font-extrabold text-primary">
                  Review & Verify Product Details
                </h2>
              </div>
              <p className="text-xs text-on-surface-variant mt-0.5">
                Verify the extracted fields below. Correct any values or enter missing dates before saving to your pantry.
              </p>
            </div>

            <button
              type="button"
              onClick={handleClear}
              className="px-3 py-1.5 rounded-full text-xs font-bold text-on-surface-variant hover:text-red-700 hover:bg-red-50 transition-colors self-start sm:self-auto cursor-pointer"
            >
              Reset Form
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Product Name */}
            <div className="space-y-1 sm:col-span-2">
              <label className="text-xs font-bold text-primary block">
                Product Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.productName}
                onChange={(e) => setFormData({ ...formData, productName: e.target.value })}
                placeholder="e.g. Organic Rolled Oats, Penne Rigate"
                className="w-full px-4 py-2.5 rounded-xl bg-surface-container-lowest border border-surface-container-high focus:border-secondary focus:outline-none text-xs sm:text-sm font-semibold"
              />
            </div>

            {/* Brand */}
            <div className="space-y-1">
              <label className="text-xs font-bold text-primary block">Brand / Producer</label>
              <input
                type="text"
                value={formData.brand}
                onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                placeholder="e.g. Quaker, Barilla"
                className="w-full px-4 py-2.5 rounded-xl bg-surface-container-lowest border border-surface-container-high focus:border-secondary focus:outline-none text-xs sm:text-sm"
              />
            </div>

            {/* Barcode Number */}
            <div className="space-y-1">
              <label className="text-xs font-bold text-primary block">Barcode (EAN/UPC)</label>
              <input
                type="text"
                value={formData.barcode}
                onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
                placeholder="e.g. 0041190005085"
                className="w-full px-4 py-2.5 rounded-xl bg-surface-container-lowest border border-surface-container-high focus:border-secondary focus:outline-none text-xs sm:text-sm font-mono"
              />
            </div>

            {/* Expiry / Best Before Date */}
            <div className="space-y-1">
              <label className="text-xs font-bold text-primary block">
                Expiry Date / Best Before ⏳
              </label>
              <input
                type="date"
                value={formData.expiryDate}
                onChange={(e) => setFormData({ ...formData, expiryDate: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl bg-surface-container-lowest border border-surface-container-high focus:border-secondary focus:outline-none text-xs sm:text-sm font-semibold"
              />
              <span className="text-[10px] text-on-surface-variant block">
                Used to trigger smart expiry countdowns and Eat First rankings.
              </span>
            </div>

            {/* Manufacturing Date */}
            <div className="space-y-1">
              <label className="text-xs font-bold text-primary block">Manufacturing Date (MFG)</label>
              <input
                type="date"
                value={formData.mfgDate}
                onChange={(e) => setFormData({ ...formData, mfgDate: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl bg-surface-container-lowest border border-surface-container-high focus:border-secondary focus:outline-none text-xs sm:text-sm"
              />
            </div>

            {/* Storage Environment */}
            <div className="space-y-1">
              <label className="text-xs font-bold text-primary block">Storage Environment</label>
              <select
                value={formData.storageEnvironment}
                onChange={(e) => setFormData({ ...formData, storageEnvironment: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl bg-surface-container-lowest border border-surface-container-high focus:border-secondary focus:outline-none text-xs sm:text-sm cursor-pointer"
              >
                <option value="Pantry Shelf">Pantry Shelf (Ambient)</option>
                <option value="Refrigerator">Refrigerator (Chilled)</option>
                <option value="Freezer">Freezer (Frozen)</option>
              </select>
            </div>

            {/* Storage Guidance */}
            <div className="space-y-1 sm:col-span-2">
              <label className="text-xs font-bold text-primary block">Storage Instructions</label>
              <input
                type="text"
                value={formData.storageInstructions}
                onChange={(e) => setFormData({ ...formData, storageInstructions: e.target.value })}
                placeholder="e.g. Keep in a cool, dry place. Refrigerate after opening."
                className="w-full px-4 py-2.5 rounded-xl bg-surface-container-lowest border border-surface-container-high focus:border-secondary focus:outline-none text-xs sm:text-sm"
              />
            </div>

            {/* Ingredients */}
            <div className="space-y-1 sm:col-span-3">
              <label className="text-xs font-bold text-primary block">Ingredients</label>
              <textarea
                rows={2}
                value={formData.ingredients}
                onChange={(e) => setFormData({ ...formData, ingredients: e.target.value })}
                placeholder="e.g. Whole wheat flour, water, yeast, salt..."
                className="w-full px-4 py-2.5 rounded-xl bg-surface-container-lowest border border-surface-container-high focus:border-secondary focus:outline-none text-xs leading-relaxed"
              />
            </div>
          </div>

          {/* Optional Nutritional Facts */}
          <div className="pt-2">
            <span className="text-xs font-bold text-primary block mb-2">Nutritional Information (per 100g / serving)</span>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 rounded-2xl bg-surface-container-low border border-surface-container-high/60">
                <span className="text-[10px] text-on-surface-variant font-bold block uppercase">Calories</span>
                <input
                  type="text"
                  value={formData.nutrition?.calories || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      nutrition: { ...formData.nutrition, calories: e.target.value },
                    })
                  }
                  placeholder="kcal"
                  className="w-full mt-1 bg-transparent text-xs font-bold text-primary focus:outline-none"
                />
              </div>
              <div className="p-3 rounded-2xl bg-surface-container-low border border-surface-container-high/60">
                <span className="text-[10px] text-on-surface-variant font-bold block uppercase">Protein</span>
                <input
                  type="text"
                  value={formData.nutrition?.protein || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      nutrition: { ...formData.nutrition, protein: e.target.value },
                    })
                  }
                  placeholder="e.g. 8g"
                  className="w-full mt-1 bg-transparent text-xs font-bold text-primary focus:outline-none"
                />
              </div>
              <div className="p-3 rounded-2xl bg-surface-container-low border border-surface-container-high/60">
                <span className="text-[10px] text-on-surface-variant font-bold block uppercase">Carbs</span>
                <input
                  type="text"
                  value={formData.nutrition?.carbs || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      nutrition: { ...formData.nutrition, carbs: e.target.value },
                    })
                  }
                  placeholder="e.g. 24g"
                  className="w-full mt-1 bg-transparent text-xs font-bold text-primary focus:outline-none"
                />
              </div>
              <div className="p-3 rounded-2xl bg-surface-container-low border border-surface-container-high/60">
                <span className="text-[10px] text-on-surface-variant font-bold block uppercase">Fat</span>
                <input
                  type="text"
                  value={formData.nutrition?.fat || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      nutrition: { ...formData.nutrition, fat: e.target.value },
                    })
                  }
                  placeholder="e.g. 3g"
                  className="w-full mt-1 bg-transparent text-xs font-bold text-primary focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Form Submit & Navigation */}
          <div className="pt-4 border-t border-surface-container-low flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs text-on-surface-variant">
              Saves to your user pantry with real-time expiry alerts and recipe suggestions.
            </span>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => navigate('/history')}
                className="px-4 py-2.5 rounded-full text-xs font-bold text-on-surface-variant hover:bg-surface-container transition-all cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSaving}
                className="px-6 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-md hover:shadow-lg transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                {isSaving ? (
                  <>
                    <span className="material-symbols-outlined text-[16px] animate-spin">sync</span>
                    <span>Saving to Pantry...</span>
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-[16px]">check</span>
                    <span>Save to Pantry</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
    </div>
  );
}

export default PackagedFoodScannerPage;

