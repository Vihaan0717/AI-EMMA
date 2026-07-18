// models/Contact.js

const mongoose = require('mongoose');

const ContactSchema = new mongoose.Schema({
  phoneNumber: {
    type: String,
    required: true,
    unique: true
  },
  name: String,
  preferredLanguage: {
    type: String,
    enum: ['TELUGU_SCRIPT', 'TENGLISH', 'ENGLISH'],
    default: 'TENGLISH'
  },
  flatNumber: String,
  rentAmount: Number,
  joinDate: Date,
  notes: String,
  isActive: {
    type: Boolean,
    default: true
  },
  tags: [String]
}, { timestamps: true });

module.exports = mongoose.model('Contact', ContactSchema);
