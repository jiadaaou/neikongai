<template> <div class="page"> <header class="hero"> <div class="container"> <div class="nav"> <div class="logo">NeikongAI</div> <div 
          class="nav-links">
            <a href="#features">核心能力</a> <a href="#scenes">应用场景</a> <a href="#value">客户价值</a> <a 
            href="#contact">联系我们</a>
          </div> </div> <div class="hero-content"> <p class="badge">企业依法合规 AI 助手</p> <h1>让法律要求、制度建设与 AI 
          分析真正连接起来</h1> <p class="desc">
            NeikongAI 面向企业内控、合规、审计与法务场景， 基于法律知识库、制度库、风险识别与证据链能力， 
            帮助企业构建可追溯、可分析、可整改的智能合规体系。
          </p> <div class="actions"> <a class="btn primary" href="https://admin.neikongai.com">进入后台</a> <a class="btn" 
            href="#features">查看功能</a>
          </div> </div> </div> </header> <section id="features" class="section"> <div class="container"> <div class="section-head"> <p 
          class="eyebrow">核心能力</p> <h2>从法律条文到企业执行闭环</h2>
        </div> <div class="grid grid-4"> <div class="card"> <h3>法律知识库</h3> 
            <p>沉淀法规、条文、结构化规则与权威来源，形成合规底座。</p>
          </div> <div class="card"> <h3>AI 合规分析</h3> <p>自动提取义务要求、适用主体、风险等级、控制动作与整改建议。</p> </div> <div 
          class="card">
            <h3>制度缺口识别</h3> <p>对照企业制度与法律要求，发现缺失、冲突、滞后与执行断点。</p> </div> <div class="card"> 
            <h3>证据链支持</h3> <p>支持审计留痕、责任追踪、整改闭环与复核说明。</p>
          </div> </div> </div> </section> <section id="scenes" class="section dark"> <div class="container"> <div 
        class="section-head">
          <p class="eyebrow">应用场景</p> <h2>适用于多种企业治理场景</h2> </div> <div class="grid grid-3"> <div class="card"> 
            <h3>集团内控管理</h3> <p>统一制度口径，识别子公司合规执行差异，提升集团治理一致性。</p>
          </div> <div class="card"> <h3>法务与合规部门</h3> <p>快速定位法律依据，生成结构化分析结果，减少纯人工整理成本。</p> </div> 
          <div class="card">
            <h3>内部审计与整改</h3> <p>围绕问题、规则、制度与证据形成完整链条，支撑整改追踪。</p> </div> </div> </div> </section> 
    <section id="value" class="section">
      <div class="container"> <div class="section-head"> <p class="eyebrow">客户价值</p> 
          <h2>不只是“查法律”，而是帮助企业真正落地执行</h2>
        </div> <div class="value-box"> <div class="value-item"> <span>01</span> <div> <h3>降低制度建设成本</h3> 
              <p>让法律要求与企业制度内容建立清晰映射，减少重复梳理与遗漏。</p>
            </div> </div> <div class="value-item"> <span>02</span> <div> <h3>提升合规识别效率</h3> <p>通过 AI 
              自动分析条文义务、适用范围与业务触发点，提高识别速度。</p>
            </div> </div> <div class="value-item"> <span>03</span> <div> <h3>强化审计与整改闭环</h3> 
              <p>围绕问题发现、依据定位、责任分析、整改措施形成完整闭环链路。</p>
            </div> </div> </div> </div> </section> <footer id="contact" class="footer"> <div class="container footer-wrap"> <div> 
          <h3>NeikongAI</h3> <p>企业依法合规 AI 助手</p>
        </div> <div class="footer-links"> <a href="https://admin.neikongai.com">后台入口</a> <a href="#features">核心能力</a> <a 
          href="#scenes">应用场景</a>
        </div> </div> </footer> </div> </template> <style scoped> * { box-sizing: border-box;
}
:global(body) {
  margin: 0; font-family: Arial, Helvetica, sans-serif; background: #0b1220; color: #fff;
}
:global(a) {
  text-decoration: none;
}
.page { min-height: 100vh;
}
.container { width: min(1160px, 92%); margin: 0 auto;
}
.hero { background: radial-gradient(circle at top left, rgba(37, 99, 235, 0.35), transparent 35%), linear-gradient(135deg, #081120 0%, 
    #0f1b35 55%, #132445 100%);
  padding-bottom: 72px;
}
.nav { display: flex; justify-content: space-between; align-items: center; padding: 22px 0;
}
.logo { font-size: 22px; font-weight: 700; letter-spacing: 0.5px;
}
.nav-links { display: flex; gap: 24px;
}
.nav-links a { color: rgba(255,255,255,0.86); font-size: 14px;
}
.hero-content { padding: 72px 0 36px; max-width: 860px;
}
.badge, .eyebrow { display: inline-block; padding: 8px 14px; border-radius: 999px; background: rgba(255,255,255,0.1); color: #cfe0ff; 
  font-size: 13px; letter-spacing: 0.4px;
}
.hero h1 { font-size: 54px; line-height: 1.12; margin: 22px 0 18px;
}
.desc { font-size: 18px; line-height: 1.9; color: #d5dced; max-width: 780px;
}
.actions { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 30px;
}
.btn { display: inline-block; padding: 14px 22px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.18); color: #fff;
}
.btn.primary { background: #2563eb; border-color: #2563eb;
}
.section { padding: 80px 0; background: #0b1220;
}
.section.dark { background: #0f172a;
}
.section-head { margin-bottom: 28px;
}
.section-head h2 { margin: 14px 0 0; font-size: 34px; line-height: 1.3;
}
.grid { display: grid; gap: 20px;
}
.grid-4 { grid-template-columns: repeat(4, minmax(0, 1fr));
}
.grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr));
}
.card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 24px;
}
.card h3 { margin: 0 0 12px; font-size: 20px;
}
.card p { margin: 0; color: #cfd8e8; line-height: 1.8;
}
.value-box { display: grid; gap: 18px;
}
.value-item { display: flex; gap: 18px; align-items: flex-start; background: rgba(255,255,255,0.04); border: 1px solid 
  rgba(255,255,255,0.08); border-radius: 18px; padding: 24px;
}
.value-item span { width: 52px; height: 52px; flex: 0 0 52px; display: grid; place-items: center; border-radius: 14px; background: 
  #2563eb;
  font-weight: 700;
}
.value-item h3 { margin: 0 0 8px;
}
.value-item p { margin: 0; color: #cfd8e8; line-height: 1.8;
}
.footer { border-top: 1px solid rgba(255,255,255,0.08); padding: 28px 0 36px; background: #081120;
}
.footer-wrap { display: flex; justify-content: space-between; gap: 20px; align-items: center;
}
.footer h3 { margin: 0 0 8px;
}
.footer p { margin: 0; color: #aebcd3;
}
.footer-links { display: flex; gap: 18px; flex-wrap: wrap;
}
.footer-links a { color: #d5dced;
}
@media (max-width: 960px) { .grid-4 { grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .grid-3 { grid-template-columns: 1fr;
  }
  .hero h1 { font-size: 40px;
  }
  .footer-wrap { flex-direction: column; align-items: flex-start;
  }
}
@media (max-width: 640px) { .nav { flex-direction: column; align-items: flex-start; gap: 16px;
  }
  .nav-links { flex-wrap: wrap; gap: 14px;
  }
  .grid-4 { grid-template-columns: 1fr;
  }
  .hero-content { padding-top: 40px;
  }
  .hero h1 { font-size: 32px;
  }
  .desc { font-size: 16px;
  }
}
</style>
