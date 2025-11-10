#!/bin/bash
# Install dependencies for the subdomain takeover scanner

echo "🚀 Installing Subdomain Scanner Dependencies..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install from https://brew.sh"
    exit 1
fi

# Install subfinder if not present
if ! command -v subfinder &> /dev/null; then
    echo "📦 Installing subfinder..."
    brew install subfinder
else
    echo "✅ subfinder already installed"
fi

# Check dig (comes with macOS)
if command -v dig &> /dev/null; then
    echo "✅ dig already installed"
else
    echo "⚠️  dig not found - installing bind tools..."
    brew install bind
fi

# Check if .NET SDK is installed
if ! command -v dotnet &> /dev/null; then
    echo "📦 Installing .NET SDK 9.0..."
    curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 9.0
    export PATH="$HOME/.dotnet:$PATH"
    echo 'export PATH="$HOME/.dotnet:$PATH"' >> ~/.zshrc
else
    echo "✅ .NET SDK already installed ($(dotnet --version))"
fi

# Build Subdominator
echo ""
echo "🔨 Building Subdominator from source..."

if [ -d ~/Subdominator ]; then
    cd ~/Subdominator/Subdominator
    echo "📂 Found Subdominator source code"

    # Try to build with published output
    echo "Building Subdominator (this may take a few minutes)..."
    ~/.dotnet/dotnet publish -c Release -r osx-arm64 --self-contained -o ~/subdominator-bin

    if [ $? -eq 0 ]; then
        echo "✅ Subdominator built successfully!"
        echo "📍 Binary location: ~/subdominator-bin/Subdominator"

        # Create symlink for easy access
        ln -sf ~/subdominator-bin/Subdominator ~/subdominator
        echo "🔗 Created symlink: ~/subdominator"
    else
        echo "❌ Build failed. You can try building manually later."
    fi
else
    echo "⚠️  Subdominator source not found at ~/Subdominator"
fi

echo ""
echo "✅ Dependency installation complete!"
