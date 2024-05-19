import time
import requests

class CircuitBreaker:
    def __init__(self, max_retries=3, retry_delay=1, failure_threshold=5, recovery_timeout=10):
        self.max_retries = max_retries  # Максимальное количество повторных попыток
        self.retry_delay = retry_delay  # Задержка между повторными попытками
        self.failure_threshold = failure_threshold  # Порог количества ошибок для переключения в режим "отключено"
        self.recovery_timeout = recovery_timeout  # Время ожидания перед восстановлением после переключения в режим "отключено"

        self.state = "closed"  # Состояние алгоритма Circuit Breaker
        self.failure_count = 0  # Количество ошибок
        self.last_failure_time = None  # Время последней ошибки

    def send_request_with_circuit_breaker(self, url):
        if self.state == "open":
            #"Полу-открыт" (half-open): после периода ожидания, определенного в recovery_timeout,
            # Circuit Breaker переключается в состояние "полу-открыт". В это состоянии Circuit Breaker
            # разрешает один-два запроса к сервису для проверки его работоспособности.
            # Если запросы возвращают успешный результат, то Circuit Breaker переходит в состояние "закрыт" и
            # снова начинает разрешать все запросы. Если запросы возвращают ошибку,
            # Circuit Breaker снова переключается в состояние "открыт".
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half_open"  # Переключаемся в режим "полу-открыт"
            else:
                raise Exception("Circuit Breaker is open. Request rejected.")

        retries = 0
        while retries < self.max_retries:
            try:
                response = requests.get(url)
                if response.status_code < 500:  # Если получен ответ с кодом ошибки < 500, вернуть ответ
                    self.reset()  # Сбрасываем счетчик ошибок и состояние алгоритма
                    return response
                else:
                    print("Server error ({}). Retrying...".format(response.status_code))
                    retries += 1
                    time.sleep(self.retry_delay)
            except requests.RequestException as e:
                print("Request failed:", e)
                retries += 1
                time.sleep(self.retry_delay)

        self.handle_failure()  # Обрабатываем ошибку и увеличиваем счетчик ошибок
        raise Exception("Max retries exceeded. Request failed.")

    def handle_failure(self):
        #"Открыт" (open): когда количество ошибок достигает или превышает заданный порог (failure_threshold),
        # Circuit Breaker переключается в режим "открыт". В этом состоянии все запросы считаются неуспешными,
        # и Circuit Breaker выбрасывает исключение без отправки запроса сервису.
        # Время последней ошибки записывается в переменную last_failure_time.
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "open"  # Переключаем алгоритм в режим "открыт" при достижении порога ошибок
            self.last_failure_time = time.time()

    def reset(self):
        #"Закрыт" (closed): в этом состоянии Circuit Breaker позволяет выполнить запросы к сервису как обычно.
        # Количество ошибок не превышает заданный порог (failure_threshold),
        # и время восстановления (recovery_timeout) не прошло после последней ошибки.
        self.failure_count = 0
        self.state = "closed"  # Сбрасываем счетчик ошибок и возвращаемся в режим "закрыт"

# Пример использования
client = CircuitBreaker(max_retries=10, retry_delay=4, failure_threshold=3, recovery_timeout=20)

try:
    response = client.send_request_with_circuit_breaker("http://localhost:5000/api")
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
