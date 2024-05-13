import time
import requests

class RetryClient:
    def __init__(self, max_retries=3, retry_delay=1):
        self.max_retries = max_retries  # Максимальное количество повторных попыток
        self.retry_delay = retry_delay  # Задержка между повторными попытками

    def send_request_with_retry(self, url):
        retries = 0
        while retries < self.max_retries:
            try:
                response = requests.get(url)
                if response.status_code < 500:  # Если получен ответ с кодом ошибки < 500, вернуть ответ
                    return response
                else:
                    print("Server error ({}). Retrying...".format(response.status_code))
                    retries += 1
                    time.sleep(self.retry_delay)
            except requests.RequestException as e:
                print("Request failed:", e)
                retries += 1
                time.sleep(self.retry_delay)

        raise Exception("Max retries exceeded. Request failed.")

# Пример использования
client = RetryClient(max_retries=10, retry_delay=4)

try:
    response = client.send_request_with_retry("http://localhost:5000/api")  
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
