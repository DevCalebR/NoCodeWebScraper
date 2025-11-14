# 🕷️ ScraperPro - Enterprise Web Scraping SaaS Platform

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

**Professional web scraping platform with tiered pricing, 7-day free trials, and no coding required.**

Perfect for e-commerce monitoring, market research, data collection, and competitive analysis.

---

## ✨ Features

### 🎯 For Everyone
- **No Coding Required** - Visual point-and-click interface
- **7-Day Free Trial** - Full access, no credit card needed
- **Multiple Export Formats** - CSV, Excel, JSON, SQL
- **Scheduled Scraping** - Set it and forget it
- **Anti-Detection** - Rotating user agents, delays, headers

### 💼 For Businesses
- **Multi-Client Support** - Manage multiple accounts
- **Tiered Pricing** - Pro ($49/mo) and Enterprise ($199/mo)
- **API Access** - REST API for developers
- **Rate Limiting** - Protect against abuse
- **Payment Processing** - Stripe integration

### 🚀 For Developers
- **Open Source** - Fork, customize, deploy
- **Docker Support** - One-command deployment
- **Extensible** - Add custom scrapers easily
- **Well Documented** - Step-by-step guides

---

## 🚀 Quick Start (5 Minutes)

### 1. Install

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/scraper-pro.git
cd scraper-pro

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch

```bash
# Start web interface
streamlit run app.py

# In another terminal, start API server
python api_server.py
```

### 3. Access

- **Web Interface**: http://localhost:8501
- **API Server**: http://localhost:5000
- **Admin Panel**: `streamlit run admin_panel.py`

### 4. Create Your First Scraper

1. Click **"Register"** and start your 7-day trial
2. Go to **"Configurations"** tab
3. Create a new scraper:
   - Name: "Test Scraper"
   - URL: `https://quotes.toscrape.com/`
   - Container: `.quote`
   - Add fields: `text` → `.text`, `author` → `.author`
4. Click **"Run Scraper"** and export your data!

---

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Launch and get your first customer in 7 days
- **[Setup Guide](SETUP_GUIDE.md)** - Detailed installation and configuration
- **[Trial Management](TRIAL_MANAGEMENT.md)** - Managing the 7-day free trial system
- **[GitHub Setup](GITHUB_SETUP.md)** - Deploy to GitHub and promote your project

---

## 💰 Pricing Tiers

| Feature | Pro | Enterprise |
|---------|-----|------------|
| **Price** | $49/month | $199/month |
| **Free Trial** | 7 days | 7 days |
| **Requests/Day** | 1,000 | Unlimited |
| **Configurations** | 10 | Unlimited |
| **Export Formats** | CSV, Excel, JSON | All + SQL |
| **API Access** | ✅ | ✅ |
| **Scheduled Scraping** | ✅ | ✅ |
| **Priority Support** | ❌ | ✅ |
| **Dedicated Proxies** | ❌ | ✅ |

---

## 🏗️ Architecture

```
scraper-pro/
├── scraper.py              # Core scraping engine
├── app.py                  # Streamlit web interface
├── api_server.py           # REST API
├── admin_panel.py          # Admin dashboard
├── stripe_payments.py      # Payment processing
├── email_templates.py      # Automated emails
├── data/
│   ├── clients/            # Client configurations
│   └── configs/            # Scraper configs
├── output/                 # Exported data
└── logs/                   # Application logs
```

---

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access services
# Web: http://localhost:8501
# API: http://localhost:5000
```

---

## 🔌 API Usage

### Authentication

All API requests require an API key in the header:

```bash
curl -X GET "http://localhost:5000/api/v1/account" \
  -H "X-API-Key: your_api_key_here"
```

### Execute Scrape

```bash
curl -X POST "http://localhost:5000/api/v1/scrape" \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"config_id": "your_config_id"}'
```

### List Results

```bash
curl -X GET "http://localhost:5000/api/v1/results" \
  -H "X-API-Key: your_api_key_here"
```

See [API Documentation](docs/API.md) for full reference.

---

## 🎓 Use Cases

### 🛒 E-commerce
- Monitor competitor prices
- Track inventory changes
- Analyze product reviews
- Price comparison tools

### 💼 Job Listings
- Aggregate job postings
- Salary research
- Skill trend analysis
- Automated job alerts

### 🏠 Real Estate
- Property price monitoring
- Market analysis
- Investment research
- Rental comparisons

### 📰 News & Media
- Content aggregation
- Sentiment analysis
- Trend monitoring
- Research automation

---

## 🛠️ Configuration Example

```python
from scraper import ScraperConfig

config = ScraperConfig(
    config_id="my_scraper_001",
    client_id="client_123",
    name="E-commerce Product Scraper",
    target_url="https://example.com/products",
    selectors={
        'container': '.product-card',
        'title': '.product-title',
        'price': '.price',
        'rating': '.rating'
    },
    pagination={
        'next_selector': '.next-page'
    },
    output_format='csv'
)
```

---

## 🔒 Security

- **API Key Authentication** - Secure client identification
- **Rate Limiting** - Prevent abuse per tier
- **Data Encryption** - Secure client data storage
- **Input Validation** - Prevent injection attacks
- **No Sensitive Logging** - Credentials never logged

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m "Add amazing feature"`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📊 Roadmap

- [x] Multi-tier pricing system
- [x] 7-day free trial
- [x] Stripe payment integration
- [x] Email automation
- [x] Admin dashboard
- [ ] JavaScript rendering (Selenium/Playwright)
- [ ] Browser extension for selector picking
- [ ] Zapier integration
- [ ] GraphQL API
- [ ] Real-time scraping notifications
- [ ] AI-powered selector detection

---

## 🐛 Known Issues

None at this time! Please report any bugs via [GitHub Issues](https://github.com/YOUR_USERNAME/scraper-pro/issues).

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 💬 Support

- **Documentation**: [Quick Start Guide](QUICK_START.md)
- **Email**: support@scraperpro.com
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/scraper-pro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/scraper-pro/discussions)

---

## 🌟 Show Your Support

If this project helped you, give it a ⭐️!

---

## 📸 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Configuration
![Configuration](screenshots/config.png)

### Results
![Results](screenshots/results.png)

---

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web interface
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Flask](https://flask.palletsprojects.com/) - REST API
- [Stripe](https://stripe.com/) - Payment processing
- [Pandas](https://pandas.pydata.org/) - Data handling

---

**Made with ❤️ by [Your Name]**

**Star this repo if you find it useful!** ⭐
