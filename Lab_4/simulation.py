import heapq
import threading
import time
from typing import Dict

import numpy as np


class SMO(threading.Thread):
    def __init__(
        self,
        arrival_rate: float,
        service_rate: float,
        max_queue_size: int,
        total_simulation_time: int,
        time_scale_factor: int = 3600,
    ) -> None:
        """
        Инициализация симуляции.

        Инициализирует все параметры симуляции и готовит очереди событий, очереди заявок,
        а также переменные для отслеживания статистики. Конструктор запускает базовый конструктор потока.

        :param arrival_rate: Интенсивность поступления заявок в систему (заявки/мин).
        :param service_rate: Интенсивность обслуживания (заявки/мин).
        :param max_queue_size: Максимальный размер очереди (в случае, если оба сервера заняты).
        :param total_simulation_time: Общая длительность симуляции в минутах.
        :param time_scale_factor: Масштаб времени (сколько минут симуляции проходят за одну секунду реального времени).
        """
        super().__init__()
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.max_queue_size = max_queue_size
        self.total_simulation_time = total_simulation_time
        self.time_scale_factor = time_scale_factor
        self.stop_event = threading.Event()  # Событие для остановки симуляции
        self.lock = threading.Lock()  # Мьютекс для синхронизации

        # Очередь событий для симуляции
        self.event_queue = []
        heapq.heappush(
            self.event_queue, (0, "arrival", 0)
        )  # Начальное событие - первое поступление заявки

        # Очередь заявок
        self.request_queue = []

        # Переменные для отслеживания статистики
        self.simulated_time = 0
        self.server_1_free_at = 0  # Время, когда сервер 1 станет свободным
        self.server_2_free_at = 0  # Время, когда сервер 2 станет свободным
        self.served_requests = 0  # Количество обслуженных заявок
        self.rejected_requests = 0  # Количество отклонённых заявок
        self.total_waiting_time = 0  # Общее время ожидания
        self.total_system_time = 0  # Общее время нахождения заявки в системе
        self.total_arrivals = 0  # Общее количество поступивших заявок
        self.is_server_1_busy = False  # Статус занятости сервера 1
        self.is_server_2_busy = False  # Статус занятости сервера 2

    def run(self) -> None:
        """
        Запускает симуляцию, обрабатывая события в очереди.

        Функция выполняет симуляцию, последовательно обрабатывая события: поступление заявок,
        завершение обслуживания заявок. Каждое событие обрабатывается с временной синхронизацией.
        Поток работает до тех пор, пока не будет остановлен или не завершится симуляция.

        События обрабатываются в зависимости от времени их наступления.
        Каждое событие также синхронизируется с реальным временем, чтобы симуляция
        не выполнялась слишком быстро.
        """
        start_real_time = time.time()  # Записываем реальное время начала симуляции
        while not self.stop_event.is_set():
            with self.lock:
                # Если очередь событий пуста или симуляция завершена, завершаем выполнение
                if (
                    not self.event_queue
                    or self.simulated_time >= self.total_simulation_time
                ):
                    break

                # Обработка следующего события из очереди
                event_time, event_type, request_id = heapq.heappop(self.event_queue)
                self.simulated_time = event_time

                # В зависимости от типа события выполняется соответствующий метод
                if event_type == "arrival":
                    self.handle_arrival(request_id)
                elif event_type == "departure_1":
                    self.handle_departure(request_id, 1)
                elif event_type == "departure_2":
                    self.handle_departure(request_id, 2)

            # Синхронизация с реальным временем
            simulated_time_in_seconds = self.simulated_time / self.time_scale_factor
            real_time_elapsed = time.time() - start_real_time
            if simulated_time_in_seconds > real_time_elapsed:
                time.sleep(simulated_time_in_seconds - real_time_elapsed)

    def handle_arrival(self, request_id: int) -> None:
        """
        Обработка события поступления новой заявки.

        Когда заявка поступает в систему, мы проверяем, есть ли свободные серверы.
        Если оба сервера заняты, заявка добавляется в очередь ожидания. Если хотя бы
        один сервер свободен, заявка немедленно обслуживается.

        :param request_id: Идентификатор поступившей заявки (для уникальности).
        """
        self.total_arrivals += 1

        # Если оба сервера заняты и очередь не переполнена, добавляем заявку в очередь
        if (
            self.is_server_1_busy
            and self.is_server_2_busy
            and len(self.request_queue) < self.max_queue_size
        ):
            self.request_queue.append(self.simulated_time)
        # Если сервер 1 свободен, начинаем его обслуживать
        elif not self.is_server_1_busy:
            service_time = np.random.exponential(1 / self.service_rate)
            self.server_1_free_at = self.simulated_time + service_time
            self.total_system_time += service_time
            self.is_server_1_busy = True
            heapq.heappush(
                self.event_queue, (self.server_1_free_at, "departure_1", request_id)
            )
            self.served_requests += 1
        # Если сервер 2 свободен, начинаем его обслуживать
        elif not self.is_server_2_busy:
            service_time = np.random.exponential(1 / self.service_rate)
            self.server_2_free_at = self.simulated_time + service_time
            self.total_system_time += service_time
            self.is_server_2_busy = True
            heapq.heappush(
                self.event_queue, (self.server_2_free_at, "departure_2", request_id)
            )
            self.served_requests += 1
        # Если оба сервера заняты и очередь переполнена, заявка отклоняется
        else:
            self.rejected_requests += 1

        # Планируем следующее поступление заявки
        if self.simulated_time < self.total_simulation_time:
            inter_arrival_time = np.random.exponential(1 / self.arrival_rate)
            next_arrival_time = self.simulated_time + inter_arrival_time
            heapq.heappush(
                self.event_queue, (next_arrival_time, "arrival", request_id + 1)
            )

    def handle_departure(self, request_id: int, server_id: int) -> None:
        """
        Обработка завершения обслуживания заявки (отъезд).

        Когда заявка обслуживается и уходит из системы, проверяется, есть ли заявки в очереди.
        Если есть, то следующая заявка обслуживается немедленно. Если очередь пуста, сервер становится свободным.

        :param request_id: Идентификатор заявки, которая завершила обслуживание.
        :param server_id: Идентификатор сервера (1 или 2), на котором завершилось обслуживание.
        """
        if self.request_queue:
            arrival_time = self.request_queue.pop(0)
            waiting_time = self.simulated_time - arrival_time
            self.total_waiting_time += waiting_time
            service_time = np.random.exponential(1 / self.service_rate)
            if server_id == 1:
                self.server_1_free_at = self.simulated_time + service_time
                self.is_server_1_busy = True
                heapq.heappush(
                    self.event_queue, (self.server_1_free_at, "departure_1", request_id)
                )
            else:
                self.server_2_free_at = self.simulated_time + service_time
                self.is_server_2_busy = True
                heapq.heappush(
                    self.event_queue, (self.server_2_free_at, "departure_2", request_id)
                )
            self.total_system_time += waiting_time + service_time
            self.served_requests += 1
        else:
            if server_id == 1:
                self.is_server_1_busy = False
            else:
                self.is_server_2_busy = False

    def stop_simulation(self) -> None:
        """
        Остановка симуляции.

        Устанавливает событие остановки, что приводит к завершению работы потока,
        как только текущая симуляция достигнет завершения.
        """
        self.total_simulation_time = self.simulated_time
        self.stop_event.set()

    def get_simulation_results(self) -> Dict[str, float]:
        """
        Получение результатов симуляции.

        Рассчитывает и возвращает различные метрики симуляции, такие как:
        - Вероятность отказа (отношение отклонённых заявок к общему числу заявок).
        - Среднее количество заявок в очереди и в системе.
        - Среднее время нахождения заявки в системе.

        :return: Словарь с результатами симуляции, где ключами являются метрики, а значениями — их величины.
        """
        with self.lock:
            rejection_rate = (
                self.rejected_requests / self.total_arrivals
                if self.total_arrivals > 0
                else 0
            )
            avg_system_time = (
                self.total_system_time / self.served_requests
                if self.served_requests > 0
                else 0
            )
            avg_queue_length = (
                self.total_waiting_time / self.total_simulation_time
                if self.total_simulation_time > 0
                else 0
            )
            avg_service_length = (
                (self.total_system_time - self.total_waiting_time)
                / self.total_simulation_time
                if self.total_simulation_time > 0
                else 0
            )
            avg_system_length = (
                self.total_system_time / self.total_simulation_time
                if self.total_simulation_time > 0
                else 0
            )

            return {
                "rejection_rate": rejection_rate,
                "avg_queue_length": avg_queue_length,
                "avg_service_length": avg_service_length,
                "avg_system_length": avg_system_length,
                "avg_system_time": avg_system_time,
                "served_requests": self.served_requests,
                "rejected_requests": self.rejected_requests,
                "total_arrivals": self.total_arrivals,
            }


# Пример использования
if __name__ == "__main__":
    arrival_rate = 1  # Интенсивность поступления заявок (заявки/мин)
    service_rate = 0.5  # Интенсивность обслуживания (заявки/мин)
    max_queue_size = 4  # Максимальный размер очереди
    total_simulation_time = 10000000  # Время симуляции (минуты)
    time_scale_factor = (
        3600  # Масштаб времени: 1 секунда реального времени = 3600 минут симуляции
    )

    simulation_thread = SMO(
        arrival_rate,
        service_rate,
        max_queue_size,
        total_simulation_time,
        time_scale_factor,
    )
    simulation_thread.start()

    try:
        while True:
            command = input("Введите 0, чтобы прекратить симуляцию: ")
            if command == "0":
                simulation_thread.stop_simulation()
                simulation_thread.join()
                break
    except KeyboardInterrupt:
        simulation_thread.stop_simulation()
        simulation_thread.join()

    results = simulation_thread.get_simulation_results()
    print("\nРезультаты симуляции:")
    print(f"Всего поступило заявок: {results['total_arrivals']}")
    print(f"Обслужено заявок: {results['served_requests']}")
    print(f"Отклонено заявок: {results['rejected_requests']}")
    print(f"Вероятность отказа: {results['rejection_rate']:.4f}")
    print(
        f"Среднее количество заявок под обслуживанием: {results['avg_service_length']:.4f} мин"
    )
    print(f"Среднее количество заявок в очереди: {results['avg_queue_length']:.4f}")
    print(f"Среднее количество заявок в системе: {results['avg_system_length']:.4f}")
    print(f"Среднее время нахождения заявки в системе: {results['avg_system_time']:.4f}")
