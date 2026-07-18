// models/Conversation.js

const mongoose = require('mongoose');

const MessageSchema = new mongoose.Schema({
  role: {
    type: String,
    enum: ['user', 'assistant', 'system'],
    required: true
  },
  content: {
    type: String,
    required: true
  },
  originalContent: String,
  translatedContent: String,
  languageType: {
    type: String,
    enum: ['TELUGU_SCRIPT', 'TENGLISH', 'ENGLISH', 'UNKNOWN']
  },
  intent: String,
  timestamp: {
    type: Date,
    default: Date.now
  }
});

const ConversationSchema = new mongoose.Schema({
  phoneNumber: {
    type: String,
    required: true,
    index: true
  },
  contactName: String,
  messages: [MessageSchema],
  context: {
    currentTopic: String,
    rentAmount: Number,
    flatDetails: String,
    lastIntent: String,
    preferredLanguage: {
      type: String,
      default: 'TENGLISH'
    }
  },
  metadata: {
    totalMessages: { type: Number, default: 0 },
    firstContact: { type: Date, default: Date.now },
    lastActive: { type: Date, default: Date.now },
    isBlocked: { type: Boolean, default: false },
    isVIP: { type: Boolean, default: false },
    tags: [String]
  }
}, { timestamps: true });

// Auto update lastActive
ConversationSchema.pre('save', function(next) {
  this.metadata.lastActive = new Date();
  this.metadata.totalMessages = this.messages.length;
  next();
});

module.exports = mongoose.model('Conversation', ConversationSchema);
