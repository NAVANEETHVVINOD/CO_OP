/**
 * Property-based tests for frontend configuration validation.
 * 
 * Feature: seo-documentation-test-coverage
 * These tests use fast-check to validate configuration properties across the frontend codebase.
 */
import fc from 'fast-check';
import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// Feature: seo-documentation-test-coverage, Property 3: Frontend Code Has No Hardcoded URLs
// This property validates that TypeScript files do not contain hardcoded localhost URLs

function findTypeScriptFiles(dir: string, files: string[] = []): string[] {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    
    if (entry.isDirectory()) {
      // Skip node_modules, .next, and test directories
      if (!['node_modules', '.next', '__tests__', 'tests'].includes(entry.name)) {
        findTypeScriptFiles(fullPath, files);
      }
    } else if (entry.isFile() && (entry.name.endsWith('.ts') || entry.name.endsWith('.tsx'))) {
      // Skip test files
      if (!entry.name.includes('.test.') && !entry.name.includes('.spec.')) {
        files.push(fullPath);
      }
    }
  }
  
  return files;
}

function containsHardcodedUrl(content: string, filePath: string): boolean {
  // Skip env.ts and config files as they are allowed to reference env vars
  if (filePath.includes('env.ts') || filePath.includes('config.ts')) {
    return false;
  }
  
  // Patterns to detect hardcoded URLs
  const patterns = [
    /['"]https?:\/\/localhost:\d+['"]/g,
    /['"]https?:\/\/127\.0\.0\.1:\d+['"]/g,
    /['"]http:\/\/localhost['"]/g,
  ];
  
  for (const pattern of patterns) {
    const matches = content.match(pattern);
    if (matches) {
      // Check if it's in a comment
      for (const match of matches) {
        const index = content.indexOf(match);
        const lineStart = content.lastIndexOf('\n', index);
        const line = content.substring(lineStart, content.indexOf('\n', index));
        
        // Allow if it's in a comment
        if (!line.trim().startsWith('//') && !line.trim().startsWith('*')) {
          return true;
        }
      }
    }
  }
  
  return false;
}

describe('Property Tests', () => {
  it('should not contain hardcoded URLs in TypeScript files', () => {
    fc.assert(
      fc.property(fc.constant('check_hardcoded_urls'), () => {
        const srcDir = path.join(__dirname, '..');
        const tsFiles = findTypeScriptFiles(srcDir);
        
        const violations: string[] = [];
        for (const file of tsFiles) {
          const content = fs.readFileSync(file, 'utf-8');
          if (containsHardcodedUrl(content, file)) {
            violations.push(path.relative(srcDir, file));
          }
        }
        
        return violations.length === 0;
      }),
      { numRuns: 100 }
    );
  });

  it('should use environment variables for API configuration', () => {
    fc.assert(
      fc.property(fc.constant('check_env_usage'), () => {
        // Check that env.ts or similar config file exists and uses process.env
        const envFile = path.join(__dirname, '..', 'lib', 'env.ts');
        
        if (!fs.existsSync(envFile)) {
          // If env.ts doesn't exist, check api.ts
          const apiFile = path.join(__dirname, '..', 'lib', 'api.ts');
          if (!fs.existsSync(apiFile)) {
            return false;
          }
          
          const content = fs.readFileSync(apiFile, 'utf-8');
          // Should use process.env or import from env module
          return content.includes('process.env') || content.includes('from') && content.includes('env');
        }
        
        const content = fs.readFileSync(envFile, 'utf-8');
        // Should use process.env.NEXT_PUBLIC_API_URL
        return content.includes('process.env.NEXT_PUBLIC');
      }),
      { numRuns: 100 }
    );
  });

  it('should have all required environment variables documented', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('NEXT_PUBLIC_API_URL', 'NEXT_PUBLIC_ENVIRONMENT'),
        (envVar) => {
          // Check .env.example exists and contains the variable
          const envExamplePath = path.join(__dirname, '..', '..', '.env.example');
          
          if (!fs.existsSync(envExamplePath)) {
            return false;
          }
          
          const content = fs.readFileSync(envExamplePath, 'utf-8');
          return content.includes(envVar);
        }
      ),
      { numRuns: 100 }
    );
  });
});
