from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..Audio.ReferenceAudio import ReferenceAudio


class Context:
    def __init__(self):
        self.current_speaker: str = ''
        self.current_prompt_audio: Optional['ReferenceAudio'] = None
        self.text_language: Optional[str] = None  # 覆盖 model.LANGUAGE，为 None 时使用模型默认语言


context: Context = Context()
