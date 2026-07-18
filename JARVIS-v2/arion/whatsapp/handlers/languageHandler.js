// handlers/languageHandler.js

const { 
  teluguPatterns, 
  teluguUnicodeRange,
  tenglishStructures,
  wordVariations
} = require('../utils/teluguPatterns');

let translate;
try {
  const { Translate } = require('@google-cloud/translate').v2;
  if (process.env.GOOGLE_TRANSLATE_API_KEY) {
    translate = new Translate({ 
      key: process.env.GOOGLE_TRANSLATE_API_KEY 
    });
  }
} catch (e) {
  console.warn("[LanguageHandler] Google Translate dependency missing or not configured.");
}

// Fuzzy match function
function fuzzyMatch(word, pattern, threshold = 0.8) {
  if (word === pattern) return true;
  if (Math.abs(word.length - pattern.length) > 3) return false;
  
  let matches = 0;
  const wordLower = word.toLowerCase();
  const patternLower = pattern.toLowerCase();
  const minLen = Math.min(wordLower.length, patternLower.length);
  
  for (let i = 0; i < minLen; i++) {
    if (wordLower[i] === patternLower[i]) matches++;
  }
  
  return (matches / Math.max(wordLower.length, patternLower.length)) >= threshold;
}

// Check word variations
function checkWordVariations(text) {
  const words = text.toLowerCase().split(/\s+/);
  
  for (const [baseWord, variations] of Object.entries(wordVariations)) {
    for (const variation of variations) {
      if (words.some(w => fuzzyMatch(w, variation))) {
        return true;
      }
    }
  }
  return false;
}

// Enhanced Language Detection
function detectLanguageType(text) {
  const lowerText = text.toLowerCase().trim();
  
  // Check Telugu Unicode
  if (teluguUnicodeRange.test(text)) return 'TELUGU_SCRIPT';
  
  // Check Tenglish structures
  const hasTenglishStructure = tenglishStructures
    .some(p => p.test(lowerText));
  
  // Check all pattern words with fuzzy matching
  const allPatterns = Object.values(teluguPatterns).flat();
  const matchCount = allPatterns
    .filter(word => {
      const wordLower = word.toLowerCase();
      // Exact check first
      if (lowerText.includes(wordLower)) return true;
      // Word-by-word fuzzy check for efficiency
      const msgWords = lowerText.split(/\s+/);
      return msgWords.some(w => fuzzyMatch(w, wordLower));
    }).length;
  
  // Check word variations
  const hasVariations = checkWordVariations(lowerText);
  
  if (hasTenglishStructure || matchCount >= 1 || hasVariations) {
    return 'TENGLISH';
  }
  
  if (/^[a-zA-Z0-9\s.,!?'"()\-@#]+$/.test(lowerText)) {
    return 'ENGLISH';
  }
  
  return 'UNKNOWN';
}

// Detect Intent with Scoring
function detectIntent(text) {
  const lowerText = text.toLowerCase();
  const scores = {};
  
  for (const [intent, patterns] of Object.entries(teluguPatterns)) {
    scores[intent] = patterns.filter(p => {
        const patternLower = p.toLowerCase();
        return lowerText.includes(patternLower) || fuzzyMatch(lowerText, patternLower);
    }).length;
  }
  
  const top = Object.entries(scores)
    .sort(([,a],[,b]) => b - a)
    .find(([,s]) => s > 0);
  
  return top ? top[0] : 'general';
}

// Detect All Intents
function detectMultipleIntents(text) {
  const lowerText = text.toLowerCase();
  const detected = [];
  
  for (const [intent, patterns] of Object.entries(teluguPatterns)) {
    const matched = patterns.filter(p => 
      lowerText.includes(p.toLowerCase()) || fuzzyMatch(lowerText, p.toLowerCase())
    );
    if (matched.length > 0) {
      detected.push({ intent, score: matched.length, matched });
    }
  }
  
  return detected.sort((a,b) => b.score - a.score);
}

// Detect Regional Dialect
function detectDialect(text) {
  const lowerText = text.toLowerCase();
  
  const rajahmundryWords = teluguPatterns.rajahmundrySlang || [];
  const hyderabadWords = teluguPatterns.hyderabadSlang || [];
  
  const rajahmundryScore = rajahmundryWords
    .filter(w => lowerText.includes(w.toLowerCase())).length;
  const hyderabadScore = hyderabadWords
    .filter(w => lowerText.includes(w.toLowerCase())).length;
  
  if (rajahmundryScore > hyderabadScore) return 'RAJAHMUNDRY';
  if (hyderabadScore > rajahmundryScore) return 'HYDERABAD';
  if (rajahmundryScore === hyderabadScore && rajahmundryScore > 0) return 'MIXED';
  return 'GENERAL';
}

// Translate to English
async function translateToEnglish(text) {
  try {
    if (!teluguUnicodeRange.test(text)) return text;
    if (!translate) return text;
    const [translation] = await translate.translate(text, 'en');
    return translation;
  } catch (error) {
    console.error('Translation error:', error);
    return text;
  }
}

// Translate to Telugu
async function translateToTelugu(text) {
  try {
    if (!translate) return text;
    const [translation] = await translate.translate(text, 'te');
    return translation;
  } catch (error) {
    console.error('Translation error:', error);
    return text;
  }
}

module.exports = {
  detectLanguageType,
  detectIntent,
  detectMultipleIntents,
  detectDialect,
  fuzzyMatch,
  translateToEnglish,
  translateToTelugu
};
