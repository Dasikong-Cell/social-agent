import os
import functools
import threading
import time
from flask import Flask, request, jsonify
from deepseek_agent import agent
from qq_bot_service import send_to_qq_channel
from scheduler_task import add_timed_task
from dotenv import load_dotenv
from utils.log_utils import write_log
from utils.sensitive_filter import filter_text
from utils.count_utils import add_count, get_today_count

load_dotenv()
app = Flask(__name__)
PORT = int(os.getenv("SERVER_PORT", "8000"))

# 简单内存速率限制（令牌桶），防付费 LLM 接口被刷；生产可用 redis/flask-limiter 替代。
_GEN_LOCK = threading.Lock()
_GEN_HITS: dict = {}

def rate_limit(key: str, limit: int, window: int = 60) -> bool:
    now = time.time()
    with _GEN_LOCK:
        hits = _GEN_HITS.get(key, [])
        hits = [t for t in hits if now - t < window]
        if len(hits) >= limit:
            return False
        hits.append(now)
        _GEN_HITS[key] = hits
    return True

# 服务端 API Key：留空则不强制（便于本机调试）；一旦设置，副作用/外部推送端点必须带 X-API-Key。
API_KEY = os.getenv("SERVER_API_KEY", "")

def require_api_key(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if API_KEY and request.headers.get("X-API-Key") != API_KEY:
            return jsonify({"code": -401, "msg": "未授权"}), 401
        return fn(*args, **kwargs)
    return wrapper

WEB_UI = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI文案Agent</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:20px;color:#333}
.container{max-width:680px;margin:0 auto}
.card{background:#fff;border-radius:16px;padding:28px;box-shadow:0 10px 40px rgba(0,0,0,.15);margin-bottom:16px}
h1{font-size:22px;font-weight:700;margin-bottom:6px;color:#1a1a2e}
.sub{font-size:13px;color:#888;margin-bottom:20px}
.row{display:flex;gap:12px;margin-bottom:14px;flex-wrap:wrap}
.field{flex:1;min-width:140px}
label{display:block;font-size:13px;color:#666;margin-bottom:6px;font-weight:500}
select,textarea{width:100%;padding:10px 12px;border:1.5px solid #e0e0e0;border-radius:10px;font-size:14px;font-family:inherit;background:#fafafa;transition:.2s}
select:focus,textarea:focus{outline:none;border-color:#667eea;background:#fff;box-shadow:0 0 0 3px rgba(102,126,234,.15)}
textarea{resize:vertical;min-height:100px;line-height:1.6}
button{width:100%;padding:12px;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer;transition:.2s;font-family:inherit}
.btn-primary{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 6px 20px rgba(102,126,234,.4)}
.btn-primary:active{transform:translateY(0)}
.btn-primary:disabled{opacity:.6;cursor:not-allowed;transform:none}
.btn-secondary{background:#f0f0f0;color:#555;margin-top:10px}
.btn-secondary:hover{background:#e6e6e6}
.stats{display:flex;gap:12px;margin-bottom:16px}
.stat{flex:1;background:rgba(255,255,255,.15);backdrop-filter:blur(10px);border-radius:12px;padding:14px;text-align:center;color:#fff}
.stat .num{font-size:24px;font-weight:700}
.stat .lbl{font-size:12px;opacity:.8}
.result-box{background:#f8f9ff;border-left:4px solid #667eea;padding:16px;border-radius:0 10px 10px 0;font-size:14px;line-height:1.8;white-space:pre-wrap;word-break:break-word;min-height:40px}
.empty{color:#bbb;text-align:center;font-style:italic;padding:20px}
.error{background:#fff2f0;border-left-color:#ff4d4f;color:#cf1322}
.loading::after{content:'';animation:dots 1.2s steps(4) infinite}
@keyframes dots{0%{content:''}25%{content:'.'}50%{content:'..'}75%{content:'...'}}
</style>
</head>
<body>
<div class="container">
  <div class="stats">
    <div class="stat"><div class="num" id="todayCount">-</div><div class="lbl">今日调用次数</div></div>
    <div class="stat"><div class="num">AI</div><div class="lbl">文案生成引擎</div></div>
  </div>
  <div class="card">
    <h1>AI文案Agent</h1>
    <div class="sub">选择场景与风格，输入需求，一键生成专业文案</div>
    <div class="row">
      <div class="field">
        <label>使用场景</label>
        <select id="scene">
          <option>朋友圈</option>
          <option>小红书</option>
          <option>短视频文案</option>
          <option>通知公告</option>
          <option>祝福语</option>
          <option>商务话术</option>
        </select>
      </div>
      <div class="field">
        <label>文案风格</label>
        <select id="style">
          <option>简约</option>
          <option>文艺</option>
          <option>搞笑</option>
          <option>正式</option>
          <option>可爱</option>
          <option>高冷</option>
        </select>
      </div>
      <div class="field" style="max-width:120px">
        <label>字数上限</label>
        <select id="maxLen">
          <option value="100">100字</option>
          <option value="200" selected>200字</option>
          <option value="300">300字</option>
          <option value="500">500字</option>
        </select>
      </div>
    </div>
    <label>文案需求</label>
    <textarea id="require" placeholder="例如：写一条春日下午茶的朋友圈文案"></textarea>
    <button class="btn-primary" id="genBtn" onclick="generate()">✨ 立即生成</button>
  </div>
  <div class="card">
    <label>生成结果</label>
    <div class="result-box" id="result"><span class="empty">等待生成...</span></div>
    <button class="btn-secondary" onclick="copyResult()">📋 复制文案</button>
  </div>
</div>
<script>
async function loadCount(){try{const r=await fetch('/api/count');const d=await r.json();document.getElementById('todayCount').textContent=d.todayCount}catch(e){}}
loadCount();setInterval(loadCount,10000);
async function generate(){
  const btn=document.getElementById('genBtn');
  const box=document.getElementById('result');
  const req=document.getElementById('require').value.trim();
  if(!req){box.innerHTML='<span class="empty error">请先输入文案需求</span>';return}
  btn.disabled=true;btn.textContent='生成中';
  box.innerHTML='<span class="empty loading">AI正在创作';
  try{
    const r=await fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({scene:document.getElementById('scene').value,style:document.getElementById('style').value,require:req,maxLen:parseInt(document.getElementById('maxLen').value)})});
    const d=await r.json();
    if(d.code===0){box.textContent=d.data;document.getElementById('todayCount').textContent=d.todayCount}
    else{box.innerHTML='<span class="result-box error" style="background:#fff2f0;border-left-color:#ff4d4f;color:#cf1322">'+d.msg+'</span>'}
  }catch(e){box.innerHTML='<span class="result-box error" style="background:#fff2f0;border-left-color:#ff4d4f;color:#cf1322">网络错误：'+e.message+'</span>'}
  btn.disabled=false;btn.textContent='✨ 立即生成';
}
function copyResult(){const t=document.getElementById('result').textContent;if(!t||t==='等待生成...'||t.startsWith('AI正在'))return;navigator.clipboard.writeText(t).then(()=>{document.querySelector('.btn-secondary').textContent='✅ 已复制';setTimeout(()=>{document.querySelector('.btn-secondary').textContent='📋 复制文案'},1500)})}
document.getElementById('require').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey))generate()});
</script>
</body>
</html>"""

@app.route("/")
def index():
    return WEB_UI

@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"status": "ok"})

@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(silent=True) or {}
    scene = data.get("scene", "朋友圈")
    style = data.get("style", "简约")
    req = str(data.get("require", "") or "")
    try:
        max_len = int(data.get("maxLen", 200) or 200)
    except (TypeError, ValueError):
        max_len = 200
    max_len = max(1, min(max_len, 2000))  # 防超长输出放大 LLM 调用成本

    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if not rate_limit(f"gen:{client_ip}", limit=20, window=60):
        return jsonify({"code": -429, "msg": "请求过于频繁，请稍后再试"})

    if not req.strip():
        return jsonify({"code": -1, "msg": "请输入文案需求"})

    is_bad, check_msg = filter_text(req)
    if is_bad:
        write_log(f"拦截违规请求：{req}")
        return jsonify({"code": -99, "msg": check_msg})

    try:
        result = agent.generate(scene, style, req)
        if len(result) > max_len:
            result = result[:max_len] + "..."
        add_count()
        today_num = get_today_count()
        write_log(f"生成成功｜场景:{scene} 风格:{style} 今日累计调用:{today_num}次")
        return jsonify({
            "code": 0,
            "data": result,
            "todayCount": today_num
        })
    except Exception as e:
        write_log(f"生成异常：{str(e)}")
        # 不向客户端泄露原始异常细节
        return jsonify({"code": -2, "msg": "生成失败，请稍后重试"})

@app.route("/api/send_qq", methods=["POST"])
@require_api_key
def api_send_qq():
    data = request.get_json(silent=True) or {}
    text = str(data.get("content", "") or "")
    if not text:
        return jsonify({"code": -1, "msg": "文案为空"})
    res = send_to_qq_channel(text)
    if res:
        return jsonify({"code": 0, "msg": "已推送至QQ频道"})
    else:
        return jsonify({"code": -3, "msg": "QQ推送接口异常"})

@app.route("/api/task", methods=["POST"])
@require_api_key
def api_task():
    data = request.get_json(silent=True) or {}
    t = data.get("time")
    c = data.get("content")
    res = add_timed_task(t, c)
    if res:
        return jsonify({"code": 0, "msg": f"已设置定时 {t} 发布"})
    else:
        return jsonify({"code": -4, "msg": "定时时间格式错误，请用 HH:MM"})

@app.route("/api/count", methods=["GET"])
def get_count():
    num = get_today_count()
    return jsonify({"code": 0, "todayCount": num})

if __name__ == "__main__":
    write_log("===== 服务启动 =====")
    print("=== DeepSeek文案Agent桌面服务已启动 ===")
    bind_host = os.getenv("BIND_HOST", "127.0.0.1")
    print(f"本地地址：http://{bind_host}:{PORT}")
    print("关闭当前窗口即可停止服务")
    # 默认仅监听本机；如需局域网/公网访问，设置 BIND_HOST=0.0.0.0 并务必配置 SERVER_API_KEY。
    app.run(host=bind_host, port=PORT, debug=False)
