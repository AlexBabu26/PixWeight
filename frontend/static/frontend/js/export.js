/**
 * CSV export functionality for session history
 */

/**
 * Convert sessions data to CSV format and trigger download
 * @param {Array} sessions - Array of session objects
 * @param {string} filename - Output filename (default: 'weight_estimates.csv')
 */
function exportHistoryToCSV(sessions, filename = 'weight_estimates.csv') {
  if (!sessions || sessions.length === 0) {
    alert('No data to export');
    return;
  }
  
  // Define CSV headers
  const headers = [
    'Date',
    'Object',
    'Category',
    'Status',
    'Estimated Weight (g)',
    'Weight Range',
    'Confidence (%)',
    'Rationale'
  ];
  
  // Convert sessions to CSV rows
  const rows = sessions.map(session => {
    const estimate = session.estimate;
    const date = new Date(session.created_at).toLocaleString();
    const object = session.object_label || 'Unknown';
    const category = session.object_json?.detected_category || 'general';
    const status = session.status;
    
    if (!estimate) {
      return [
        date,
        object,
        category,
        status,
        'N/A',
        'N/A',
        'N/A',
        'No estimate yet'
      ];
    }
    
    const weight = estimate.value_grams.toFixed(1);
    const range = `${estimate.min_grams.toFixed(1)} - ${estimate.max_grams.toFixed(1)}`;
    const confidence = Math.round(estimate.confidence * 100);
    const rationale = estimate.rationale || '';
    
    return [
      date,
      object,
      category,
      status,
      weight,
      range,
      confidence,
      rationale
    ];
  });
  
  // Build CSV content
  let csvContent = headers.join(',') + '\n';
  
  rows.forEach(row => {
    // Escape commas and quotes in fields
    const escapedRow = row.map(field => {
      const str = String(field);
      // If field contains comma, quote, or newline, wrap in quotes and escape quotes
      if (str.includes(',') || str.includes('"') || str.includes('\n')) {
        return '"' + str.replace(/"/g, '""') + '"';
      }
      return str;
    });
    csvContent += escapedRow.join(',') + '\n';
  });
  
  // Create blob and trigger download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // Clean up
  URL.revokeObjectURL(url);
}

/**
 * Export statistics summary to text file
 * @param {Object} statistics - Statistics object
 * @param {string} filename - Output filename
 */
function exportStatisticsToText(statistics, filename = 'statistics.txt') {
  if (!statistics) {
    alert('No statistics to export');
    return;
  }
  
  let content = 'WEIGHT ESTIMATION STATISTICS\n';
  content += '============================\n\n';
  content += `Generated: ${new Date().toLocaleString()}\n\n`;
  content += `Total Sessions: ${statistics.total_sessions}\n`;
  content += `Completed: ${statistics.completed_sessions}\n`;
  content += `Pending: ${statistics.pending_sessions}\n`;
  content += `Average Confidence: ${statistics.average_confidence}%\n\n`;
  
  if (statistics.category_breakdown && Object.keys(statistics.category_breakdown).length > 0) {
    content += 'Category Breakdown:\n';
    content += '-------------------\n';
    Object.entries(statistics.category_breakdown).forEach(([category, count]) => {
      content += `${category.charAt(0).toUpperCase() + category.slice(1)}: ${count}\n`;
    });
  }
  
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
}
