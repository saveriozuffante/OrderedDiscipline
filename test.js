const assert = require('assert');
const { orderedDiscipline } = require('./index');

assert.deepStrictEqual(orderedDiscipline([3,1,2]), [1,2,3]);

console.log('All tests passed');
