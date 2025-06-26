# System Requirements Installation Script
# Run this script to install system dependencies

echo "🔧 Installing system dependencies for CPU Data Processor..."

# Update package list
sudo apt-get update

# Install wkhtmltopdf
echo "📄 Installing wkhtmltopdf..."
sudo apt-get install -y wkhtmltopdf

# Install poppler-utils for PDF to image conversion
echo "🖼️  Installing poppler-utils for PDF processing..."
sudo apt-get install -y poppler-utils

# Install Google Chrome for Selenium
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Install curl for testing
echo "🔗 Installing curl..."
sudo apt-get install -y curl

echo "✅ System dependencies installed successfully!"
echo "Now run: pip install -r requirements.txt"
