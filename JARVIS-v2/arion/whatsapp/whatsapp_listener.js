// arion/whatsapp/whatsapp_listener.js
require('dotenv').config();
process.removeAllListeners('warning');

const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { connectDB } = require('./config/database');
const net = require('net');
const fs = require('fs');
const path = require('path');

// ============================================
// IMPORTS (ARION HANDLERS)
// ============================================
const { 
  detectLanguageType, 
  detectIntent,
  detectMultipleIntents,
  detectDialect,
  translateToEnglish 
} = require('./handlers/languageHandler');

const { 
  generateAIResponse,
  getConversationStats 
} = require('./handlers/aiHandler');

// ============================================
// CONFIG & STORAGE
// ============================================
const WHITELIST_FILE = path.join(__dirname, 'whitelist.json');
const BLOCKED_FILE   = path.join(__dirname, 'blocked.json');
const ADMIN_NUMBER   = process.env.ADMIN_NUMBER + '@c.us';
const PYTHON_PORT    = parseInt(process.env.ARION_PORT || process.env.PYTHON_PORT || '5006');

// Queue file locations (must match WhatsAppBridge python paths)
// __dirname = arion/whatsapp  →  ../data = arion/data  ✓
const BRIDGE_QUEUE_DIR = path.resolve(__dirname, '../data/bridge_queue');
const INCOMING_FILE    = path.join(BRIDGE_QUEUE_DIR, 'incoming.json');
const INCOMING_LOCK    = path.join(BRIDGE_QUEUE_DIR, 'incoming_writing.json');
const OUTGOING_FILE    = path.join(BRIDGE_QUEUE_DIR, 'outgoing.json');
const OUTGOING_DONE    = path.join(BRIDGE_QUEUE_DIR, 'outgoing_processing.json');
const TEMP_MEDIA_DIR   = path.join(BRIDGE_QUEUE_DIR, 'temp_media');

function ensureQueue() {
  if (!fs.existsSync(BRIDGE_QUEUE_DIR)) fs.mkdirSync(BRIDGE_QUEUE_DIR, { recursive: true });
  if (!fs.existsSync(TEMP_MEDIA_DIR)) fs.mkdirSync(TEMP_MEDIA_DIR, { recursive: true });
  if (!fs.existsSync(INCOMING_FILE)) fs.writeFileSync(INCOMING_FILE, '[]');
}

function writeToQueue(data) {
  try {
    ensureQueue();
    let existing = [];
    try { existing = JSON.parse(fs.readFileSync(INCOMING_FILE, 'utf8')); } catch(e) {}
    existing.push(data);
    // Atomic write: write to temp then rename
    fs.writeFileSync(INCOMING_LOCK, JSON.stringify(existing, null, 2));
    fs.renameSync(INCOMING_LOCK, INCOMING_FILE);
    return true;
  } catch(e) {
    console.error('[Bridge] Queue write error:', e.message);
    return false;
  }
}


// Connect to MongoDB
connectDB();

function loadWhitelist() {
  try {
    if (fs.existsSync(WHITELIST_FILE)) {
      return JSON.parse(fs.readFileSync(WHITELIST_FILE, 'utf8'));
    }
  } catch(e) {}
  return { enabled: true, numbers: [], names: [], settings: {} };
}

function loadBlocked() {
  try {
    if (fs.existsSync(BLOCKED_FILE)) {
      return JSON.parse(fs.readFileSync(BLOCKED_FILE, 'utf8'));
    }
  } catch(e) {}
  return { numbers: [], reasons: {} };
}

function saveWhitelist(wl) {
  fs.writeFileSync(WHITELIST_FILE, JSON.stringify(wl, null, 2));
}

function saveBlocked(bl) {
  fs.writeFileSync(BLOCKED_FILE, JSON.stringify(bl, null, 2));
}

// ============================================
// MESSAGE FILTERS
// ============================================
async function shouldReply(message, contact, whitelist, blocked) {
  const phone = message.from;
  const phoneClean = phone.replace('@c.us', '').replace('@g.us', '');
  const contactName = contact?.pushname || contact?.name || '';
  const isContact = contact?.isMyContact || false;

  // 1. Skip own messages
  if (message.fromMe) return { reply: false, reason: 'own_message' };

  // 2. Skip status/broadcast/newsletter
  if (message.isStatus || phone.includes('@broadcast') || phone.includes('@newsletter') || phone.includes('@lid')) {
    return { reply: false, reason: 'broadcast' };
  }

  // 3. Skip groups (unless enabled)
  if (phone.includes('@g.us')) {
    if (!whitelist.settings.reply_to_groups) return { reply: false, reason: 'group_message' };
  }

  // 4. Skip blocked
  if (blocked.numbers.includes(phoneClean)) {
    return { reply: false, reason: `blocked: ${blocked.reasons[phoneClean] || 'manual'}` };
  }

  // 5. Whitelist Logic
  if (whitelist.enabled) {
    const isNumberWhitelisted = whitelist.numbers.includes(phoneClean);
    const isNameWhitelisted = whitelist.names.some(name => contactName.toLowerCase().includes(name.toLowerCase()));

    if (whitelist.settings.reply_to_saved_contacts_only) {
      if (!isContact && !isNumberWhitelisted && !isNameWhitelisted) {
        return { 
          reply: false, 
          reason: 'not_saved_contact', 
          notify_admin: whitelist.settings.unknown_contact_action === 'notify'
        };
      }
    } else {
      if (!isNumberWhitelisted && !isNameWhitelisted) {
        return { reply: false, reason: 'not_whitelisted', notify_admin: true };
      }
    }
  }

  return { reply: true, reason: 'allowed' };
}

function detectSpam(text) {
  if (!text) return { isSpam: false };
  const lower = text.toLowerCase();
  const patterns = [
    { pattern: /earn.*per.*day/i, reason: 'earn money spam' },
    { pattern: /click.*link.*earn/i, reason: 'click link spam' },
    { pattern: /free.*recharge/i, reason: 'free recharge spam' },
    { pattern: /whatsapp.*prize/i, reason: 'prize spam' }
  ];
  for (const { pattern, reason } of patterns) {
    if (pattern.test(lower)) return { isSpam: true, reason };
  }
  return { isSpam: false };
}

// ============================================
// ADMIN COMMANDS
// ============================================
async function handleAdminCommand(message, body, phoneClean) {
  const upper = body.toUpperCase().trim();
  
  // APPROVE [number]
  const approveMatch = body.match(/^APPROVE\s+(\d+)/i);
  if (approveMatch) {
    const num = approveMatch[1].replace(/\D/g, '');
    const wl = loadWhitelist();
    if (!wl.numbers.includes(num)) {
      wl.numbers.push(num);
      saveWhitelist(wl);
    }
    return `Approved: ${num}. Added to whitelist.`;
  }

  // BLOCK [number]
  const blockMatch = body.match(/^BLOCK\s+(\d+)/i);
  if (blockMatch) {
    const num = blockMatch[1].replace(/\D/g, '');
    const bl = loadBlocked();
    if (!bl.numbers.includes(num)) {
      bl.numbers.push(num);
      bl.reasons[num] = 'admin_blocked';
      saveBlocked(bl);
    }
    return `Blocked: ${num}.`;
  }

  if (upper === 'STATUS') {
    const wl = loadWhitelist();
    const bl = loadBlocked();
    return `ARION Status\nWL: ${wl.enabled ? 'ON' : 'OFF'}\nSaved-Only: ${wl.settings.reply_to_saved_contacts_only ? 'ON' : 'OFF'}\nNumbers: ${wl.numbers.length}\nBlocked: ${bl.numbers.length}`;
  }

  // AGENTS — quick local list (no Python round-trip)
  if (upper === 'AGENTS' || upper === 'FLEET') {
    return [
      '🤖 *JARVIS Agent Fleet*',
      '@arion  — The Companion (Tenglish buddy)',
      '@atlas  — The Scholar (research)',
      '@axiom  — The Architect (system design)',
      '@cleo   — The Archivist (knowledge)',
      '@vega   — The Analyst (data)',
      '@stack  — The Coder (full-stack)',
      '@terra  — The Planner (tasks)',
      '@vera   — The Counselor (emotional)',
      '@hank   — The Enforcer (security)',
      '@iris   — The Observer (vision)',
      '@nova   — The Innovator (tech)',
      '@zero   — The Pioneer (R&D)',
      '...and 11 more',
      '',
      '_Use: @<agent> <message>  or  call @<agent>_'
    ].join('\n');
  }

  // HELP — show WhatsApp command reference
  if (upper === 'HELP' || upper === 'COMMANDS') {
    return [
      '🤖 *JARVIS WhatsApp Bridge — Commands*',
      '',
      '*Agent Chat*',
      '  @<agent> <msg>  — one-shot message',
      '  call @<agent>   — focused session',
      '  end session     — back to main brain',
      '',
      '*System*',
      '  /status   /agents   /progress',
      '  /mode fleet | /mode single',
      '',
      '*Tasks*',
      '  /task add <text>',
      '  /task list',
      '  /task done <id>',
      '  /task delete <id>',
      '',
      '*Reminders*',
      '  /remind HH:MM <text>',
      '  /remind list',
      '  /remind cancel <id>',
      '',
      '*Memory*',
      '  /memory save <fact>',
      '  /memory recall <query>',
      '  /know <fact>',
      '',
      '🎙️ Voice note = hands-free conversation'
    ].join('\n');
  }

  return null;
}

// ============================================
// WHATSAPP CLIENT
// ============================================
const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: [
      '--no-sandbox', 
      '--disable-setuid-sandbox', 
      '--disable-dev-shm-usage',
      '--disable-extensions',
      '--disable-gpu',
      '--no-first-run',
      '--no-zygote',
      '--single-process'
    ],
    handleSIGINT: false,
    handleSIGTERM: false,
    handleSIGHUP: false
  },
  authTimeoutMs: 120000,
  takeoverOnTimeout: true,
  takeoverTimeoutMs: 5000,
  webVersionCache: {
    type: 'remote',
    remotePath: 'https://raw.githubusercontent.com/wppconnect-team/wa-version/main/html/2.3000.1018260275-alpha.html'
  }
});

let isReady = false;

// READY WATCHDOG: Restart if ready doesn't fire in 5 mins
const readyTimeout = setTimeout(() => {
    if (!isReady) {
        console.log('⚠️  [WhatsApp] Ready event timed out. Session might be too large (~1GB). Restarting client...');
        client.initialize().catch(e => console.error('Restart failed:', e.message));
    }
}, 300000); 

client.on('qr', qr => {
  console.log('\n📱 [WhatsApp] Scan QR Code (Required for session):');
  qrcode.generate(qr, { small: true });
});

client.on('loading_screen', (percent, message) => {
  console.log(`\n⏳ [WhatsApp] Syncing Data: ${percent}% - ${message}`);
});

client.on('authenticated', () => {
  console.log('\n🔓 [WhatsApp] Authenticated! Now syncing session data (Large session detected)...');
});

client.on('auth_failure', msg => {
  console.error('\n❌ [WhatsApp] Auth failure:', msg);
});

client.on('ready', () => {
  isReady = true;
  clearTimeout(readyTimeout);
  console.log('\n✅ WhatsApp Bridge Ready with Security Layer!');
  console.log(`📡 Owner number : ${ADMIN_NUMBER}`);
  console.log(`📂 Queue folder : ${BRIDGE_QUEUE_DIR}`);
});

// ============================================
// OWNER SELF-CHAT → ARION  
// 'message' event does NOT fire for messages you send to yourself.
// 'message_create' catches ALL sent messages — we filter to self-chat only.
// How to use: Open WhatsApp → tap your own name → "Message Yourself" → send anything.
// ============================================
client.on('message_create', async (message) => {
  try {
    if (!message.fromMe) return;           // Only care about messages WE sent

    const selfJid = client.info?.wid?._serialized;
    if (!selfJid) return;

    // Robust self-chat detection: handles variant JID formats
    const isSelf = (message.to === selfJid) || 
                   (message.from === selfJid && message.to === message.from) ||
                   (message.to.split('@')[0] === selfJid.split('@')[0]);

    if (!isSelf) return;

    const body = message.body?.trim() || '';

    // ── OWNER VOICE NOTE DETECTION ────────────────────────────────────────
    // Voice notes sent to self have an empty body — do NOT drop them early.
    // Download and route through the bridge queue just like text messages.
    let mediaPath = null;
    if (message.hasMedia) {
      try {
        const media = await message.downloadMedia();
        if (media && (media.mimetype.startsWith('audio/') || media.mimetype.startsWith('video/ogg'))) {
          ensureQueue();
          const ext = media.mimetype.includes('ogg') ? 'ogg' : 'mp3';
          const filename = `owner_voice_${Date.now()}.${ext}`;
          mediaPath = path.join(TEMP_MEDIA_DIR, filename);
          fs.writeFileSync(mediaPath, media.data, 'base64');
          console.log(`[Owner Self-Chat] 🎤 Downloaded voice note: ${filename}`);
        }
      } catch (e) {
        console.error('[Owner Self-Chat] Media download error:', e.message);
      }
    }
    // ──────────────────────────────────────────────────────────────────────

    // Skip if neither text nor voice note (e.g. image, sticker)
    if (!body && !mediaPath) return;

    // ECHO FILTER: Don't process our own automated text replies
    if (body && global.lastSentMessage === body) {
        return; 
    }

    console.log(`\n${'='.repeat(40)}`);
    if (mediaPath) {
      console.log(`👤 [Owner Self-Chat] Voice note detected → queuing for transcription`);
    } else {
      console.log(`👤 [Owner Self-Chat] Processing: "${body.substring(0, 40)}${body.length > 40 ? '...' : ''}"`);
    }

    const payload = {
      source:     'whatsapp',
      jid:        selfJid,
      from:       ADMIN_NUMBER,
      contact:    ADMIN_NUMBER,
      text:       body,
      name:       'Owner',
      is_owner:   true,
      isOwner:    true,
      timestamp:  Date.now(),
      media_path: mediaPath || null,
      // Command metadata flags for the Python router
      is_command: body.startsWith('/'),
      is_mention: body.startsWith('@'),
      is_session_cmd: /^(call|talk to|connect|end session|end chat|exit|bye)\s*(@\w+)?$/i.test(body.trim()),
    };

    const sent = writeToQueue(payload);

    if (sent) {
      console.log(`[Bridge] ✅ Message written to ${INCOMING_FILE}`);
    } else {
      console.log(`[Bridge] ❌ FAILED to write to queue file`);
    }
  } catch(e) {
    console.error('[Owner Self-Chat] Error:', e.message);
  }
});

// ============================================
// MAIN MESSAGE HANDLER — incoming messages from OTHER people
// (Self-chat is handled separately above via message_create)
// ============================================
client.on('message', async (message) => {
  try {
    const contact = await message.getContact();
    const senderName = contact?.pushname || contact?.name || 'Unknown';
    const phoneNumber = message.from;
    const phoneClean = phoneNumber.replace('@c.us', '').replace('@g.us', '');
    const body = message.body?.trim() || '';
    const isFromMe = message.fromMe;
    const isAdmin = phoneNumber === ADMIN_NUMBER || isFromMe;

    console.log('\n' + '='.repeat(40));
    console.log(`From: ${senderName} (${phoneClean}) | Me: ${isFromMe}`);

    // Drop messages we sent (self-chat is handled by message_create above)
    if (isFromMe) {
      if (body) {
        const cmdResponse = await handleAdminCommand(message, body, phoneClean);
        if (cmdResponse) { await message.reply(cmdResponse); }
      }
      return;
    }

    // ── ADMIN COMMANDS ────────────────────────────────────────────────────
    if (isAdmin && body) {
      const cmdResponse = await handleAdminCommand(message, body, phoneClean);
      if (cmdResponse) { await message.reply(cmdResponse); return; }
    }

    // WHITELIST FILTER
    const whitelist = loadWhitelist();
    const filter = await shouldReply(message, contact, whitelist, loadBlocked());

    if (!filter.reply) {
      console.log(`Blocked: ${filter.reason}`);
      if (filter.notify_admin && isReady) {
        const alert = `ARION Alert\nUnknown Message\nUser: ${senderName}\nPhone: ${phoneClean}\nMsg: ${body.substring(0, 100)}\nApprove? APPROVE ${phoneClean}`;
        await client.sendMessage(ADMIN_NUMBER, alert);
      }
      return;
    }

    // SPAM FILTER
    const spam = detectSpam(body);
    if (spam.isSpam) {
      const bl = loadBlocked();
      if (!bl.numbers.includes(phoneClean)) {
        bl.numbers.push(phoneClean);
        bl.reasons[phoneClean] = spam.reason;
        saveBlocked(bl);
      }
      console.log(`Auto-blocked spam: ${spam.reason}`);
      return;
    }

    // PROCESS (Whitelisted)
    const languageType = detectLanguageType(body);
    const dialect = detectDialect(body);
    const intent = detectIntent(body);
    const intents = detectMultipleIntents(body);

    // ── MEDIA HANDLING (Voice Notes) ──────────────────────────────────────
    let mediaPath = null;
    if (message.hasMedia) {
      try {
        const media = await message.downloadMedia();
        if (media && (media.mimetype.startsWith('audio/') || media.mimetype.startsWith('video/ogg'))) {
          // It's a voice note
          const ext = media.mimetype.split('/')[1].split(';')[0] === 'ogg' ? 'ogg' : 'mp3';
          const filename = `voice_${Date.now()}.${ext}`;
          mediaPath = path.join(TEMP_MEDIA_DIR, filename);
          fs.writeFileSync(mediaPath, media.data, 'base64');
          console.log(`[Media] Downloaded Voice Note: ${filename}`);
        }
      } catch (e) {
        console.error('[Media] Failed to download media:', e.message);
      }
    }
    // ──────────────────────────────────────────────────────────────────────

    let translatedText = body;
    if (languageType === 'TELUGU_SCRIPT' && body) {
      translatedText = await translateToEnglish(body);
    }

    console.log(`Processing: [${languageType}] [${dialect}] [${intent}] Media: ${mediaPath ? 'Yes' : 'No'}`);

    const aiResponse = await generateAIResponse({
      phoneNumber,
      contactName: senderName,
      message: body,
      translatedMessage: translatedText,
      languageType,
      dialect,
      intent,
      intents,
      mediaPath: mediaPath
    });

    // null = response is coming async via the NEXUS brain queue (outgoing.json)
    // Only do an immediate reply if we got a sync string back (disk-write failure fallback)
    if (aiResponse !== null) {
      await message.reply(aiResponse);
      console.log(`Replied (fallback): ${aiResponse.substring(0, 50)}...`);
    } else {
      console.log(`✅ [Bridge] Message queued. Reply will arrive via NEXUS Brain.`);
    }

    // Admin alert: only send the raw message text, NOT the AI reply
    // (including the reply caused "poisoned context" feedback loops)
    if (!isAdmin && isReady) {
      const alert = `ARION Alert\nFrom: ${senderName}\nLang: ${languageType}\nMsg: ${body.substring(0, 100)}`;
      await client.sendMessage(ADMIN_NUMBER, alert);
    }

  } catch(e) {
    if (e.message?.includes('description')) return;
    console.error('Core Error:', e.message);
  }
});

// ── OUTBOUND QUEUE POLLING ────────────────────────────────────────────────
// Periodically checks if the Python brain has written replies to outgoing.json
// Uses atomic rename to prevent reading while Python is writing.
async function pollOutgoingQueue() {
  try {
    if (!fs.existsSync(OUTGOING_FILE)) return;

    // Atomic Move
    try {
      if (fs.existsSync(OUTGOING_DONE)) fs.unlinkSync(OUTGOING_DONE);
      fs.renameSync(OUTGOING_FILE, OUTGOING_DONE);
    } catch (e) { return; } // Python might be writing, skip

    const content = fs.readFileSync(OUTGOING_DONE, 'utf8');
    if (!content) return;

    const messages = JSON.parse(content);
    if (messages && messages.length > 0) {
      console.log(`[Bridge] 📤 Found ${messages.length} outgoing messages.`);
      
      for (const msg of messages) {
        if (isReady && msg.target) {
          try {
            // Check if there is a voice note / audio file attached
            if (msg.media_path && fs.existsSync(msg.media_path)) {
               const media = MessageMedia.fromFilePath(msg.media_path);
               // Send as Voice Note (audio native)
               await client.sendMessage(msg.target, media, { sendAudioAsVoice: true });
               console.log(`[Bridge] Sent VOICE NOTE to ${msg.target}`);
               // Optionally delete after sending
               try { fs.unlinkSync(msg.media_path); } catch(e){}
            } 
            
            // Also send text if present
            if (msg.text) {
               global.lastSentMessage = msg.text.trim();
               await client.sendMessage(msg.target, msg.text);
               console.log(`[Bridge] Sent TEXT to ${msg.target}: "${msg.text.substring(0, 30)}..."`);
            }
          } catch(err) {
            console.error(`[Bridge] Error sending to ${msg.target}:`, err.message);
          }
        }
      }
    }

    if (fs.existsSync(OUTGOING_DONE)) fs.unlinkSync(OUTGOING_DONE);
  } catch (e) {
    console.error('[Bridge] Outbound Poll Error:', e.message);
  }
}

// Start Polling Loop
setInterval(pollOutgoingQueue, 1000);

// ── HEARTBEAT ─────────────────────────────────────────────────────────────
function heartbeat() {
  const heartbeatFile = path.join(BRIDGE_QUEUE_DIR, 'heartbeat.json');
  try {
    ensureQueue();
    fs.writeFileSync(heartbeatFile, JSON.stringify({
      status: isReady ? 'online' : 'initializing',
      timestamp: Date.now(),
      pid: process.pid
    }));
  } catch(e) {}
}
setInterval(heartbeat, 10000);

client.on('disconnected', (reason) => { 
  isReady = false; 
  console.log(`❌ WhatsApp Disconnected! Reason: ${reason}. Reconnecting in 10s...`);
  setTimeout(() => {
    client.initialize().catch(e => console.error('[WhatsApp] Re-init error:', e.message));
  }, 10000); 
});

// ── PROCESS CRASH GUARDS ──────────────────────────────────────────────────
// Prevent the ENTIRE Node process from dying on unhandled errors.
// The Guardian can restart us if needed, but we should try to survive.
process.on('uncaughtException', (err) => {
  console.error('[WhatsApp] Uncaught Exception (surviving):', err.message);
  // If it's a Puppeteer crash, try to restart the client
  if (err.message && (err.message.includes('Target closed') || 
      err.message.includes('Session closed') ||
      err.message.includes('Protocol error') ||
      err.message.includes('Execution context'))) {
    console.log('[WhatsApp] Puppeteer crash detected. Reinitializing in 15s...');
    isReady = false;
    setTimeout(() => {
      client.initialize().catch(e => console.error('[WhatsApp] Emergency re-init error:', e.message));
    }, 15000);
  }
  // Do NOT call process.exit() — stay alive!
});

process.on('unhandledRejection', (reason) => {
  console.error('[WhatsApp] Unhandled Promise Rejection (surviving):', reason?.message || reason);
  // Do NOT call process.exit() — stay alive!
});

console.log('🚀 Launching WhatsApp Client...');
client.initialize();

