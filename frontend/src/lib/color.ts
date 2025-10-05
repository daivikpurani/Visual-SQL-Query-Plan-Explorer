/**
 * Color utilities for heatmap visualization
 */

export const getHeatColor = (heatScore: number): string => {
  // Convert heat score (0-1) to a color gradient
  // 0 = green (good), 0.5 = yellow (moderate), 1 = red (bad)
  
  if (heatScore < 0.2) {
    return '#4CAF50' // Green
  } else if (heatScore < 0.4) {
    return '#8BC34A' // Light green
  } else if (heatScore < 0.6) {
    return '#FFEB3B' // Yellow
  } else if (heatScore < 0.8) {
    return '#FF9800' // Orange
  } else {
    return '#F44336' // Red
  }
}

export const getSeverityColor = (severity: 'low' | 'medium' | 'high' | 'critical'): string => {
  switch (severity) {
    case 'low':
      return '#4CAF50'
    case 'medium':
      return '#FF9800'
    case 'high':
      return '#FF5722'
    case 'critical':
      return '#F44336'
    default:
      return '#9E9E9E'
  }
}

export const getPerformanceColor = (value: number, threshold: number): string => {
  if (value <= threshold) {
    return '#4CAF50' // Good
  } else if (value <= threshold * 2) {
    return '#FF9800' // Warning
  } else {
    return '#F44336' // Critical
  }
}
