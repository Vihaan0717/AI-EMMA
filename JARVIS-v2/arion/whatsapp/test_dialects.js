// test_dialects.js

const { detectDialect, detectIntent } = require('./handlers/languageHandler');

const testCases = [
  { text: "kya scene hai yaar, rent kitna hai?", expected: "HYDERABAD" },
  { text: "em ra babu, rent entha avutundi?", expected: "RAJAHMUNDRY" },
  { text: "namaste, what is the rent?", expected: "GENERAL" },
  { text: "jaldi pampinchu ra dei", expected: "RAJAHMUNDRY" },
  { text: "kya yaar, payment kar do na", expected: "HYDERABAD" }
];

console.log("=== ARION DIALECT TEST SUITE ===\n");

testCases.forEach(test => {
    const dialect = detectDialect(test.text);
    const intent = detectIntent(test.text);
    const status = dialect === test.expected ? "✅" : "❌";
    console.log(`[${status}] Input: "${test.text}"`);
    console.log(`     Detected: ${dialect} (Expected: ${test.expected}) | Intent: ${intent}\n`);
});
