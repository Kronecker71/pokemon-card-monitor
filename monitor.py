import time
import requests
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# --- 監視対象の設定（テスト用を削除済み） ---
WATCH_LIST = {
    "4521329431161": "ポケモンカードゲーム メガブレイブ BOX",
    "4521329431185": "ポケモンカードゲーム MEGA 拡張パック メガシンフォニア BOX",
    "4521329431529": "ポケモンカードゲーム MEGA 拡張パック インフェルノX BOX",
    "4521329431932": "ポケモンカードゲーム MEGA ハイクラスパック MEGAドリームex BOX",
    "4521329432274": "ポケモンカードゲーム MEGA 拡張パック ムニキスゼロ BOX",
    "4521329432786": "ポケモンカードゲーム MEGA 拡張パック ニンジャスピナー BOX",
    "4521329362342": "ポケモンカードゲーム ハイクラスパック テラスタルフェスex BOX",
    "4521329462011": "ポケモンカードゲーム MEGA スペシャルカードセット メガエルレイドex"
}

# --- 設定 ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1485526455566860472/wNEEQt1gWWFqzEGOaWHL8LJ-mQM5Bnsh-m-JoWw7vl07C1A9nxdUxrX5yHZ5BySs4Jxp"
SHOW_BROWSER = False

def send_discord_embed(name, url):
    if not DISCORD_WEBHOOK_URL or not DISCORD_WEBHOOK_URL.startswith("http"):
        return
    
    data = {
        "content": f"🚨 **{name}** 🚨\n検索にヒットしました！在庫復活の可能性があります！",
        "embeds": [{
            "title": f"🛒 {name} の購入ページへ",
            "description": "今すぐ上のリンクから確認してください！",
            "url": url,
            "color": 16711680
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
        print(f"[{name}] 🔔 Discordへ通知を送信しました！")
    except Exception as e:
        print(f"通知エラー: {e}")

def check_stock():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not SHOW_BROWSER)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        for jan, name in WATCH_LIST.items():
            url = f"https://www.toysrus.co.jp/search/?q={jan}"
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(2000)
                
                text_content = page.locator("body").inner_text()
                clean_text = text_content.replace(" ", "").replace("　", "").replace("\n", "")
                
                if "検索結果1" in clean_text:
                    send_discord_embed(name, page.url)
                elif "一致する商品はありません" in clean_text:
                    pass
                else:
                    pass

            except Exception as e:
                print(f"[{name}] 取得エラー: {e}")

        browser.close()

def wait_until_next_5_min():
    now = datetime.now()
    next_minute = ((now.minute // 5) + 1) * 5
    next_run_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=next_minute)
    
    wait_seconds = (next_run_time - now).total_seconds()
    # 修正: '%H:%M:%00' を '%H:%M:00' に直しました！
    print(f"--- 次の確認時刻 [{next_run_time.strftime('%H:%M:00')}] まで {int(wait_seconds)}秒 待機します ---")
    time.sleep(wait_seconds)

if __name__ == "__main__":
    print("🤖 トイザらス自動監視システムを起動しました！")
    
    while True:
        wait_until_next_5_min()
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 定期チェックを開始します...")
        check_stock()
        print("チェック完了。")