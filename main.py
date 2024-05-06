from abstract import Circuit_Breaker
import time
import requests
import random


class Circuit_Breaker(Circuit_Breaker):
    SUCCESS_FLAG = 200

    def __init__(self, counter_limit=6, timout=40,  **kwargs):
        super().__init__(counter_limit, timout)
        self.url = kwargs.get("url", None)
        if self.url is None:
            raise ValueError("Отсутствующий аргумент url-адреса")

    def operation(self):
        try:
            res = requests.get(self.url, timeout=self.timeout)
        except Exception as e:
            print("Error", e)
        return res

    def closed(self):
        if self.state == self.State.CLOSED:
            failure_counter = 0
            while (failure_counter < self.counter_limit):
                try:
                    res = self.operation()
                    resp = res.status_code
                    if int(resp) == self.SUCCESS_FLAG:
                        return res
                    else:
                        failure_counter += 1
                except Exception as e:
                    failure_counter += 1
                time.sleep((random.randint(0, 1000) / 1000))
            else:
                self.state = self.State.OPEND
                self.open()

    def open(self):
        if self.state == 'open':
            time.sleep(self.timout)
            self.state = self.State.HALF_OPEN
            self.half_open()
        else:
            raise Exception(
                f"Вызвано неправильное состояние: {self.state}")

    def half_open(self):
        if self.state == self.State.HALF_OPEN:
            try:
                res = self.operation()
                if res.status_code == self.SUCCESS_FLAG:
                    self.state = self.State.CLOSED  # yeah!
                    self.closed()
                else:
                    self.state = self.State.OPEND  # oops...
                    self.open()
            except Exception as e:
                self.current_state = self.State.OPEND

                self.open()


if __name__ == "__main__":
    cb = Circuit_Breaker(url="https://medium.com/new-story")
