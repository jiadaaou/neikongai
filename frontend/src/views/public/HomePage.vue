<template>
  <div class="home-page">
    <!-- 导航栏 -->
    <header class="navbar">
      <div class="navbar-inner container">
        <div class="navbar-brand">
          <svg class="logo-icon" width="32" height="32" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="8" fill="#6c63ff"/>
            <circle cx="16" cy="16" r="6" stroke="#fff" stroke-width="2"/>
            <circle cx="16" cy="16" r="2" fill="#fff"/>
            <line x1="16" y1="4" x2="16" y2="10" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
            <line x1="16" y1="22" x2="16" y2="28" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
            <line x1="4" y1="16" x2="10" y2="16" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
            <line x1="22" y1="16" x2="28" y2="16" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span class="brand-text">内控AI</span>
        </div>
        <nav class="navbar-links">
          <a href="#features">功能特性</a>
          <a href="#solutions">解决方案</a>
          <a href="#pricing">价格方案</a>
          <a href="#contact">联系我们</a>
        </nav>
        <el-button type="primary" @click="$router.push('/login')">立即登录</el-button>
      </div>
    </header>

    <!-- Hero 区域 -->
    <section class="hero" id="hero">
      <div class="hero-deco hero-deco-tl"></div>
      <div class="hero-deco hero-deco-tr"></div>
      <div class="hero-deco hero-deco-bl"></div>
      
      <div class="hero-content container">
        <div class="badge">智能法律合规</div>
        <h1 class="hero-title">AI驱动的内部控制与合规管理</h1>
        <p class="hero-subtitle">基于人工智能的企业法律合规解决方案，让合规管理更简单高效</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/login')">
            立即开始
          </el-button>
          <el-button size="large" @click="$router.push('/register')">
            企业注册
          </el-button>
        </div>
      </div>

      <!-- Dashboard 预览 -->
      <div class="dashboard-preview container">
        <div class="dashboard-mockup">
          <div class="mockup-header">
            <div class="mockup-dots">
              <span class="dot dot-red"></span>
              <span class="dot dot-yellow"></span>
              <span class="dot dot-green"></span>
            </div>
            <span class="mockup-title">内控AI 管理后台</span>
          </div>
          <div class="mockup-content">
            <div class="mockup-sidebar">
              <div class="sidebar-item active">仪表盘</div>
              <div class="sidebar-item">法规管理</div>
              <div class="sidebar-item">风险监控</div>
              <div class="sidebar-item">审计日志</div>
            </div>
            <div class="mockup-main">
              <div class="mockup-cards">
                <div class="mockup-card">
                  <div class="card-label">合规评分</div>
                  <div class="card-value">96.8%</div>
                  <div class="card-trend">↑ +2.1%</div>
                </div>
                <div class="mockup-card">
                  <div class="card-label">待处理事项</div>
                  <div class="card-value">12</div>
                  <div class="card-trend">↓ -3</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 功能特性 -->
    <section class="features" id="features">
      <div class="container">
        <div class="section-header">
          <div class="badge badge-purple">核心功能</div>
          <h2 class="section-title">强大的功能体系</h2>
          <p class="section-subtitle">全方位的法律合规管理解决方案</p>
        </div>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon feature-icon-purple">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <h3>智能文档管理</h3>
            <p>自动化的法律文档管理系统，实时更新法规变化，确保企业合规</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon feature-icon-green">
              <el-icon :size="32"><ChatDotRound /></el-icon>
            </div>
            <h3>AI法律问答</h3>
            <p>基于人工智能的法律问答系统，快速准确地解答企业合规问题</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon feature-icon-blue">
              <el-icon :size="32"><DataAnalysis /></el-icon>
            </div>
            <h3>风险评估</h3>
            <p>智能风险评估引擎，提前识别合规风险，提供优先级排序和解决方案</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 解决方案 -->
    <section class="solutions" id="solutions">
      <div class="container">
        <div class="section-header">
          <div class="badge badge-light">解决方案</div>
          <h2 class="section-title section-title-light">全面的合规解决方案</h2>
          <p class="section-subtitle section-subtitle-light">满足不同场景的合规管理需求</p>
        </div>

        <div class="solution-row">
          <div class="solution-content">
            <span class="solution-tag">01</span>
            <h3>法规智能监控</h3>
            <p>实时监控全球法规变化，自动分析对企业的影响，及时提供合规建议</p>
            <ul class="solution-list">
              <li><el-icon color="#22c55e"><Check /></el-icon> 200+ 监管机构实时监控</li>
              <li><el-icon color="#22c55e"><Check /></el-icon> 自动化影响分析</li>
              <li><el-icon color="#22c55e"><Check /></el-icon> 主动预警提醒</li>
            </ul>
          </div>
          <div class="solution-visual">
            <div class="visual-card">
              <div class="visual-header">法规智能分析</div>
              <div class="visual-content">
                <div class="visual-score">
                  <span class="score-value">92%</span>
                  <span class="score-label">合规率</span>
                </div>
                <div class="visual-items">
                  <div class="visual-item">
                    <span class="item-dot item-dot-green"></span>
                    <span class="item-text">数据保护政策已更新</span>
                  </div>
                  <div class="visual-item">
                    <span class="item-dot item-dot-yellow"></span>
                    <span class="item-text">Cookie 合规需审查</span>
                  </div>
                  <div class="visual-item">
                    <span class="item-dot item-dot-green"></span>
                    <span class="item-text">加密标准：通过</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 价格方案 -->
    <section class="pricing" id="pricing">
      <div class="container">
        <div class="section-header">
          <div class="badge badge-purple">价格方案</div>
          <h2 class="section-title">简单透明的定价</h2>
          <p class="section-subtitle">选择适合您企业的方案</p>
        </div>

        <div class="pricing-grid">
          <div class="pricing-card">
            <h3 class="pricing-name">基础版</h3>
            <p class="pricing-desc">适合小型企业起步</p>
            <div class="pricing-price">
              <span class="price-currency">¥</span>
              <span class="price-amount">299</span>
              <span class="price-period">/月</span>
            </div>
            <ul class="pricing-features">
              <li><el-icon color="#22c55e"><Check /></el-icon> 最多 5 个用户</li>
              <li><el-icon color="#22c55e"><Check /></el-icon> 3 个合规框架</li>
              <li><el-icon color="#22c55e"><Check /></el-icon> 基础风险评估</li>
              <li><el-icon color="#909399"><Close /></el-icon> 自定义集成</li>
            </ul>
            <el-button class="pricing-button" size="large">开始使用</el-button>
          </div>

          <div class="pricing-card pricing-card-popular">
            <div class="popular-badge">最受欢迎</div>
            <h3 class="pricing-name">专业版</h3>
            <p class="pricing-desc">适合成长型企业</p>
            <div class="pricing-price">
              <span class="price-currency">¥</span>
              <span class="price-amount">799</span>
              <span class="price-period">/月</span>
            </div>
            <ul class="pricing-features">
              <li><el-icon color="#22c55e"><Check /></el-icon> 最多 25 个用户</li>
              <li><el-icon color="#22c55e"><Check /></el-icon> 无限合规框架</li>
              <li><el-icon color="#22c55e"><Check /></el-icon> AI 风险评分</li>
              <li><el-icon color="#22c55e"><Check /></el-icon> 20+ 预置集成</li>
            </ul>
            <el-button type="primary" class="pricing-button" size="large">开始试用</el-button>
          </div>

          <div class="pricing-card">
            <h3 class="pricing-name">企业版</h3>
            <p class="pricing-desc">大型企业定制方案</p>
            <div class="pricing-price">
              <span class="price-amount price-amount-custom">定制</span>
            </div>
            <ul class="pricing-features">
              <li><el-icon color="#22c55e"><Check /></el-icon> 无限用户</li>
              <li><el-icon color="#22c55e"><Check /></el-icon> 所有合规框架</li>
              <li><el-icon color="#22c55e"><Check /></el-icon> 企业级 AI 分析</li>
              <li><el-icon color="#22c55e"><Check /></el-icon> 专属客户经理</li>
            </ul>
            <el-button class="pricing-button" size="large">联系销售</el-button>
          </div>
        </div>
      </div>
    </section>

    <!-- 联系我们 -->
    <section class="contact" id="contact">
      <div class="container">
        <div class="section-header">
          <div class="badge badge-light">联系我们</div>
          <h2 class="section-title section-title-light">开始您的合规之旅</h2>
          <p class="section-subtitle section-subtitle-light">我们随时准备帮助您解决合规问题</p>
        </div>

        <div class="contact-content">
          <div class="contact-info">
            <div class="contact-item">
              <el-icon :size="24" color="#6c63ff"><Location /></el-icon>
              <div>
                <div class="contact-label">地址</div>
                <div class="contact-value">北京市朝阳区建国路 88 号<br>SOHO 现代城 A 座 2008</div>
              </div>
            </div>
            <div class="contact-item">
              <el-icon :size="24" color="#6c63ff"><Message /></el-icon>
              <div>
                <div class="contact-label">邮箱</div>
                <div class="contact-value">contact@neikongai.com</div>
              </div>
            </div>
            <div class="contact-item">
              <el-icon :size="24" color="#6c63ff"><Phone /></el-icon>
              <div>
                <div class="contact-label">电话</div>
                <div class="contact-value">400-888-8888</div>
              </div>
            </div>
          </div>

          <el-form class="contact-form" label-position="top">
            <el-form-item label="姓名">
              <el-input size="large" placeholder="请输入您的姓名" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input size="large" placeholder="请输入您的邮箱" />
            </el-form-item>
            <el-form-item label="留言">
              <el-input type="textarea" :rows="4" placeholder="请告诉我们您的需求" />
            </el-form-item>
            <el-button type="primary" size="large" style="width: 100%">发送消息</el-button>
          </el-form>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <div class="footer-main">
          <div class="footer-brand">
            <div class="navbar-brand">
              <svg class="logo-icon" width="28" height="28" viewBox="0 0 32 32" fill="none">
                <rect width="32" height="32" rx="8" fill="#6c63ff"/>
                <circle cx="16" cy="16" r="6" stroke="#fff" stroke-width="2"/>
                <circle cx="16" cy="16" r="2" fill="#fff"/>
              </svg>
              <span class="brand-text">内控AI</span>
            </div>
            <p class="footer-desc">智能法律合规管理平台，为500+企业提供专业的合规解决方案</p>
          </div>

          <div class="footer-links">
            <div class="footer-col">
              <h4>产品</h4>
              <a href="#features">功能特性</a>
              <a href="#solutions">解决方案</a>
              <a href="#pricing">价格方案</a>
            </div>
            <div class="footer-col">
              <h4>支持</h4>
              <a href="#">帮助文档</a>
              <a href="#">API 文档</a>
              <a href="#">常见问题</a>
            </div>
            <div class="footer-col">
              <h4>法律</h4>
              <a href="#">隐私政策</a>
              <a href="#">服务条款</a>
              <a href="#">Cookie 政策</a>
            </div>
          </div>
        </div>

        <div class="footer-bottom">
          <p>&copy; 2024 内控AI. All rights reserved.</p>
          <div class="footer-bottom-links">
            <a href="#">隐私</a>
            <a href="#">条款</a>
            <a href="#">Cookies</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { Document, ChatDotRound, DataAnalysis, Check, Close, Location, Message, Phone } from '@element-plus/icons-vue'
</script>

<style scoped>
/* 统一设计系统 */
.home-page {
  font-family: var(--font-primary);
}

/* 导航栏 */
.navbar {
  position: sticky;
  top: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  z-index: 100;
  padding: 1rem 0;
}

.navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a1a1a;
}

.logo-icon {
  flex-shrink: 0;
}

.navbar-links {
  display: flex;
  gap: 2rem;
}

.navbar-links a {
  color: #666;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.navbar-links a:hover {
  color: var(--primary-color);
}

/* Hero 区域 */
.hero {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 6rem 0 4rem;
  overflow: hidden;
  color: white;
}

.hero-deco {
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  z-index: 0;
}

.hero-deco-tl {
  top: -200px;
  left: -200px;
}

.hero-deco-tr {
  top: -150px;
  right: -150px;
  width: 300px;
  height: 300px;
}

.hero-deco-bl {
  bottom: -100px;
  left: 10%;
  width: 250px;
  height: 250px;
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  margin-bottom: 4rem;
}

.badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.badge-purple {
  background: rgba(108, 99, 255, 0.1);
  color: #6c63ff;
}

.badge-light {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.hero-title {
  font-family: var(--font-heading);
  font-size: 3.5rem;
  font-weight: 800;
  margin: 0 0 1.5rem;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.25rem;
  margin: 0 0 2.5rem;
  opacity: 0.95;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

/* Dashboard 预览 */
.dashboard-preview {
  position: relative;
  z-index: 1;
}

.dashboard-mockup {
  background: var(--dark-bg);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.mockup-header {
  background: var(--dark-bg-secondary);
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.mockup-dots {
  display: flex;
  gap: 0.5rem;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot-red { background: #ef4444; }
.dot-yellow { background: #f59e0b; }
.dot-green { background: #22c55e; }

.mockup-title {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
}

.mockup-content {
  display: flex;
  min-height: 300px;
}

.mockup-sidebar {
  width: 200px;
  background: var(--dark-bg-secondary);
  padding: 1.5rem 1rem;
}

.sidebar-item {
  padding: 0.75rem 1rem;
  color: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.sidebar-item.active {
  background: var(--primary-color);
  color: white;
}

.mockup-main {
  flex: 1;
  padding: 2rem;
}

.mockup-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.mockup-card {
  background: var(--dark-bg-secondary);
  padding: 1.5rem;
  border-radius: 12px;
}

.card-label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.card-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
}

.card-trend {
  color: var(--success);
  font-size: 0.875rem;
}

/* 通用容器 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* 通用 Section */
.features, .solutions, .pricing, .contact {
  padding: 6rem 0;
}

.solutions {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-title {
  font-family: var(--font-heading);
  font-size: 2.5rem;
  font-weight: 700;
  margin: 1rem 0;
  color: #1a1a1a;
}

.section-title-light {
  color: white;
}

.section-subtitle {
  font-size: 1.125rem;
  color: #666;
  max-width: 600px;
  margin: 0 auto;
}

.section-subtitle-light {
  color: rgba(255, 255, 255, 0.9);
}

/* 功能卡片 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
}

.feature-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.feature-icon-purple { background: rgba(108, 99, 255, 0.1); color: #6c63ff; }
.feature-icon-green { background: rgba(34, 197, 94, 0.1); color: #22c55e; }
.feature-icon-blue { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }

.feature-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: #1a1a1a;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* 解决方案 */
.solution-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 4rem;
  align-items: center;
}

.solution-tag {
  display: inline-block;
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
}

.solution-content h3 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 1rem;
}

.solution-content p {
  font-size: 1.125rem;
  line-height: 1.6;
  margin: 0 0 1.5rem;
  opacity: 0.9;
}

.solution-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.solution-list li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  font-size: 1rem;
}

.visual-card {
  background: var(--dark-bg);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.visual-header {
  background: var(--dark-bg-secondary);
  padding: 1.5rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
  font-weight: 600;
}

.visual-content {
  padding: 2rem;
}

.visual-score {
  text-align: center;
  margin-bottom: 2rem;
}

.score-value {
  display: block;
  font-size: 3rem;
  font-weight: 800;
  color: var(--success);
  margin-bottom: 0.5rem;
}

.score-label {
  color: rgba(255, 255, 255, 0.5);
}

.visual-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.visual-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.item-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.item-dot-green { background: var(--success); }
.item-dot-yellow { background: var(--warning); }

.item-text {
  color: rgba(255, 255, 255, 0.75);
  font-size: 0.875rem;
}

/* 价格卡片 */
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.pricing-card {
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  transition: transform 0.3s, box-shadow 0.3s;
}

.pricing-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
}

.pricing-card-popular {
  border: 2px solid var(--primary-color);
}

.popular-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--primary-color);
  color: white;
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
}

.pricing-name {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
  color: #1a1a1a;
}

.pricing-desc {
  color: #666;
  margin: 0 0 2rem;
}

.pricing-price {
  margin-bottom: 2rem;
}

.price-currency {
  font-size: 1.5rem;
  font-weight: 600;
  color: #666;
}

.price-amount {
  font-size: 3rem;
  font-weight: 800;
  color: #1a1a1a;
}

.price-amount-custom {
  font-size: 2rem;
}

.price-period {
  font-size: 1rem;
  color: #666;
}

.pricing-features {
  list-style: none;
  padding: 0;
  margin: 0 0 2rem;
}

.pricing-features li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0;
  color: #666;
}

.pricing-button {
  width: 100%;
}

/* 联系我们 */
.contact {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.contact-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 4rem;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.contact-item {
  display: flex;
  gap: 1.5rem;
}

.contact-label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  opacity: 0.7;
}

.contact-value {
  font-size: 1.125rem;
  line-height: 1.6;
}

.contact-form {
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
}

/* Footer */
.footer {
  background: #1a1a1a;
  color: white;
  padding: 4rem 0 2rem;
}

.footer-main {
  display: grid;
  grid-template-columns: 2fr 3fr;
  gap: 4rem;
  margin-bottom: 3rem;
}

.footer-desc {
  color: rgba(255, 255, 255, 0.6);
  margin: 1.5rem 0 0;
  line-height: 1.6;
}

.footer-links {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.footer-col h4 {
  font-weight: 600;
  margin: 0 0 1rem;
}

.footer-col a {
  display: block;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  padding: 0.5rem 0;
  transition: color 0.3s;
}

.footer-col a:hover {
  color: white;
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-bottom p {
  margin: 0;
  color: rgba(255, 255, 255, 0.5);
}

.footer-bottom-links {
  display: flex;
  gap: 2rem;
}

.footer-bottom-links a {
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  transition: color 0.3s;
}

.footer-bottom-links a:hover {
  color: white;
}

/* 响应式 */
@media (max-width: 768px) {
  .navbar-links {
    display: none;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .solution-row,
  .contact-content,
  .footer-main {
    grid-template-columns: 1fr;
  }
  
  .pricing-grid {
    grid-template-columns: 1fr;
  }
}
</style>
