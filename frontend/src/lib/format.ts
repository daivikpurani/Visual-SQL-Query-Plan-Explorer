/**
 * Formatting utilities for numbers, durations, and other values
 */

export const formatDuration = (milliseconds: number): string => {
  if (milliseconds < 1) {
    return `${(milliseconds * 1000).toFixed(1)}μs`
  } else if (milliseconds < 1000) {
    return `${milliseconds.toFixed(1)}ms`
  } else {
    return `${(milliseconds / 1000).toFixed(2)}s`
  }
}

export const formatNumber = (num: number): string => {
  if (num < 1000) {
    return num.toString()
  } else if (num < 1000000) {
    return `${(num / 1000).toFixed(1)}K`
  } else if (num < 1000000000) {
    return `${(num / 1000000).toFixed(1)}M`
  } else {
    return `${(num / 1000000000).toFixed(1)}B`
  }
}

export const formatBytes = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${value.toFixed(decimals)}%`
}

export const formatCost = (cost: number): string => {
  return formatNumber(cost)
}

export const formatRows = (rows: number): string => {
  return formatNumber(rows)
}

export const formatBlocks = (blocks: number): string => {
  return formatNumber(blocks)
}
