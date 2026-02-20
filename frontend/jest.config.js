const nextJest = require('next/jest');
const createJestConfig = nextJest({ dir: './' });
const customJestConfig = {
  setupFilesAfterFramework: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  testMatch: ['**/__tests__/**/*.test.{ts,tsx}'],
};
module.exports = createJestConfig(customJestConfig);
