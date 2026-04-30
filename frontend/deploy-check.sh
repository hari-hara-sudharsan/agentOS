#!/bin/bash
# Force clean deployment script

echo "🧹 Cleaning up local cache..."
rm -rf .next
rm -rf node_modules/.cache

echo "📦 Installing dependencies..."
npm ci

echo "🏗️  Building for production..."
npm run build

echo "✅ Local build complete! Ready to deploy."
echo ""
echo "Next steps:"
echo "1. Commit changes: git add . && git commit -m 'fix: Update frontend deployment config'"
echo "2. Push to deploy: git push origin main"
echo "3. Check Vercel dashboard for deployment status"
