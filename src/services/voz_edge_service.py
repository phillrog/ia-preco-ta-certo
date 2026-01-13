import base64
import edge_tts
import asyncio

class VozEdgeService:
    def __init__(self, voice="pt-BR-FranciscaNeural"):
        self.voice = voice

    async def _gerar_audio_async(self, texto):
        """Método interno assíncrono para o Edge-TTS."""
        try:
            communicate = edge_tts.Communicate(texto, self.voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            if not audio_data:
                return None
            return base64.b64encode(audio_data).decode()
        except Exception as e:
            print(f"Erro na síntese de voz: {e}")
            return None

    def gerar_audio_base64(self, texto):
        """Interface síncrona para o Streamlit rodar o código async."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            resultado = loop.run_until_complete(self._gerar_audio_async(texto))
            loop.close()
            return resultado
        except Exception as e:
            print(f"Erro ao rodar loop de áudio: {e}")
            return None