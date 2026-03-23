import os
import time
import requests
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# --- 監視対象の設定 ---
WATCH_LIST = {
    "4521329427270": "スタートデッキ100　バトルコレクション",
    "4521329431161": "ポケモンカードゲーム メガブレイブ BOX",
    "4521329431185": "ポケモンカードゲーム MEGA 拡張パック メガシンフォニア BOX",
    "4521329431529": "ポケモンカードゲーム MEGA 拡張パック インフェルノX BOX",
    "4521329431932": "ポケモンカードゲーム MEGA ハイクラスパック MEGAドリームex BOX",
    "4521329432274": "ポケモンカードゲーム MEGA 拡張パック ムニキスゼロ BOX",
    "4521329432786": "ポケモンカードゲーム MEGA 拡張パック ニンジャスピナー BOX",
    "4521329362342": "ポケモンカードゲーム ハイクラスパック テラスタルフェスex BOX",
    "4521329462011": "ポケモンカードゲーム MEGA スペシャルカードセット メガエルレイドex"
}

# --- 設定（GitHub Secretsから読み込み） ---
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord_embed(name, url):
    if not DISCORD_WEBHOOK_URL:
        return
    
    data = {
        "content": f"🚨 **{name}** 🚨\n検索にヒットしました！在庫復活の可能性があります！",
        "embeds": [{
            "title": f"🛒 {name} の購入ページへ",
            "url": url,
            "color": 16711680
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
    except:
        pass

def check_stock():
    with sync_playwright() as p:
        # GitHub Actions環境では headless=True が必須
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        for jan, name in WATCH_LIST.items():
            url = f"https://www.toysrus.co.jp/search/?q={jan}"
            try:
                # タイムアウトを少し長めに設定
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)
                
                text_content = page.locator("body").inner_text()
                clean_text = text_content.replace(" ", "").replace("　", "").replace("\n", "")
                
                if "検索結果1" in clean_text:
                    print(f"[{name}] 🌟 ヒット！")
                    send_discord_embed(name, page.url)
                else:
                    print(f"[{name}] 在庫なし")

            except Exception as e:
                print(f"[{name}] 取得エラー: {e}")

        browser.close()

if __name__ == "__main__":
    # GitHub Actions側で5分おきに叩くので、while True（ループ）は不要です
    check_stock()
