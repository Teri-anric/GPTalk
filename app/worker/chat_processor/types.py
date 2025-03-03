import time
from dataclasses import dataclass, field
from datetime import datetime

from app.db import ChatAISettings


@dataclass
class ChatProcessInfo:
    chat_id: int
    last_processed: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    max_not_response_time: float | None = None
    min_delay_between_messages: float | None = None
    last_seen_date: datetime = field(default_factory=datetime.now)

    def update_settings(self, chat_setting: ChatAISettings):
        self.max_not_response_time = chat_setting.max_not_response_time
        self.min_delay_between_messages = chat_setting.min_delay_between_messages

    def is_ready_to_process(self) -> bool:
        is_ready = False
        time_diff = time.time() - self.last_processed
        # Check max delay
        if self.max_not_response_time is not None:
            is_ready = time_diff > self.max_not_response_time
        # Check last updated
        if self.last_updated >= self.last_processed:
            is_ready = True
        # Check min delay
        if is_ready and self.min_delay_between_messages is not None:
            is_ready = time_diff > self.min_delay_between_messages
        # Update last processed
        if is_ready:
            self.last_seen_date = self.last_processed or datetime.now()
            self.last_processed = time.time()
        return is_ready

    def set_last_updated(self, last_updated: float):
        self.last_updated = last_updated
