import { useState, useEffect } from 'react';
import { historyService } from '../services/historyService.js';
import { roadmapService } from '../services/roadmapService.js';

export function useFoodFresh() {
  const [history, setHistory] = useState([]);
  const [archivedHistory, setArchivedHistory] = useState([]);
  const [activityLogs, setActivityLogs] = useState([]);
  const [totalTracked, setTotalTracked] = useState(0);
  const [roadmap, setRoadmap] = useState({ active: [], completed: [], total: 0, completionRate: 0 });
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    const bundle = await historyService.getHistoryData();
    const roadData = await roadmapService.rebuildFromPantryHistory(bundle.items);
    setHistory(bundle.items || []);
    setArchivedHistory(bundle.archivedItems || []);
    setActivityLogs(bundle.activityLogs || []);
    setTotalTracked(bundle.totalTracked || ((bundle.items || []).length + (bundle.archivedItems || []).length));
    setRoadmap(roadData);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const deleteHistoryItem = async (id, options = {}) => {
    await historyService.deleteHistoryItem(id, options);
    await loadData();
  };

  const restoreHistoryItem = async (id) => {
    await historyService.restoreHistoryItem(id);
    await loadData();
  };

  const permanentlyDeleteHistoryItem = async (id) => {
    await historyService.permanentlyDeleteHistoryItem(id);
    await loadData();
  };

  const markRoadmapEaten = async (id) => {
    const updated = await roadmapService.markAsEaten(id);
    const refreshed = await roadmapService.getRoadmap();
    setRoadmap(refreshed);
  };

  const undoRoadmapItem = async (id) => {
    await roadmapService.undoEaten(id);
    const refreshed = await roadmapService.getRoadmap();
    setRoadmap(refreshed);
  };

  return {
    history,
    archivedHistory,
    activityLogs,
    totalTracked,
    roadmap,
    loading,
    refresh: loadData,
    deleteHistoryItem,
    restoreHistoryItem,
    permanentlyDeleteHistoryItem,
    markRoadmapEaten,
    undoRoadmapItem,
  };
}

export default useFoodFresh;
