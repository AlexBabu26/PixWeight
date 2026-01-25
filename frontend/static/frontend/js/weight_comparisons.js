/**
 * Weight comparison references for providing context to weight estimates
 */

const WEIGHT_REFERENCES = {
  ranges: [
    {
      min: 1,
      max: 10,
      items: [
        { name: "US Penny", weight: 2.5 },
        { name: "US Nickel", weight: 5 },
        { name: "Business Card", weight: 2 },
        { name: "Sheet of Paper", weight: 5 },
      ]
    },
    {
      min: 10,
      max: 50,
      items: [
        { name: "AAA Battery", weight: 11 },
        { name: "AA Battery", weight: 23 },
        { name: "Golf Ball", weight: 45 },
        { name: "Chicken Egg", weight: 50 },
      ]
    },
    {
      min: 50,
      max: 200,
      items: [
        { name: "Deck of Cards", weight: 94 },
        { name: "Baseball", weight: 145 },
        { name: "Smartphone", weight: 170 },
        { name: "Apple (medium)", weight: 182 },
        { name: "Orange", weight: 150 },
      ]
    },
    {
      min: 200,
      max: 500,
      items: [
        { name: "Can of Soda", weight: 330 },
        { name: "Basketball", weight: 450 },
        { name: "Water Bottle (500ml)", weight: 500 },
      ]
    },
    {
      min: 500,
      max: 1000,
      items: [
        { name: "Football (American)", weight: 420 },
        { name: "Hardcover Book", weight: 600 },
        { name: "Laptop (13 inch)", weight: 900 },
      ]
    },
    {
      min: 1000,
      max: 5000,
      items: [
        { name: "Bag of Sugar (2lb)", weight: 900 },
        { name: "Brick", weight: 2000 },
        { name: "Gallon of Milk", weight: 3780 },
        { name: "Bowling Ball", weight: 3600 },
        { name: "Chihuahua", weight: 2000 },
      ]
    },
    {
      min: 5000,
      max: 50000,
      items: [
        { name: "Beagle Dog", weight: 10000 },
        { name: "Golden Retriever", weight: 30000 },
        { name: "Microwave Oven", weight: 15000 },
        { name: "Mountain Bike", weight: 12000 },
      ]
    },
    {
      min: 50000,
      max: 999999999,
      items: [
        { name: "German Shepherd", weight: 35000 },
        { name: "Adult Human (average)", weight: 70000 },
        { name: "Refrigerator", weight: 90000 },
      ]
    }
  ]
};

/**
 * Get weight comparison items for a given weight in grams
 * @param {number} grams - Weight in grams
 * @returns {Array} Array of comparison objects with name, weight, and count
 */
function getWeightComparisons(grams) {
  if (!grams || grams <= 0) return [];
  
  // Find appropriate range
  const range = WEIGHT_REFERENCES.ranges.find(r => grams >= r.min && grams <= r.max);
  
  if (!range) {
    // Use last range for very heavy items
    const lastRange = WEIGHT_REFERENCES.ranges[WEIGHT_REFERENCES.ranges.length - 1];
    return lastRange.items.map(item => ({
      name: item.name,
      weight: item.weight,
      count: Math.round(grams / item.weight * 10) / 10,
      icon: getIconForItem(item.name)
    })).slice(0, 3);
  }
  
  // Return items from the range, with counts
  return range.items.map(item => ({
    name: item.name,
    weight: item.weight,
    count: Math.round(grams / item.weight * 10) / 10,
    icon: getIconForItem(item.name)
  })).slice(0, 3);
}

/**
 * Get the best single comparison (closest weight)
 * @param {number} grams - Weight in grams
 * @returns {Object|null} Best comparison object
 */
function getBestComparison(grams) {
  if (!grams || grams <= 0) return null;
  
  let bestMatch = null;
  let smallestDiff = Infinity;
  
  WEIGHT_REFERENCES.ranges.forEach(range => {
    range.items.forEach(item => {
      const diff = Math.abs(grams - item.weight);
      if (diff < smallestDiff) {
        smallestDiff = diff;
        bestMatch = {
          name: item.name,
          weight: item.weight,
          count: Math.round(grams / item.weight * 10) / 10,
          icon: getIconForItem(item.name)
        };
      }
    });
  });
  
  return bestMatch;
}

/**
 * Get a simple emoji icon for common items
 * @param {string} itemName - Name of the item
 * @returns {string} Emoji icon
 */
function getIconForItem(itemName) {
  const name = itemName.toLowerCase();
  
  if (name.includes('penny') || name.includes('nickel') || name.includes('coin')) return '🪙';
  if (name.includes('battery')) return '🔋';
  if (name.includes('paper') || name.includes('card')) return '📄';
  if (name.includes('golf')) return '⛳';
  if (name.includes('egg')) return '🥚';
  if (name.includes('baseball')) return '⚾';
  if (name.includes('basketball')) return '🏀';
  if (name.includes('football')) return '🏈';
  if (name.includes('phone') || name.includes('smartphone')) return '📱';
  if (name.includes('apple')) return '🍎';
  if (name.includes('orange')) return '🍊';
  if (name.includes('soda') || name.includes('can')) return '🥤';
  if (name.includes('water') || name.includes('bottle')) return '💧';
  if (name.includes('book')) return '📚';
  if (name.includes('laptop') || name.includes('computer')) return '💻';
  if (name.includes('sugar') || name.includes('bag')) return '🛍️';
  if (name.includes('brick')) return '🧱';
  if (name.includes('milk') || name.includes('gallon')) return '🥛';
  if (name.includes('bowling')) return '🎳';
  if (name.includes('dog') || name.includes('chihuahua') || name.includes('beagle') || 
      name.includes('retriever') || name.includes('shepherd')) return '🐕';
  if (name.includes('microwave') || name.includes('oven')) return '📟';
  if (name.includes('bike') || name.includes('bicycle')) return '🚴';
  if (name.includes('human') || name.includes('person') || name.includes('adult')) return '🧍';
  if (name.includes('refrigerator') || name.includes('fridge')) return '🧊';
  
  return '⚖️'; // Default scale icon
}

/**
 * Format weight comparison text
 * @param {Object} comparison - Comparison object
 * @returns {string} Formatted text
 */
function formatComparisonText(comparison) {
  if (!comparison) return "";
  
  if (comparison.count === 1) {
    return `About the same as 1 ${comparison.name}`;
  } else if (comparison.count < 1) {
    const percentage = Math.round(comparison.count * 100);
    return `About ${percentage}% of a ${comparison.name}`;
  } else {
    const rounded = Math.round(comparison.count);
    return `About the same as ${rounded} ${comparison.name}${rounded > 1 ? 's' : ''}`;
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    getWeightComparisons,
    getBestComparison,
    formatComparisonText,
    getIconForItem
  };
}
