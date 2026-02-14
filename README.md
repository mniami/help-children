# Help Children Project

This repository contains comprehensive documentation and analysis for projects supporting children in need, with a focus on street children in Ethiopia.

## 🌟 Barkot Foundation Website

The main application is a Jekyll-based website documenting strategies to support the Barkot Foundation's work.

### Prerequisites

- Ruby (version 3.0 or higher)
- Bundler gem manager

### Quick Start

1. **Install Bundler** (if not already installed):
   ```bash
   gem install bundler
   ```

2. **Navigate to the barkot directory**:
   ```bash
   cd barkot
   ```

3. **Install dependencies**:
   ```bash
   bundle config set --local path 'vendor/bundle'
   bundle install
   ```

4. **Start the development server**:
   ```bash
   bundle exec jekyll serve --host 0.0.0.0 --port 4000
   ```

5. **View the website**:
   Open your browser and navigate to: `http://localhost:4000`

### Project Structure

- **barkot/** - Jekyll website with Barkot Foundation analysis
- **ethiopia/** - Ethiopia-specific childcare documentation
- **idea/** - Project concept documentation
- Various analysis documents in the root directory

### Features

The Barkot Foundation website includes:
- 🏢 Foundation Overview
- 📚 Current Activities
- 📊 Revenue Strategy & Priority List
- 🆚 Current vs. Proposed Approach
- 💬 Discussion of Practical Concerns
- 🚀 Action Plan
- 📞 Contact Information

### Development

The site automatically rebuilds when you make changes to the source files. Simply refresh your browser to see updates.

To stop the server, press `Ctrl+C` in the terminal where it's running.

### Deployment

This site is designed to be deployed to GitHub Pages. See `barkot/DEPLOYMENT.md` for detailed deployment instructions.

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions, suggestions, and feedback are welcome. Please feel free to open issues or submit pull requests.
