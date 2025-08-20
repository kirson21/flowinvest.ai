// Debug bot type classification logic
const userBots = [
  { id: 1, type: 'ai_generated', name: 'BTC Smart Trader Pro' },
  { id: 2, type: 'ai_generated', name: 'BTC Steady Growth Bot' },
  { id: 3, type: 'advanced', name: 'ETH Lightning Scalper' },
  { id: 4, type: 'advanced', name: 'Manual Strategy Bot' }
];

console.log('=== Bot Type Classification Test ===');

// Test AI bots counting
const aiBots = userBots.filter(bot => bot.type === 'ai_generated');
console.log('AI Bots:', aiBots.length, aiBots.map(b => b.name));

// Test manual bots counting (should exclude AI bots)
const manualBots = userBots.filter(bot => 
  bot.type === 'advanced' || (bot.type && bot.type !== 'ai_generated')
);
console.log('Manual Bots:', manualBots.length, manualBots.map(b => b.name));

// Expected results:
// AI Bots: 2 ['BTC Smart Trader Pro', 'BTC Steady Growth Bot']
// Manual Bots: 2 ['ETH Lightning Scalper', 'Manual Strategy Bot']

console.log('=== Limits Check ===');
console.log('Free plan limits:');
console.log('- AI Bots: 1 (current: ' + aiBots.length + ') - ' + (aiBots.length >= 1 ? 'LIMIT REACHED' : 'CAN CREATE'));
console.log('- Manual Bots: 2 (current: ' + manualBots.length + ') - ' + (manualBots.length >= 2 ? 'LIMIT REACHED' : 'CAN CREATE'));