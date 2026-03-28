/**
 * Environment variable validation and access
 * 
 * This module provides type-safe access to environment variables with
 * validation at build time. Required variables will throw clear errors
 * if not set, while optional variables have safe defaults.
 */

function getRequiredEnv(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(
      `Missing required environment variable: ${key}\n` +
      `Please set ${key} in your .env.local file or environment.\n` +
      `See .env.example for reference.`
    );
  }
  return value;
}

function getOptionalEnv(key: string, defaultValue: string): string {
  return process.env[key] || defaultValue;
}

/**
 * Centralized environment configuration
 * 
 * All environment variables are accessed through this object to ensure
 * consistency and validation across the application.
 */
export const env = {
  /** API URL - must be accessible from the browser (required) */
  API_URL: getRequiredEnv('NEXT_PUBLIC_API_URL'),
  
  /** Default email for development login (optional) */
  DEFAULT_EMAIL: getOptionalEnv('NEXT_PUBLIC_DEFAULT_EMAIL', 'admin@co-op.local'),
  
  /** Default password for development login (optional) */
  DEFAULT_PASSWORD: getOptionalEnv('NEXT_PUBLIC_DEFAULT_PASSWORD', 'testpass123'),
  
  /** Environment: development, staging, or production (optional) */
  ENVIRONMENT: getOptionalEnv('NEXT_PUBLIC_ENVIRONMENT', 'development'),
} as const;
