"""
UI 自动化全局夹具与钩子配置
核心亮点：
1. 自动启动/关闭本地 Web 靶场
2. logged_in_page 夹具：通过直接注入 Cookie 跳过重复 UI 登录（企业级 UI+API 混合提速技巧！）
3. pytest_runtest_makereport Hook：用例失败时自动全页截图并保存到 reports/screenshots + 挂载 Allure
"""
import sys
import threading
from pathlib import Path
import allure
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mock_web.app import start_web_server

BASE_URL = "http://127.0.0.1:8900"


@pytest.fixture(scope="session", autouse=True)
def mock_web_server():
    """后台自动启动本地迷你电商 Web 靶场"""
    server = start_web_server("127.0.0.1", 8900)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield BASE_URL
    server.shutdown()
    server.server_close()


@pytest.fixture(scope="function")
def logged_in_page(page, mock_web_server):
    """
    黄金提速技巧（面试必讲）：
    测商品加购/结算页时，不需要每次都从登录页填账号密码点登录！
    直接往浏览器上下文注入登录态 Cookie，直达 /shop 页面，节省大量执行时间。
    """
    page.context.add_cookies(
        [
            {
                "name": "session_user",
                "value": "tester",
                "url": mock_web_server,
            }
        ]
    )
    return page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败时自动截图留存现场，并附加到 Allure 报告"""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
        if page:
            shot_dir = ROOT_DIR / "reports" / "screenshots"
            shot_dir.mkdir(parents=True, exist_ok=True)
            safe_name = item.name.replace("[", "_").replace("]", "_").replace("/", "_")
            shot_path = shot_dir / f"{safe_name}.png"
            png_bytes = page.screenshot(path=str(shot_path), full_page=True)
            allure.attach(
                png_bytes,
                name="失败页面全屏截图",
                attachment_type=allure.attachment_type.PNG,
            )
