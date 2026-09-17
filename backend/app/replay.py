"""Replay controller with a simulated clock. Owner: Person A.

Reads messages from messages.sqlite in timestamp order and calls pipeline.process()
as the simulated clock passes each message. All "now" logic uses the simulated time.
Threads touching Lucene must call lucene.getVMEnv().attachCurrentThread().
"""


class ReplayController:
    def start(self, speed: float = 60, start_ts: int | None = None) -> dict:
        raise NotImplementedError

    def pause(self) -> dict:
        raise NotImplementedError

    def reset(self) -> dict:
        raise NotImplementedError

    def status(self) -> dict:
        """{"status", "now", "speed", "processed", "total"}"""
        raise NotImplementedError

    def now(self) -> int:
        """Current simulated time, epoch ms."""
        raise NotImplementedError
