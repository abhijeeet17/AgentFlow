from abc import ABC, abstractmethod

class BaseIntegration(ABC):
    @abstractmethod
    async def send_notification(self, message: str) -> bool:
        pass
