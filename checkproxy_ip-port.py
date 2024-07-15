import requests
from tqdm import tqdm
import threading
import queue
import concurrent.futures

def check_protocol(proxy, protocol, timeout):
    proxies = {protocol: proxy}
    try:
        with requests.get("http://httpbin.org/get", proxies=proxies, timeout=timeout) as response:
            return response.status_code == 200, protocol
    except requests.exceptions.RequestException:
        return False, protocol

def check_proxy(proxy, timeout, output_file):
    print(f"Kiểm tra proxy: {proxy}")
    working_protocols = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(check_protocol, proxy, protocol, timeout) 
                   for protocol in ["http", "https", "socks4", "socks5"]]
        for future in concurrent.futures.as_completed(futures):
            success, protocol = future.result()
            if success:
                working_protocols.append(protocol)
                print(f"  - Hoạt động với {protocol}")
            else:
                print(f"  - Không hoạt động với {protocol}")

    if working_protocols:
        with open(output_file, "a") as f_out:
            for protocol in working_protocols:
                f_out.write(f"{protocol}://{proxy.strip()}\n")

def main():
    input_file = "proxy_list_ip-port.txt"
    output_file = "proxy_list_ip-port_good.txt"
    num_threads = 10 
    timeout = 0.5  

    proxy_queue = queue.Queue()
    threads = []

    with open(input_file, "r") as f_in:
        proxies = f_in.readlines()

    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(proxy_queue, timeout, output_file))
        t.start()
        threads.append(t)

    for proxy in tqdm(proxies, desc="Kiểm tra proxy", unit="proxy"):
        proxy_queue.put(proxy.strip())

    for i in range(num_threads):
        proxy_queue.put(None)  # Đánh dấu kết thúc

    for t in threads:
        t.join()

    print("Kiểm tra proxy hoàn tất!")

def worker(proxy_queue, timeout, output_file):
    while True:
        proxy = proxy_queue.get()
        if proxy is None:
            break
        check_proxy(proxy, timeout, output_file)
        proxy_queue.task_done()


if __name__ == "__main__":
    main()
