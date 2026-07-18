// config/database.js
const mongoose = require('mongoose');

// In-memory store for resilience mode
const memoryStore = {
  conversations: new Map(),
  isMemoryMode: false
};

const connectDB = async () => {
  const mongoUri = process.env.MONGODB_URI || 
                   'mongodb://127.0.0.1:27017/arion_db';
  
  try {
    await mongoose.connect(mongoUri, {
      serverSelectionTimeoutMS: 5000,
      family: 4  // ✅ Force IPv4 (fixes ::1 vs 127.0.0.1 issue)
    });
    console.log('✅ [Database] MongoDB Connected!');
    memoryStore.isMemoryMode = false;
    
  } catch (error) {
    console.log(`⚠️ [Database] MongoDB unavailable: ${error.message}`);
    console.log('🚀 [Database] Entering Resilience Mode (Memory-Only)');
    memoryStore.isMemoryMode = true;
  }
};

// ✅ Memory-based conversation store
const memoryDB = {
  
  getConversation(phoneNumber) {
    return memoryStore.conversations.get(phoneNumber) || {
      phoneNumber,
      messages: [],
      context: { preferredLanguage: 'TENGLISH' },
      metadata: { totalMessages: 0 }
    };
  },
  
  saveConversation(phoneNumber, data) {
    memoryStore.conversations.set(phoneNumber, data);
  },
  
  isMemoryMode() {
    return memoryStore.isMemoryMode;
  }
};

module.exports = { connectDB, memoryDB };
