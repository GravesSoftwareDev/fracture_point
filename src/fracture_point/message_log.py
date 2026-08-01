class MessageLog:
    """Keeps recent messages for on-screen display."""

    def __init__(self, max_messages: int = 30):
        self.messages: list[str] = []
        self.max_messages = max_messages

    def add(self, text: str) -> None:
        self.messages.append(text)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)