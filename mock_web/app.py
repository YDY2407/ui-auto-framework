"""
本地迷你电商 Web 前端靶场（零外部依赖，仅用 Python 标准库）
页面路由：
  - GET  /login     登录页（用户名/密码校验、错误 Toast 提示）
  - GET  /shop      商品列表与购物车结算页（加购、移除、提交订单、退出登录）
  - POST /api/login 登录接口（校验通过后种下 session Cookie）
  - POST /api/checkout 下单结算接口（可被 Playwright page.route 拦截 Mock！）

单独启动查看页面：python mock_web/app.py  -> 浏览器访问 http://127.0.0.1:8900/login
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

LOGIN_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>极速商城 - 登录</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f4f6f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .card { background: #fff; padding: 32px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); width: 340px; }
    h2 { margin-top: 0; text-align: center; color: #1f2937; }
    input { width: 100%; padding: 10px 12px; margin: 8px 0 14px; border: 1px solid #d1d5db; border-radius: 6px; box-sizing: border-box; }
    button { width: 100%; padding: 10px; background: #2563eb; color: #fff; border: none; border-radius: 6px; font-size: 15px; cursor: pointer; }
    button:hover { background: #1d4ed8; }
    .error { color: #dc2626; font-size: 13px; margin-bottom: 10px; min-height: 18px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>极速商城登录</h2>
    <div id="error-msg" data-testid="error-msg" class="error"></div>
    <input id="username" data-testid="username-input" placeholder="请输入用户名" />
    <input id="password" data-testid="password-input" type="password" placeholder="请输入密码" />
    <button id="login-btn" data-testid="login-btn">登录</button>
  </div>
  <script>
    document.getElementById("login-btn").addEventListener("click", async () => {
      const username = document.getElementById("username").value.trim();
      const password = document.getElementById("password").value;
      const errEl = document.getElementById("error-msg");
      errEl.textContent = "";

      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (res.ok && data.code === 0) {
        window.location.href = "/shop";
      } else {
        errEl.textContent = data.message || "登录失败";
      }
    });
  </script>
</body>
</html>
"""

SHOP_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>极速商城 - 商品大厅</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f4f6f9; margin: 0; padding: 24px; }
    .header { display: flex; justify-content: space-between; align-items: center; background: #fff; padding: 16px 24px; border-radius: 10px; margin-bottom: 20px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
    .product { background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .price { color: #e11d48; font-weight: bold; font-size: 18px; margin: 8px 0; }
    button { padding: 8px 14px; background: #2563eb; color: #fff; border: none; border-radius: 6px; cursor: pointer; }
    .cart-bar { margin-top: 24px; background: #fff; padding: 20px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; }
    .result { margin-top: 16px; padding: 14px; border-radius: 8px; display: none; }
    .result.ok { background: #dcfce7; color: #166534; display: block; }
    .result.fail { background: #fee2e2; color: #991b1b; display: block; }
  </style>
</head>
<body>
  <div class="header">
    <div><strong>极速商城</strong> | 欢迎你，<span data-testid="current-user">tester</span></div>
    <div>购物车：<span data-testid="cart-count">0</span> 件</div>
  </div>

  <div class="grid">
    <div class="product" data-testid="product-keyboard">
      <h3>机械键盘 Pro</h3>
      <div class="price">¥399</div>
      <button data-testid="add-keyboard" onclick="addToCart('机械键盘 Pro', 399)">加入购物车</button>
    </div>
    <div class="product" data-testid="product-mouse">
      <h3>人体工学鼠标</h3>
      <div class="price">¥199</div>
      <button data-testid="add-mouse" onclick="addToCart('人体工学鼠标', 199)">加入购物车</button>
    </div>
    <div class="product" data-testid="product-monitor">
      <h3>4K 护眼显示器</h3>
      <div class="price">¥2499</div>
      <button data-testid="add-monitor" onclick="addToCart('4K 护眼显示器', 2499)">加入购物车</button>
    </div>
  </div>

  <div class="cart-bar">
    <div>总计金额：<strong>¥<span data-testid="cart-total">0</span></strong></div>
    <button data-testid="checkout-btn" onclick="checkout()">立即结算</button>
  </div>

  <div id="checkout-result" data-testid="checkout-result" class="result"></div>

  <script>
    const cart = [];
    function addToCart(name, price) {
      cart.push({ name, price });
      document.querySelector('[data-testid="cart-count"]').textContent = cart.length;
      const total = cart.reduce((sum, item) => sum + item.price, 0);
      document.querySelector('[data-testid="cart-total"]').textContent = total;
    }

    async function checkout() {
      const resultEl = document.getElementById("checkout-result");
      if (cart.length === 0) {
        resultEl.className = "result fail";
        resultEl.textContent = "购物车为空，请先选择商品";
        return;
      }
      const res = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: cart })
      });
      const data = await res.json();
      if (res.ok && data.code === 0) {
        resultEl.className = "result ok";
        resultEl.textContent = `下单成功！订单号：${data.data.order_no}`;
      } else {
        resultEl.className = "result fail";
        resultEl.textContent = `下单失败：${data.message || "服务异常"}`;
      }
    }
  </script>
</body>
</html>
"""


class WebShopHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send_html(self, html: str, status: int = 200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, payload: dict, cookie: str | None = None):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def _is_logged_in(self) -> bool:
        cookie = self.headers.get("Cookie", "")
        return "session_user=tester" in cookie

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/login"):
            return self._send_html(LOGIN_HTML)
        if path == "/shop":
            if not self._is_logged_in():
                self.send_response(302)
                self.send_header("Location", "/login")
                self.end_headers()
                return
            return self._send_html(SHOP_HTML)
        return self._send_html("<h1>404 Not Found</h1>", status=404)

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        data = json.loads(raw)

        if path == "/api/login":
            u = str(data.get("username", "")).strip()
            p = str(data.get("password", ""))
            if not u or not p:
                return self._send_json(400, {"code": 40001, "message": "用户名和密码不能为空"})
            if u == "tester" and p == "Password123":
                return self._send_json(200, {"code": 0, "message": "登录成功"}, cookie="session_user=tester; Path=/")
            return self._send_json(401, {"code": 40100, "message": "用户名或密码错误"})

        if path == "/api/checkout":
            if not self._is_logged_in():
                return self._send_json(401, {"code": 40101, "message": "请先登录"})
            items = data.get("items", [])
            if not items:
                return self._send_json(400, {"code": 40002, "message": "购物车为空"})
            return self._send_json(200, {"code": 0, "message": "ok", "data": {"order_no": "UI-ORD-20261125"}})

        return self._send_json(404, {"code": 40400, "message": "接口不存在"})


def start_web_server(host: str = "127.0.0.1", port: int = 8900) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), WebShopHandler)


if __name__ == "__main__":
    srv = start_web_server()
    print("🚀 本地 Web 商城靶场已启动: http://127.0.0.1:8900/login")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.server_close()
