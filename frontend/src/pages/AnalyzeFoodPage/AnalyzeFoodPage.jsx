import React, { useState, useEffect, useRef } from 'react';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';
import { analysisService } from '../../services/analysisService.js';
import { historyService } from '../../services/historyService.js';
import { freshoBuddyService } from '../../services/freshoBuddyService.js';
import { Toast } from '../../components/common/Toast.jsx';

export function AnalyzeFoodPage({ navigate }) {
  const [analysisMode, setAnalysisMode] = useState('single'); // 'single' | 'compare'
  const [uploadedImage, setUploadedImage] = useState(null);
  const [showRemoveConfirm, setShowRemoveConfirm] = useState(false);
  const [storageLocation, setStorageLocation] = useState('countertop'); // 'countertop' | 'fridge'
  const [daysInKitchen, setDaysInKitchen] = useState(2);

  // Scanning & Error state
  const [isScanning, setIsScanning] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);

  // Camera capture state & refs
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);

  // Results state conforming to FoodAnalysisResult
  const [singleResult, setSingleResult] = useState(null);
  const [compareResults, setCompareResults] = useState(null);

  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  /**
   * Stop all active MediaStream tracks and clean up camera resources
   */
  const stopCameraStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop();
      });
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  };

  // Component unmount cleanup - guarantee camera indicator stops
  useEffect(() => {
    return () => {
      stopCameraStream();
    };
  }, []);

  // Sync video element with active camera stream once DOM element mounts
  useEffect(() => {
    if (isCameraActive && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;
      videoRef.current.play().catch(() => {});
    }
  }, [isCameraActive]);

  /**
   * Start live camera preview upon intentional user action
   */
  const handleStartCamera = async () => {
    setCameraError(null);
    setAnalysisError(null);
    stopCameraStream();

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      const msg = 'Camera capture is not supported by your current browser. Please use Upload Image instead.';
      setCameraError(msg);
      triggerToast(msg);
      return;
    }

    try {
      let stream;
      try {
        // Preferred mobile rear-facing camera with high resolution
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: { ideal: 'environment' },
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
          audio: false,
        });
      } catch {
        // Fallback to standard video stream
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
      }

      streamRef.current = stream;
      setIsCameraActive(true);
    } catch (err) {
      stopCameraStream();
      let msg = 'Could not access the camera. Please use Upload Image instead.';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        msg = 'Camera access was denied. Please allow camera permission in your browser settings or use Upload Image instead.';
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        msg = 'No camera device found on this system. Please use Upload Image instead.';
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        msg = 'Camera is already in use by another application. Please close other camera apps and try again.';
      }
      setCameraError(msg);
      triggerToast(msg);
    }
  };

  /**
   * Capture still photo from live camera feed
   */
  const handleCapturePhoto = () => {
    if (!videoRef.current || !streamRef.current) return;

    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    const width = video.videoWidth || 1280;
    const height = video.videoHeight || 720;
    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, width, height);

    // High quality JPEG without decorative filters or manipulation
    const capturedDataUrl = canvas.toDataURL('image/jpeg', 0.92);

    // Converge directly into the common image state
    setUploadedImage(capturedDataUrl);
    setSingleResult(null);
    setCompareResults(null);
    setAnalysisError(null);

    // Mandatory cleanup of camera hardware stream
    stopCameraStream();
    triggerToast('Photo captured successfully!');
  };

  /**
   * Cancel live camera preview without altering previously loaded image
   */
  const handleCancelCamera = () => {
    stopCameraStream();
    setCameraError(null);
  };

  /**
   * Start food analysis workflow (common to uploaded and camera-captured images)
   */
  const handleStartAnalysis = async () => {
    if (!uploadedImage) {
      triggerToast('Please upload or capture a food image first.');
      return;
    }

    setAnalysisError(null);
    setSingleResult(null);
    setCompareResults(null);
    setIsScanning(true);

    try {
      if (analysisMode === 'single') {
        const result = await analysisService.analyzeSingleFood(uploadedImage, {
          storage: storageLocation,
          daysInPantry: daysInKitchen,
        });
        if (!result) {
          throw new Error('Food analysis could not be completed.');
        }
        setSingleResult(result);
      } else {
        const results = await analysisService.compareMultipleFoods([uploadedImage]);
        setCompareResults(results);
      }
    } catch (err) {
      setAnalysisError(err.message || 'Food analysis could not be completed.');
      triggerToast(err.message || 'Food analysis could not be completed.');
    } finally {
      setIsScanning(false);
    }
  };

  const handleSaveToHistory = async () => {
    if (!singleResult || singleResult.source !== 'ml' || !singleResult.detectedFood) {
      triggerToast('Saving to Pantry History will be available after ML model integration.');
      return;
    }
    const saved = await historyService.saveToHistory(singleResult);
    if (saved) {
      triggerToast(`Saved ${singleResult.detectedFood} to your Pantry History!`);
    }
  };

  const handleFileDrop = (e) => {
    e.preventDefault();
    stopCameraStream();
    setCameraError(null);

    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (uploadEvent) => {
        setUploadedImage(uploadEvent.target.result);
        setSingleResult(null);
        setCompareResults(null);
        setAnalysisError(null);
      };
      reader.readAsDataURL(file);
    }
  };

  /**
   * Remove current food photo and analysis state after confirmation
   */
  const handleConfirmRemoveFood = () => {
    stopCameraStream();
    setUploadedImage(null);
    setSingleResult(null);
    setCompareResults(null);
    setAnalysisError(null);
    setCameraError(null);
    setIsScanning(false);
    setShowRemoveConfirm(false);
    triggerToast('Food removed from current analysis.');
  };

  const handleChooseAnotherImage = () => {
    stopCameraStream();
    setUploadedImage(null);
    setSingleResult(null);
    setCompareResults(null);
    setAnalysisError(null);
    setCameraError(null);
  };

  const getPriorityLabel = (tier) => {
    if (tier === 1) return 'Consume First';
    if (tier === 2) return 'Consume Soon';
    if (tier === 3) return 'Can Wait';
    return 'Pending Evaluation';
  };

  return (
    <div className="space-y-8 pb-12 font-sans">
      <Toast message={toastMessage} visible={showToast} />

      {/* Header & Mode Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
            Analyze Food
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
            Inspect produce photos, evaluate visible quality, and prepare for ML model inference.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center p-1 bg-surface-container-low rounded-2xl border border-surface-container-high self-start sm:self-auto">
          <button
            type="button"
            onClick={() => {
              setAnalysisMode('single');
              setSingleResult(null);
              setCompareResults(null);
              setAnalysisError(null);
            }}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              analysisMode === 'single'
                ? 'bg-primary text-white shadow-2xs'
                : 'text-on-surface-variant hover:text-primary'
            }`}
          >
            🍎 Single Food Item
          </button>
          <button
            type="button"
            onClick={() => {
              setAnalysisMode('compare');
              setSingleResult(null);
              setCompareResults(null);
              setAnalysisError(null);
            }}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              analysisMode === 'compare'
                ? 'bg-primary text-white shadow-2xs'
                : 'text-on-surface-variant hover:text-primary'
            }`}
          >
            🥇 Compare & Prioritize
          </button>
        </div>
      </div>

      {/* MAIN TWO-COLUMN WORKBENCH */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* LEFT WORKBENCH: Upload Zone & Pantry Context (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Produce Photo Source Card */}
          <div className="p-6 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-primary">Produce Photo Source</h2>
              <span className="text-[11px] text-on-surface-variant font-semibold">Camera or File</span>
            </div>

            {/* Quick Action Selector (Upload Image vs Take Photo vs Remove Food) */}
            <div className="flex flex-wrap items-center gap-2">
              <label className="flex-1 min-w-[105px] py-2.5 px-3 rounded-2xl bg-surface-container-low hover:bg-surface-container border border-surface-container-high font-bold text-xs text-primary flex items-center justify-center gap-1.5 cursor-pointer transition-all active:scale-98">
                <span className="material-symbols-outlined text-[18px]">upload_file</span>
                <span>Upload Image</span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileDrop}
                  className="hidden"
                />
              </label>

              <button
                type="button"
                onClick={handleStartCamera}
                className={`flex-1 min-w-[105px] py-2.5 px-3 rounded-2xl font-bold text-xs flex items-center justify-center gap-1.5 cursor-pointer transition-all active:scale-98 ${
                  isCameraActive
                    ? 'bg-primary text-white shadow-xs'
                    : 'bg-secondary-container/60 hover:bg-secondary-container text-on-secondary-container'
                }`}
                aria-label="Take Photo"
              >
                <span className="material-symbols-outlined text-[18px]">photo_camera</span>
                <span>Take Photo</span>
              </button>

              <button
                type="button"
                id="remove-food-btn"
                disabled={!uploadedImage}
                onClick={() => setShowRemoveConfirm(true)}
                className={`py-2.5 px-3 rounded-2xl font-bold text-xs flex items-center justify-center gap-1.5 transition-all ${
                  uploadedImage
                    ? 'bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 cursor-pointer active:scale-98'
                    : 'bg-surface-container-low text-on-surface-variant/40 border border-surface-container-high cursor-not-allowed opacity-50'
                }`}
                aria-label="Remove Food"
                title={uploadedImage ? 'Remove food from current analysis' : 'Select a food image first'}
              >
                <span className="material-symbols-outlined text-[18px]">delete</span>
                <span>Remove Food</span>
              </button>
            </div>

            {/* Camera Error Notice */}
            {cameraError && !isCameraActive && (
              <div className="p-3.5 rounded-2xl bg-error-container text-on-error-container text-xs flex items-start gap-2.5 border border-red-200">
                <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
                <p className="flex-1 leading-snug">{cameraError}</p>
                <button
                  type="button"
                  onClick={() => setCameraError(null)}
                  className="font-bold text-error cursor-pointer"
                >
                  ✕
                </button>
              </div>
            )}

            {/* Photo Container: Live Video Stream, Captured/Uploaded Image Preview, or Idle Dropzone */}
            <div className="relative group rounded-2xl overflow-hidden border-2 border-dashed border-secondary/40 hover:border-secondary bg-surface-container-low/40 transition-all">
              {isCameraActive ? (
                /* LIVE CAMERA PREVIEW WITH CAPTURE & CANCEL */
                <div className="relative aspect-video w-full overflow-hidden bg-black flex items-center justify-center">
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                  />

                  {/* Cancel Button */}
                  <div className="absolute top-2.5 right-2.5 z-10">
                    <button
                      type="button"
                      onClick={handleCancelCamera}
                      aria-label="Cancel camera"
                      className="px-3 py-1 rounded-full bg-black/60 hover:bg-black/80 text-white text-xs font-semibold backdrop-blur-sm transition-all cursor-pointer flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined text-[16px]">close</span>
                      <span>Cancel</span>
                    </button>
                  </div>

                  {/* Capture Button */}
                  <div className="absolute bottom-3 inset-x-0 z-10 flex items-center justify-center gap-3 px-4">
                    <button
                      type="button"
                      onClick={handleCapturePhoto}
                      aria-label="Capture photo"
                      className="px-6 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white font-bold text-xs shadow-lg transition-all flex items-center gap-2 cursor-pointer active:scale-95"
                    >
                      <span className="material-symbols-outlined text-[18px]">camera</span>
                      <span>Capture Photo</span>
                    </button>
                  </div>
                </div>
              ) : uploadedImage ? (
                /* PREVIEW OF UPLOADED OR CAPTURED IMAGE */
                <div className="relative aspect-video w-full overflow-hidden">
                  <img
                    src={uploadedImage}
                    alt="Uploaded food image"
                    className="w-full h-full object-cover group-hover:scale-102 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-primary/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <label className="px-3.5 py-1.5 rounded-full bg-white text-primary text-xs font-bold shadow-md cursor-pointer hover:bg-surface-container flex items-center gap-1">
                      <span className="material-symbols-outlined text-[16px]">upload_file</span>
                      <span>Change</span>
                      <input type="file" accept="image/*" onChange={handleFileDrop} className="hidden" />
                    </label>
                    <button
                      type="button"
                      onClick={handleStartCamera}
                      className="px-3.5 py-1.5 rounded-full bg-white text-primary text-xs font-bold shadow-md cursor-pointer hover:bg-surface-container flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined text-[16px]">photo_camera</span>
                      <span>Retake</span>
                    </button>
                  </div>
                  <div className="absolute bottom-2 left-2 px-2.5 py-0.5 rounded-full bg-white/90 backdrop-blur-xs text-[10px] font-bold text-primary">
                    ✓ Photo Loaded
                  </div>
                </div>
              ) : (
                /* IDLE DROPZONE / INPUT PROMPT */
                <div className="p-6 sm:p-8 flex flex-col items-center justify-center text-center">
                  <div className="w-14 h-14 rounded-2xl bg-white shadow-2xs flex items-center justify-center text-secondary mb-3">
                    <span className="material-symbols-outlined text-[28px]">add_a_photo</span>
                  </div>
                  <p className="text-xs font-bold text-primary">
                    Upload or take a food photo
                  </p>
                  <p className="text-[11px] text-on-surface-variant mt-1 mb-4">
                    Select a counter or refrigerator food photo
                  </p>
                  <div className="flex items-center gap-2.5">
                    <label className="px-4 py-2 rounded-full bg-white border border-surface-container-high text-primary text-xs font-bold shadow-2xs hover:bg-surface-container cursor-pointer transition-colors flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[16px]">upload_file</span>
                      <span>Browse Files</span>
                      <input type="file" accept="image/*" onChange={handleFileDrop} className="hidden" />
                    </label>
                    <button
                      type="button"
                      onClick={handleStartCamera}
                      className="px-4 py-2 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-2xs cursor-pointer transition-colors flex items-center gap-1.5"
                    >
                      <span className="material-symbols-outlined text-[16px]">photo_camera</span>
                      <span>Take Photo</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Pantry Context Settings Card */}
          <div className="p-6 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm space-y-4">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary text-[20px]">shelves</span>
              <h2 className="text-sm font-bold text-primary">Pantry Context (Storage Signal)</h2>
            </div>

            {/* Storage Location */}
            <div>
              <label className="block text-xs font-bold text-on-surface mb-2">
                Storage Environment
              </label>
              <div className="grid grid-cols-2 gap-2.5">
                <button
                  type="button"
                  onClick={() => setStorageLocation('countertop')}
                  className={`p-3 rounded-2xl border text-left transition-all cursor-pointer ${
                    storageLocation === 'countertop'
                      ? 'bg-secondary-container/40 border-secondary text-primary'
                      : 'bg-surface-container-low border-surface-container-high text-on-surface-variant'
                  }`}
                >
                  <div className="flex items-center gap-1.5 text-xs font-bold">
                    <span>☀️</span>
                    <span>Countertop</span>
                  </div>
                  <span className="text-[11px] block mt-0.5 opacity-80">Ambient ~21°C</span>
                </button>

                <button
                  type="button"
                  onClick={() => setStorageLocation('fridge')}
                  className={`p-3 rounded-2xl border text-left transition-all cursor-pointer ${
                    storageLocation === 'fridge'
                      ? 'bg-secondary-container/40 border-secondary text-primary'
                      : 'bg-surface-container-low border-surface-container-high text-on-surface-variant'
                  }`}
                >
                  <div className="flex items-center gap-1.5 text-xs font-bold">
                    <span>❄️</span>
                    <span>Crisper Chill</span>
                  </div>
                  <span className="text-[11px] block mt-0.5 opacity-80">Refrigerated ~4°C</span>
                </button>
              </div>
            </div>

            {/* Days on Counter Slider */}
            <div>
              <div className="flex justify-between items-center text-xs font-bold mb-1">
                <span>Days on Counter / In Pantry</span>
                <span className="text-secondary">{daysInKitchen} days</span>
              </div>
              <input
                type="range"
                min="0"
                max="14"
                value={daysInKitchen}
                onChange={(e) => setDaysInKitchen(Number(e.target.value))}
                className="w-full accent-secondary"
              />
              <div className="flex justify-between text-[10px] text-outline mt-1">
                <span>Purchased Today</span>
                <span>1 Week</span>
                <span>2 Weeks</span>
              </div>
            </div>

            {/* Analyze Action Button */}
            <button
              type="button"
              disabled={isScanning || !uploadedImage || isCameraActive}
              onClick={handleStartAnalysis}
              className="w-full py-3.5 px-6 rounded-full bg-primary hover:bg-primary-container text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 active:scale-98 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="material-symbols-outlined text-[20px]">{isScanning ? 'sync' : 'search_insights'}</span>
              <span>{isScanning ? 'Analyzing food...' : 'Analyze Food'}</span>
            </button>
          </div>
        </div>

        {/* RIGHT WORKBENCH: Scanning Loader, Structured Result Card, Compare State, Error State, or Idle Workbench (7 cols) */}
        <div className="lg:col-span-7">
          {/* STATE 3: SCANNING LOADER */}
          {isScanning && (
            <div className="p-8 rounded-3xl bg-white border border-surface-container-high/80 shadow-md space-y-6 text-center animate-in fade-in duration-200">
              <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
                <div className="absolute inset-0 rounded-full border-4 border-secondary-container border-t-secondary animate-spin" />
                <span className="text-3xl">🌿</span>
              </div>

              <div>
                <h3 className="text-lg font-extrabold text-primary">Analyzing your food...</h3>
                <p className="text-xs text-on-surface-variant mt-1">
                  Connecting optical cues with FoodFresh AI inference pipeline.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-surface-container-low/60 max-w-sm mx-auto text-xs text-on-surface-variant">
                Synthesizing visible surface features and storage environment inputs...
              </div>
            </div>
          )}

          {/* STATE 5: ANALYSIS ERROR STATE */}
          {analysisError && !isScanning && (
            <div className="p-8 rounded-3xl bg-surface-container-low border border-dashed border-red-300 text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-red-50 text-red-600 mx-auto flex items-center justify-center text-3xl shadow-2xs">
                <span className="material-symbols-outlined text-[32px]">error</span>
              </div>
              <h3 className="text-lg font-bold text-primary">Analysis could not be completed.</h3>
              <p className="text-xs text-on-surface-variant max-w-md mx-auto leading-relaxed">
                {analysisError || 'We encountered an issue preparing the analysis result for this photo.'}
              </p>

              <div className="flex items-center justify-center gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleStartAnalysis}
                  className="px-5 py-2.5 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container transition-colors cursor-pointer"
                >
                  Try Again
                </button>
                <button
                  type="button"
                  onClick={handleChooseAnotherImage}
                  className="px-5 py-2.5 rounded-full bg-white border border-surface-container-high text-primary text-xs font-bold hover:bg-surface-container-low transition-colors cursor-pointer"
                >
                  Choose Another Image
                </button>
              </div>
            </div>
          )}

          {/* STATE 4: STRUCTURED FOOD ANALYSIS RESULT CARD */}
          {analysisMode === 'single' && singleResult && !isScanning && !analysisError && (
            <div className="p-6 sm:p-8 rounded-3xl bg-white border border-surface-container-high/80 shadow-md space-y-6 animate-in fade-in duration-300">
              {/* Header / Pipeline Status */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-surface-container-low">
                <div>
                  <h2 className="text-xl sm:text-2xl font-extrabold text-primary tracking-tight">
                    Food Analysis Result
                  </h2>
                  <p className="text-xs text-on-surface-variant mt-0.5">
                    {singleResult.source === 'ml'
                      ? 'Inference via FoodFresh AI Master Hybrid Vision Pipeline • Shelf-Life pending'
                      : 'Pre-ML Integration Stage • Ready for Model Pipeline'}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold ${
                      singleResult.source === 'ml'
                        ? 'bg-secondary-container text-on-secondary-container'
                        : 'bg-surface-container-high text-on-surface-variant'
                    }`}
                  >
                    {singleResult.source === 'ml'
                      ? '✓ Hybrid Vision Pipeline'
                      : 'Model Disconnected'}
                  </span>
                </div>
              </div>

              {/* 1. Detected Food Card with Image Thumbnail & Scene Objects */}
              <div className="p-5 rounded-2xl bg-surface-container-low/70 border border-surface-container-high/60 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-secondary">
                    Detected Food
                  </h3>
                  <span className="text-[11px] font-semibold text-on-surface-variant">
                    {singleResult.rawConfidencePercent != null
                      ? `${singleResult.rawConfidencePercent.toFixed(1)}% recognition confidence`
                      : singleResult.recognitionConfidence != null
                      ? `${(singleResult.recognitionConfidence * 100).toFixed(1)}% recognition confidence`
                      : 'Not available yet'}
                  </span>
                </div>

                <div className="flex items-center gap-4 pt-1">
                  {singleResult.imageSrc && (
                    <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl overflow-hidden border border-surface-container-high shrink-0 shadow-xs bg-surface-container">
                      <img
                        src={singleResult.imageSrc}
                        alt={singleResult.detectedFood || 'Uploaded food'}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}

                  <div className="flex-1 min-w-0">
                    {singleResult.detectedFood ? (
                      <div>
                        <span className="text-2xl sm:text-3xl font-extrabold text-primary block truncate">
                          {singleResult.detectedFood}
                        </span>
                        <span className="text-xs text-secondary font-bold block mt-0.5">
                          {singleResult.rawConfidencePercent != null
                            ? `${singleResult.rawConfidencePercent.toFixed(1)}% recognition confidence`
                            : `${((singleResult.recognitionConfidence || 0) * 100).toFixed(1)}% recognition confidence`}
                        </span>
                      </div>
                    ) : singleResult.status === 'low_confidence' ? (
                      <div>
                        <span className="text-lg font-bold text-amber-800 block">
                          Low Confidence Recognition
                        </span>
                        <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
                          The model could not identify the produce with high certainty (confidence was below the 50% threshold). Please try a clearer angle or better lighting.
                        </p>
                      </div>
                    ) : (
                      <div>
                        <span className="text-xl sm:text-2xl font-extrabold text-on-surface-variant block">
                          Model not connected
                        </span>
                        <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
                          {singleResult.message || 'Food recognition model is disconnected. Awaiting integration of new pretrained model.'}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Grounding DINO Scene Objects Caption (Phase 8) */}
                <div className="pt-2 border-t border-surface-container-high/40 text-xs">
                  {singleResult.detectedObjects && singleResult.detectedObjects.length > 0 ? (
                    <div className="flex items-center gap-1.5 text-on-surface-variant">
                      <span className="material-symbols-outlined text-[15px] text-secondary">countertops</span>
                      <span>
                        <span className="font-semibold text-primary">Also detected: </span>
                        {singleResult.detectedObjects
                          .map((o) => o.label.charAt(0).toUpperCase() + o.label.slice(1))
                          .join(' · ')}
                      </span>
                    </div>
                  ) : (
                    <div className="text-[11px] text-on-surface-variant/75 italic">
                      No additional scene objects detected.
                    </div>
                  )}
                </div>
              </div>

              {/* 2. Top Predictions */}
              <div className="p-5 rounded-2xl bg-surface-container-low/70 border border-surface-container-high/60 space-y-2.5">
                <h3 className="text-xs font-bold uppercase tracking-wider text-secondary">
                  Top Predictions
                </h3>
                {singleResult.topPredictions && singleResult.topPredictions.length > 0 ? (
                  <div className="space-y-2">
                    {singleResult.topPredictions.map((pred, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between text-xs font-semibold p-2.5 rounded-xl bg-white border border-surface-container-high/60"
                      >
                        <span className="text-primary font-bold">
                          {idx + 1}. {pred.food}
                        </span>
                        <span className="text-secondary font-bold">
                          — {pred.percentage || `${(pred.confidence * 100).toFixed(1)}%`}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-3 rounded-xl bg-white/70 text-xs text-on-surface-variant italic">
                    Not available yet
                  </div>
                )}
              </div>

              {/* 3. Freshness, Shelf-Life & Eat First Priority Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                {/* Visible Freshness */}
                <div className="p-4 rounded-2xl bg-surface-container-low border border-surface-container-high/50 flex flex-col justify-between">
                  <div>
                    <h3 className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant block">
                      Estimated Visible Freshness
                    </h3>
                    <span className="text-base font-extrabold text-primary block mt-1">
                      {singleResult.freshness?.status === 'unavailable' || !singleResult.freshness?.label
                        ? 'Visible freshness unavailable'
                        : `${singleResult.freshness.label}${
                            singleResult.freshness.score != null
                              ? ` (${singleResult.freshness.score.toFixed(1)}%)`
                              : ''
                          }`}
                    </span>
                  </div>
                  <span className="text-[10px] text-on-surface-variant mt-2 block opacity-75">
                    {singleResult.freshness?.source || 'nathansekar/food-freshness-detector'}
                  </span>
                </div>

                {/* Shelf-Life */}
                <div className="p-4 rounded-2xl bg-surface-container-low border border-surface-container-high/50 flex flex-col justify-between">
                  <div>
                    <h3 className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant block">
                      Shelf-Life
                    </h3>
                    {singleResult.shelfLife?.status === 'available' && singleResult.shelfLife.remaining ? (
                      <div className="mt-1">
                        <span className="text-[11px] text-on-surface-variant block">Estimated remaining quality:</span>
                        <span className="text-base font-extrabold text-primary block">
                          {singleResult.shelfLife.remaining.minDays === singleResult.shelfLife.remaining.maxDays
                            ? `${singleResult.shelfLife.remaining.minDays} day${singleResult.shelfLife.remaining.minDays === 1 ? '' : 's'}`
                            : `${singleResult.shelfLife.remaining.minDays}–${singleResult.shelfLife.remaining.maxDays} days`}
                        </span>
                      </div>
                    ) : (
                      <div className="mt-1">
                        <span className="text-base font-extrabold text-primary block">Not available</span>
                        <span className="text-[11px] text-on-surface-variant block mt-0.5">
                          {singleResult.shelfLife?.reason || 'No FoodKeeper guidance found for this food.'}
                        </span>
                      </div>
                    )}
                  </div>
                  <span className="text-[10px] text-on-surface-variant mt-2 block opacity-75">
                    Source: {singleResult.shelfLife?.source || 'USDA FoodKeeper'}
                  </span>
                </div>

                {/* Eat First Priority */}
                <div className="p-4 rounded-2xl bg-surface-container-low border border-surface-container-high/50 flex flex-col justify-between">
                  <div>
                    <h3 className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant block">
                      Eat First Priority
                    </h3>
                    {singleResult.eatFirstPriority?.status === 'available' ? (
                      <div className="mt-1">
                        <div className="flex items-center gap-1.5">
                          <span
                            className={`px-2 py-0.5 rounded-lg text-xs font-black uppercase tracking-wider ${
                              singleResult.eatFirstPriority.priority === 'VERY_HIGH'
                                ? 'bg-rose-100 text-rose-800 border border-rose-300'
                                : singleResult.eatFirstPriority.priority === 'HIGH'
                                ? 'bg-amber-100 text-amber-800 border border-amber-300'
                                : singleResult.eatFirstPriority.priority === 'MEDIUM'
                                ? 'bg-yellow-100 text-yellow-800 border border-yellow-300'
                                : 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                            }`}
                          >
                            {singleResult.eatFirstPriority.priority.replace('_', ' ')}
                          </span>
                          {singleResult.eatFirstPriority.score != null && (
                            <span className="text-[10px] text-on-surface-variant font-bold">
                              ({singleResult.eatFirstPriority.score}/100)
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-on-surface-variant mt-1.5 leading-snug">
                          {singleResult.eatFirstPriority.reason}
                        </p>
                      </div>
                    ) : (
                      <div className="mt-1">
                        <span className="text-base font-extrabold text-primary block">Not available</span>
                        <span className="text-[11px] text-on-surface-variant block mt-0.5">
                          {singleResult.eatFirstPriority?.reason || 'Eat First requires an available shelf-life estimate.'}
                        </span>
                      </div>
                    )}
                  </div>
                  <span className="text-[10px] text-on-surface-variant mt-2 block opacity-75">
                    Deterministic decision rule
                  </span>
                </div>
              </div>


              {/* 4. Active Model Stack Info */}
              <div className="p-3.5 rounded-2xl bg-surface-container-low/50 border border-surface-container-high/40 text-[11px] text-on-surface-variant space-y-1">
                <div className="font-bold text-primary flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[14px] text-secondary">psychology</span>
                  <span>Active Hybrid Vision Stack:</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-0.5 text-[10px] pl-5">
                  <div>• Detector: <span className="font-mono text-outline">IDEA-Research/grounding-dino-base</span></div>
                  <div>• Semantic: <span className="font-mono text-outline">google/siglip2-base-patch16-224</span></div>
                  <div>• Specialist: <span className="font-mono text-outline">ibrahimdaud/raw-food-recognition-models</span></div>
                  <div>• Freshness: <span className="font-mono text-outline">nathansekar/food-freshness-detector</span></div>
                </div>
              </div>

              {/* Actions Footer */}
              <div className="pt-2 flex flex-wrap items-center justify-between gap-3 border-t border-surface-container-low">
                <button
                  type="button"
                  disabled={singleResult.source !== 'ml' || !singleResult.detectedFood}
                  onClick={handleSaveToHistory}
                  className="px-5 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-sm transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                  title={singleResult.source !== 'ml' ? 'Save to Pantry History will be enabled after ML model integration' : 'Save to Pantry History'}
                >
                  <span className="material-symbols-outlined text-[16px]">bookmark_add</span>
                  <span>Save to Pantry History</span>
                </button>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleChooseAnotherImage}
                    className="px-4 py-2.5 rounded-full bg-surface-container-low hover:bg-surface-container text-primary text-xs font-bold transition-all cursor-pointer"
                  >
                    Choose Another Image
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      if (singleResult) {
                        freshoBuddyService.setFoodContext({
                          detectedFood: singleResult.detectedFood || 'Produce Item',
                          foodName: singleResult.detectedFood || 'Produce Item',
                          recognitionConfidence: singleResult.rawConfidencePercent || (singleResult.recognitionConfidence ? singleResult.recognitionConfidence * 100 : null),
                          freshness: singleResult.freshness || { label: 'Uncertain' },
                          shelfLife: singleResult.shelfLife || null,
                          storageType: storageLocation,
                          daysStored: daysInKitchen,
                          imageSrc: singleResult.imageSrc,
                          analyzedAt: singleResult.analyzedAt,
                        });
                      }
                      navigate('/fresho-buddy');
                    }}
                    className="px-4 py-2.5 rounded-full bg-surface-container hover:bg-secondary-container hover:text-on-secondary-container text-primary text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
                  >
                    <img src={MASCOT_ASSETS.freshoBuddyUrl} alt="Buddy" className="w-4 h-4 object-contain" />
                    <span>Ask FreshoBuddy</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* MULTI-FOOD COMPARISON WORKBENCH */}
          {analysisMode === 'compare' && !isScanning && (
            <div className="p-8 rounded-3xl bg-white border border-surface-container-high/80 shadow-md space-y-4 text-center">
              <div className="w-16 h-16 rounded-full bg-surface-container mx-auto flex items-center justify-center text-3xl shadow-2xs">
                🥇
              </div>
              <h3 className="text-lg font-bold text-primary">Multi-Food Prioritization</h3>
              <p className="text-xs text-on-surface-variant max-w-md mx-auto leading-relaxed">
                Multi-item Eat First prioritization and comparison will be available when the shelf-life model and ranking pipeline are integrated.
              </p>
            </div>
          )}

          {/* STATE 2: IMAGE LOADED, READY FOR ANALYSIS */}
          {analysisMode === 'single' && uploadedImage && !isScanning && !singleResult && !analysisError && (
            <div className="p-10 rounded-3xl bg-surface-container-low/70 border border-dashed border-secondary/40 text-center space-y-3 animate-in fade-in duration-200">
              <div className="w-16 h-16 rounded-full bg-white mx-auto flex items-center justify-center text-3xl shadow-2xs">
                📷
              </div>
              <h3 className="text-base font-bold text-primary">Photo Ready for Analysis</h3>
              <p className="text-xs text-on-surface-variant max-w-sm mx-auto leading-relaxed">
                Your produce photo is ready. Adjust kitchen storage settings if desired, then click “Analyze Food” to begin inspection.
              </p>
            </div>
          )}

          {/* STATE 1: IDLE EMPTY STATE (NO IMAGE LOADED) */}
          {analysisMode === 'single' && !uploadedImage && !isScanning && !singleResult && !analysisError && (
            <div className="p-10 rounded-3xl bg-surface-container-low/60 border border-dashed border-surface-container-high text-center space-y-3">
              <div className="w-16 h-16 rounded-full bg-white mx-auto flex items-center justify-center text-3xl shadow-2xs">
                🌿
              </div>
              <h3 className="text-base font-bold text-primary">Produce Analysis Workbench Ready</h3>
              <p className="text-xs text-on-surface-variant max-w-sm mx-auto leading-relaxed">
                Upload or capture a food photo to begin. Then click “Analyze Food” to inspect.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Remove Food Confirmation Modal (Phase 10) */}
      {showRemoveConfirm && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4 animate-in fade-in duration-150"
        >
          <div className="bg-white rounded-3xl max-w-sm w-full p-6 shadow-xl border border-surface-container-high space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center">
              <span className="material-symbols-outlined text-[24px]">delete</span>
            </div>
            <div>
              <h3 className="text-base font-extrabold text-primary">Remove Food</h3>
              <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
                Remove this food from the current analysis?
              </p>
            </div>
            <div className="flex items-center justify-end gap-2.5 pt-2">
              <button
                type="button"
                id="cancel-remove-btn"
                onClick={() => setShowRemoveConfirm(false)}
                className="px-4 py-2 rounded-xl text-xs font-bold text-on-surface-variant hover:bg-surface-container transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                id="confirm-remove-btn"
                onClick={handleConfirmRemoveFood}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-rose-600 hover:bg-rose-700 text-white transition-colors cursor-pointer"
              >
                Remove Food
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalyzeFoodPage;

