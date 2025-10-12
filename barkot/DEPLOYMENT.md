# GitHub Pages Deployment Instructions

## 🚀 How to Deploy to GitHub Pages

### Step 1: Initialize Git Repository
```bash
cd /home/dszczepek/slums
git init
git add .
git commit -m "Initial commit: Barkot Foundation analysis website"
```

### Step 2: Create GitHub Repository
1. Go to [GitHub.com](https://github.com)
2. Create a new repository named `slums`
3. **Important**: Make it public (required for free GitHub Pages)
4. Don't initialize with README (we already have one)

### Step 3: Connect Local to Remote
```bash
git remote add origin https://github.com/dszczepek/slums.git
git branch -M main
git push -u origin main
```

### Step 4: Enable GitHub Pages
1. Go to your repository on GitHub
2. Click on **Settings** tab
3. Scroll down to **Pages** section
4. Under **Source**, select "Deploy from a branch"
5. Choose **main** branch
6. Click **Save**

### Step 5: Wait for Deployment
- GitHub will automatically build and deploy your Jekyll site
- It may take 5-10 minutes for the first deployment
- Your site will be available at: `https://dszczepek.github.io/slums`

## 🔧 Local Development

### Prerequisites
```bash
# Install Ruby and Bundler (if not already installed)
sudo apt update
sudo apt install ruby-full build-essential zlib1g-dev

# Install Bundler
gem install bundler
```

### Run Locally
```bash
cd /home/dszczepek/slums
bundle install
bundle exec jekyll serve
```

Your local site will be available at: `http://localhost:4000`

## 📝 Making Updates

### To update content:
1. Edit the files (markdown, HTML, CSS, JS)
2. Commit and push changes:
```bash
git add .
git commit -m "Update: describe your changes"
git push
```

### GitHub Pages will automatically rebuild and deploy your changes!

## 🌟 Features Enabled

- ✅ **SEO Optimization**: Meta tags, structured data
- ✅ **Mobile Responsive**: Works on all devices
- ✅ **Fast Loading**: Optimized assets
- ✅ **Analytics Ready**: Easy to add Google Analytics
- ✅ **Professional URLs**: Clean, SEO-friendly URLs
- ✅ **Automatic HTTPS**: Secure by default

## 🔍 File Structure
```
/home/dszczepek/slums/
├── _config.yml          # Jekyll configuration
├── _layouts/            # Page templates
│   ├── default.html     # Main layout
│   └── document.html    # Document layout
├── _documents/          # Additional documents
├── assets/              # CSS, JS, images
│   ├── css/styles.css   # Stylesheets
│   └── js/main.js       # JavaScript
├── index.html           # Main page
├── Gemfile             # Ruby dependencies
└── README.md           # Project documentation
```

## 🎯 Next Steps After Deployment

1. **Share the URL**: `https://dszczepek.github.io/slums`
2. **Add Google Analytics** (optional): Add tracking ID to `_config.yml`
3. **Custom Domain** (optional): Add your own domain in repository settings
4. **Social Media**: Share on LinkedIn, Twitter, Facebook
5. **Email**: Send to Barkot Foundation and other stakeholders

## 🆘 Troubleshooting

### Build Errors
- Check the **Actions** tab in GitHub for build logs
- Ensure all files are properly formatted
- Verify Jekyll configuration in `_config.yml`

### Page Not Loading
- Wait 5-10 minutes after first deployment
- Check repository is public
- Verify GitHub Pages is enabled in settings

### Local Development Issues
```bash
# If bundle install fails
sudo apt install ruby-dev

# If Jekyll serve fails
bundle update
bundle exec jekyll serve --incremental
```

---

*🎉 Your website will be live at: `https://dszczepek.github.io/slums`*
