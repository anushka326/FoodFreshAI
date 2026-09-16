import { useState, useEffect } from 'react';
import { historyService } from '../services/historyService.js';
import { roadmapService } from '../services/roadmapService.js';

export function useFoodFresh() {
  const [history, setHistory] = useState([]);
  const [roadmap, setRoadmap] = useState({ active: [], completed: [], total: 0, completionRate: 0 });
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    const [histData, roadData] = await Promise.all([
      historyService.getHistoryItems(),
      roadmapService.getRoadmap(),
    ]);
    setHistory(histData);
    setRoadmap(roadData);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const deleteHistoryItem = async (id) => {
    await historyService.deleteHistoryItem(id);
    setHistory((prev) => prev.filter((item) => item.id !== id));
    const refreshed = await roadmapService.getRoadmap();
    setRoadmap(refreshed);
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
    roadmap,
    loading,
    refresh: loadData,
    deleteHistoryItem,
    markRoadmapEaten,
    undoRoadmapItem,
  };
}

export default useFoodFresh;
