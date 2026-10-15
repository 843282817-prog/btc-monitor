import time
import requests

# ----------------------------- 1. 基础配置 -----------------------------
BARK_KEY = "4pbUuPZa73KPBtF6vYBp3B"  # 你的 Bark 推送 Key
INST_ID = "BTC-USDT-SWAP"        # OKX 永续合约代码
print("🚀 OKX BTC 监控脚本准备启动...")

# ----------------------------- 2. 工具函数：发送 Bark 推送 -----------------------------
def send_bark_alert(title, body):
    url = f"https://api.day.app/{BARK_KEY}/{title}/{body}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("[推送成功] Bark 通知已发送")
        else:
            print(f"[推送失败] HTTP 状态码: {response.status_code}")
    except Exception as e:
        print(f"[推送异常] {e}")

# ----------------------------- 3. 获取 OKX 公共接口行情数据 -----------------------------
def get_okx_data():
    url = f"https://www.okx.com/api/v5/market/candles?instId={INST_ID}&bar=1H&limit=30"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        if data.get("code") == "0" and data.get("data"):
            candles = data["data"]
            closes = [float(candle[4]) for candle in candles]
            closes.reverse()
            return closes
    except Exception as e:
        print(f"[获取行情异常] {e}")
    return None

# ----------------------------- 4. 主逻辑：计算均线并报警 -----------------------------
def main():
    closes = get_okx_data()
    if not closes or len(closes) < 20:
        print("[数据不足] 无法计算均线")
        return

    current_price = closes[-1]
    ma7 = sum(closes[-7:]) / 7
    ma20 = sum(closes[-20:]) / 20

    print(f"当前价格: {current_price} | MA7: {ma7:.2f} | MA20: {ma20:.2f}")

    if current_price > ma7:
        title = "BTC突破MA7提醒"
        body = f"当前价格 {current_price} 已上穿 MA7 ({ma7:.2f})"
        send_bark_alert(title, body)

if __name__ == "__main__":
    main()
