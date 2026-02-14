export default function HomePage() {
  return (
    <main className="container">
      <div className="hero-section">
        <h1 className="hero-title">Welcome to Your App</h1>
        <p className="hero-subtitle">
          A beautiful, modern interface with seamless light/dark mode support
        </p>
        <div className="hero-buttons">
          <button className="button-primary">Get Started</button>
          <button className="button-secondary">Learn More</button>
        </div>
      </div>

      <section className="features-section">
        <h2 className="section-title">Features</h2>
        <div className="features-grid">
          <div className="card feature-card">
            <div className="feature-icon">⚡</div>
            <h3 className="feature-title">Lightning Fast</h3>
            <p className="feature-description">
              Optimized for performance with minimal overhead and smooth transitions.
            </p>
          </div>

          <div className="card feature-card">
            <div className="feature-icon">🎨</div>
            <h3 className="feature-title">Beautiful Design</h3>
            <p className="feature-description">
              Modern UI with carefully crafted colors and smooth animations.
            </p>
          </div>

          <div className="card feature-card">
            <div className="feature-icon">🔒</div>
            <h3 className="feature-title">Secure & Private</h3>
            <p className="feature-description">
              Your preferences are stored locally with no external tracking.
            </p>
          </div>

          <div className="card feature-card">
            <div className="feature-icon">📱</div>
            <h3 className="feature-title">Responsive</h3>
            <p className="feature-description">
              Works perfectly on all devices from mobile to desktop.
            </p>
          </div>
        </div>
      </section>

      <section className="form-section">
        <h2 className="section-title">Contact Us</h2>
        <div className="card form-card">
          <form className="contact-form">
            <div className="form-group">
              <label htmlFor="name" className="form-label">Name</label>
              <input
                type="text"
                id="name"
                className="form-input"
                placeholder="John Doe"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email" className="form-label">Email</label>
              <input
                type="email"
                id="email"
                className="form-input"
                placeholder="john@example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="message" className="form-label">Message</label>
              <textarea
                id="message"
                className="form-textarea"
                rows={5}
                placeholder="Your message here..."
              />
            </div>

            <button type="submit" className="button-primary button-full">
              Send Message
            </button>
          </form>
        </div>
      </section>

      <section className="stats-section">
        <h2 className="section-title">By The Numbers</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">100K+</div>
            <div className="stat-label">Active Users</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">99.9%</div>
            <div className="stat-label">Uptime</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">50ms</div>
            <div className="stat-label">Response Time</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">24/7</div>
            <div className="stat-label">Support</div>
          </div>
        </div>
      </section>

      <section className="pricing-section">
        <h2 className="section-title">Simple Pricing</h2>
        <div className="pricing-grid">
          <div className="card pricing-card">
            <div className="pricing-header">
              <h3 className="pricing-title">Starter</h3>
              <div className="pricing-price">
                <span className="price-currency">$</span>
                <span className="price-amount">9</span>
                <span className="price-period">/month</span>
              </div>
            </div>
            <ul className="pricing-features">
              <li className="pricing-feature">✓ 10 Projects</li>
              <li className="pricing-feature">✓ Basic Support</li>
              <li className="pricing-feature">✓ 5GB Storage</li>
              <li className="pricing-feature">✓ Community Access</li>
            </ul>
            <button className="button-secondary button-full">Choose Plan</button>
          </div>

          <div className="card pricing-card pricing-card-featured">
            <div className="featured-badge">Most Popular</div>
            <div className="pricing-header">
              <h3 className="pricing-title">Professional</h3>
              <div className="pricing-price">
                <span className="price-currency">$</span>
                <span className="price-amount">29</span>
                <span className="price-period">/month</span>
              </div>
            </div>
            <ul className="pricing-features">
              <li className="pricing-feature">✓ Unlimited Projects</li>
              <li className="pricing-feature">✓ Priority Support</li>
              <li className="pricing-feature">✓ 100GB Storage</li>
              <li className="pricing-feature">✓ Advanced Analytics</li>
            </ul>
            <button className="button-primary button-full">Choose Plan</button>
          </div>

          <div className="card pricing-card">
            <div className="pricing-header">
              <h3 className="pricing-title">Enterprise</h3>
              <div className="pricing-price">
                <span className="price-currency">$</span>
                <span className="price-amount">99</span>
                <span className="price-period">/month</span>
              </div>
            </div>
            <ul className="pricing-features">
              <li className="pricing-feature">✓ Unlimited Everything</li>
              <li className="pricing-feature">✓ 24/7 Dedicated Support</li>
              <li className="pricing-feature">✓ 1TB Storage</li>
              <li className="pricing-feature">✓ Custom Integrations</li>
            </ul>
            <button className="button-secondary button-full">Choose Plan</button>
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="card cta-card">
          <h2 className="cta-title">Ready to Get Started?</h2>
          <p className="cta-description">
            Join thousands of satisfied customers and experience the difference today.
          </p>
          <button className="button-primary button-large">
            Start Your Free Trial
          </button>
        </div>
      </section>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4 className="footer-title">Product</h4>
            <ul className="footer-links">
              <li><a href="#" className="footer-link">Features</a></li>
              <li><a href="#" className="footer-link">Pricing</a></li>
              <li><a href="#" className="footer-link">Security</a></li>
              <li><a href="#" className="footer-link">Roadmap</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4 className="footer-title">Company</h4>
            <ul className="footer-links">
              <li><a href="#" className="footer-link">About</a></li>
              <li><a href="#" className="footer-link">Blog</a></li>
              <li><a href="#" className="footer-link">Careers</a></li>
              <li><a href="#" className="footer-link">Contact</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4 className="footer-title">Resources</h4>
            <ul className="footer-links">
              <li><a href="#" className="footer-link">Documentation</a></li>
              <li><a href="#" className="footer-link">Help Center</a></li>
              <li><a href="#" className="footer-link">API Reference</a></li>
              <li><a href="#" className="footer-link">Community</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4 className="footer-title">Legal</h4>
            <ul className="footer-links">
              <li><a href="#" className="footer-link">Privacy</a></li>
              <li><a href="#" className="footer-link">Terms</a></li>
              <li><a href="#" className="footer-link">License</a></li>
              <li><a href="#" className="footer-link">Cookies</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p className="footer-copyright">
            © 2026 Your Company. All rights reserved.
          </p>
        </div>
      </footer>
    </main>
  );
}
