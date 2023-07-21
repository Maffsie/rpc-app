from dataclasses import dataclass


@dataclass
class TailscaleHost:
    hostname: str
    extern: bool
    a4: str
    a6: str

    _publish_tag: str
    _tags: list

    @property
    def publish(self) -> bool:
        return f"tag:{self._publish_tag}" in self._tags
