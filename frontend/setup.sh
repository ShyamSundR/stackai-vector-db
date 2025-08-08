#!/bin/bash

# StackAI Frontend Setup Script
echo "🚀 Setting up StackAI Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Install dependencies
echo "📦 Installing dependencies..."
if command -v yarn &> /dev/null; then
    yarn install
else
    npm install
fi

# Create environment file if it doesn't exist
if [ ! -f .env.local ]; then
    echo "🔧 Creating environment configuration..."
    cat > .env.local << EOF
# StackAI Frontend Environment Variables
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_DEV_MODE=true
EOF
    echo "✅ Created .env.local with default settings"
fi

echo ""
echo "🎉 Setup complete! "
echo ""
echo "📋 Next steps:"
echo "1. Make sure your StackAI backend is running on http://localhost:8000"
echo "2. Start the frontend development server:"
echo "   npm run dev"
echo "   # or"
echo "   yarn dev"
echo ""
echo "3. Open your browser to http://localhost:3000"
echo ""
echo "🔗 Useful commands:"
echo "   npm run dev      - Start development server"
echo "   npm run build    - Build for production"
echo "   npm run lint     - Run linting"
echo "   npm run test     - Run tests"
echo ""
echo "📖 For more information, see the README.md file" 