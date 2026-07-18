// handlers/aiHandler.js
// NOTE: The old ARION TCP Core (port 5006) no longer exists.
// All responses now flow through the NEXUS Brain queue pipeline:
//   whatsapp_listener → incoming.json → Python WhatsAppBridge → brain → outgoing.json → reply

require('dotenv').config();
const path = require('path');
const fs   = require('fs');
const { memoryDB } = require('../config/database');

// Queue paths (same as whatsapp_listener.js)
const BRIDGE_QUEUE_DIR = path.resolve(__dirname, '../../data/bridge_queue');
const INCOMING_FILE    = path.join(BRIDGE_QUEUE_DIR, 'incoming.json');
const INCOMING_LOCK    = path.join(BRIDGE_QUEUE_DIR, 'incoming_writing.json');
const OUTGOING_FILE    = path.join(BRIDGE_QUEUE_DIR, 'outgoing.json');

function ensureQueue() {
  if (!fs.existsSync(BRIDGE_QUEUE_DIR)) fs.mkdirSync(BRIDGE_QUEUE_DIR, { recursive: true });
  if (!fs.existsSync(INCOMING_FILE)) fs.writeFileSync(INCOMING_FILE, '[]');
}

/**
 * Writes message to the NEXUS incoming queue.
 * The Python WhatsAppBridge polls this file and sends replies via outgoing.json.
 * Returns null — reply comes asynchronously via pollOutgoingQueue in whatsapp_listener.js.
 */
async function generateAIResponse(params) {
  const {
    phoneNumber,
    contactName,
    message,
    translatedMessage,
    languageType,
    dialect,
    intent,
    intents
  } = params;

  try {
    console.log(`🧠 [Bridge] Routing to NEXUS Brain via queue...`);

    ensureQueue();
    let existing = [];
    try { existing = JSON.parse(fs.readFileSync(INCOMING_FILE, 'utf8')); } catch(e) {}

    existing.push({
      source:      'whatsapp',
      jid:         phoneNumber,
      from:        phoneNumber,
      contact:     phoneNumber,
      text:        message,             // ← clean user text only, no fallback contamination
      name:        contactName,
      is_owner:    false,
      language:    languageType,
      dialect:     dialect,
      intent:      intent,
      timestamp:   Date.now(),
      media_path:  params.mediaPath || null
    });

    // Atomic write
    fs.writeFileSync(INCOMING_LOCK, JSON.stringify(existing, null, 2));
    fs.renameSync(INCOMING_LOCK, INCOMING_FILE);

    console.log(`✅ [Bridge] Message queued for NEXUS Brain.`);

    // Return null — reply arrives asynchronously via outgoing.json
    // whatsapp_listener.js pollOutgoingQueue() will send it.
    return null;

  } catch (error) {
    console.error('❌ [Bridge] Queue write error:', error.message);
    // Only use fallback when we literally cannot write to disk
    const fallbacks = {
      TELUGU_SCRIPT:       'క్షమించండి, మళ్ళీ చెప్పండి!',
      TENGLISH_RAJAHMUNDRY: 'Sare ra, ippudu konchem busy ga unna! Malli try cheseyyi ra.',
      TENGLISH_HYDERABAD:  'Yaar sorry, abhi thoda busy hoon! Phir se try karo yaar.',
      TENGLISH:            'Sorry, konchem delay aindi! Malli cheppandi please.',
      ENGLISH:             'Sorry! I missed that. Can you repeat please?'
    };
    const dialectKey = dialect === 'RAJAHMUNDRY' ? 'TENGLISH_RAJAHMUNDRY'
                     : dialect === 'HYDERABAD'    ? 'TENGLISH_HYDERABAD'
                     : languageType;
    return fallbacks[dialectKey] || fallbacks.ENGLISH;
  }
}

/**
 * GET CONVERSATION STATS — stub (no TCP core anymore)
 */
async function getConversationStats(phoneNumber) {
  return {};
}

module.exports = { 
  generateAIResponse, 
  getConversationStats
};


module.exports = { 
  generateAIResponse, 
  getConversationStats
};
