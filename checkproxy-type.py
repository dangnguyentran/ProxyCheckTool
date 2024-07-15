import asyncio
import httpx
from httpx_socks import AsyncProxyTransport
from tqdm import tqdm

# Đọc danh sách proxy từ file proxy_list.txt
def load_proxies(filename):
    with open(filename, 'r') as f:
        proxies = [line.strip() for line in f if line.strip()]
    return proxies

async def check_proxy(proxy, progress_bar):
    url = 'http://www.google.com'  # URL để kiểm tra
    scheme = proxy.split("://")[0]

    try:
        if scheme in ['http', 'https']:
            async with httpx.AsyncClient(proxies=proxy, timeout=500) as client:
                response = await client.get(url)
        elif scheme in ['socks4', 'socks5']:
            transport = AsyncProxyTransport.from_url(proxy)
            async with httpx.AsyncClient(transport=transport, timeout=500) as client:
                response = await client.get(url)
        else:
            raise ValueError(f"Unknown proxy scheme: {scheme}")

        if response.status_code == 200:
            print(f"Proxy {proxy} hoạt động.")
            return proxy
        else:
            print(f"Proxy {proxy} không hoạt động (status code: {response.status_code}).")
            return None
    except Exception as e:
        print(f"Proxy {proxy} không hoạt động (lỗi: {e}).")
        return None
    finally:
        progress_bar.update(1)

async def main():
    # Load proxies từ file proxy_list.txt
    proxies = load_proxies('proxy_list.txt')

    # Tạo thanh tiến trình
    progress_bar = tqdm(total=len(proxies), desc="Đang kiểm tra proxy", ncols=100)

    tasks = [check_proxy(proxy, progress_bar) for proxy in proxies]
    results = await asyncio.gather(*tasks)
    good_proxies = [proxy for proxy in results if proxy is not None]

    # Lưu các proxy hoạt động vào file proxygood.txt
    with open('proxygood.txt', 'w') as f:
        for proxy in good_proxies:
            f.write(f"{proxy}\n")
    
    progress_bar.close()

# Chạy kiểm tra các proxy
asyncio.run(main())
