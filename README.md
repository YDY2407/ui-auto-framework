# Web UI 自动化测试框架实战（Playwright + POM）

## 快速运行

```bash
# 1. 无头模式极速跑全量（直接复用 Windows 自带 Edge，无需额外下载浏览器）
pytest --browser-channel msedge

# 2. 有头慢放模式（强烈推荐！亲眼看浏览器自动填表、点击、加购、结算！）
pytest --browser-channel msedge --headed --slowmo 600

# 3. 如果你执行过 playwright install chromium，也可以直接敲：
pytest
```

## 面试必讲 4 大工程亮点
1. **POM（Page Object Model）分层**：`pages/` 管理元素定位（统一 `data-testid`）与页面动作，`testcases/` 只写业务流程和断言。
2. **零 `time.sleep()`**：全面采用 Playwright 自动等待与 `expect()` 智能断言，彻底解决 Flaky 脆弱用例。
3. **UI + 接口/Cookie 混合提速**：`logged_in_page` Fixture 直接注入会话 Cookie 跳过登录页，直达商品结算页。
4. **网络拦截 Mock + 失败自动截图**：用 `page.route()` 模拟后端 500 宕机测前端容错；通过 `pytest_runtest_makereport` Hook 实现失败自动截全屏挂载报告。
