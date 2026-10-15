import time
import requests


def get_btc_price():
    url = "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 "
            "Mobile/15E148 Safari/604.1"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        if data.get("code") == "0" and data.get("data"):
            last_price = data["data"][0]["last"]
            print(f"[成功] 当前 OKX BTC-USDT 价格: ${last_price}")
            return last_price
        else:
            print(f"[失败] API 返回异常数据: {data}")
            return None

    except Exception as e:
        print(f"[错误] 请求 OKX API 失败: {e}")
        return None


if __name__ == "__main__":
    print("开始获取 BTC 价格...")
    get_btc_price()
