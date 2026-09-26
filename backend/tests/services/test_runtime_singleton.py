"""并发请求首次进入服务时，默认运行时只能创建一次。"""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from time import sleep

from app.api import runtime

# 同时请求运行时的线程数，用于暴露惰性初始化竞争。
CONCURRENT_REQUEST_COUNT = 6
# 模拟 SQLite 表初始化耗时，使线程竞争稳定复现。
SIMULATED_INIT_DELAY_SECONDS = 0.05


def test_default_runtime_is_initialized_once_for_concurrent_requests(monkeypatch) -> None:
    runtime.reset_runtime()
    ready = Barrier(CONCURRENT_REQUEST_COUNT)
    created: list[object] = []

    def build_once() -> object:
        sleep(SIMULATED_INIT_DELAY_SECONDS)
        value = object()
        created.append(value)
        return value

    monkeypatch.setattr(runtime, "build_runtime", build_once)

    def request_runtime() -> object:
        ready.wait()
        return runtime.get_runtime()

    try:
        with ThreadPoolExecutor(max_workers=CONCURRENT_REQUEST_COUNT) as executor:
            results = list(executor.map(lambda _: request_runtime(), range(CONCURRENT_REQUEST_COUNT)))
        assert len(created) == 1
        assert all(item is results[0] for item in results)
    finally:
        runtime.reset_runtime()
