export default {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  extensionsToTreatAsEsm: ['.jsx', '.js'],
  globals: {
    'ts-jest': {
      useESM: true
    }
  },
  preset: 'jest-esm'
};
