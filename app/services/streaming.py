import asyncio
import json
import logging
import os
import tempfile
import time
from io import DEFAULT_BUFFER_SIZE

import websockets
from pydub import AudioSegment
from requests import Session

API_BASE = "https://openapi.vito.ai"

SAMPLE_RATE = 8000
BYTES_PER_SAMPLE = 2


# 본 예제에서는 스트리밍 입력을 음성파일을 읽어서 시뮬레이션 합니다.
# 실제사용시에는 마이크 입력 등의 실시간 음성 스트림이 들어와야합니다.
class FileStreamer:
    def __init__(self, file):
        file_name = os.path.basename(file)
        i = file_name.rindex(".")
        audio_file_8k_path = (
            os.path.join(tempfile.gettempdir(), file_name[:i])
            + "_"
            + str(SAMPLE_RATE)
            + ".wav"
        )
        self.filepath = audio_file_8k_path
        audio = AudioSegment.from_file(file=file, format=file[i + 1 :])
        audio = audio.set_frame_rate(SAMPLE_RATE)
        audio = audio.set_channels(1)
        audio.export(audio_file_8k_path, format="wav")
        self.file = open(audio_file_8k_path, "rb")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        os.remove(self.filepath)

    async def read(self, size):
        if size > 1024 * 1024:
            size = 1024 * 1024
        await asyncio.sleep(size / (SAMPLE_RATE * BYTES_PER_SAMPLE))
        content = self.file.read(size)
        return content


class RTZROpenAPIClient:
    def __init__(self, client_id, client_secret):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self.client_id = client_id
        self.client_secret = client_secret
        self._sess = Session()
        self._token = None

    @property
    def token(self):
        if self._token is None or self._token["expire_at"] < time.time():
            resp = self._sess.post(
                API_BASE + "/v1/authenticate",
                data={"client_id": self.client_id, "client_secret": self.client_secret},
            )
            resp.raise_for_status()
            self._token = resp.json()
        return self._token["access_token"]

    async def streaming_transcribe(self, filename, config=None):
        if config is None:
            config = dict(
                sample_rate=str(SAMPLE_RATE),
                encoding="LINEAR16",
                use_itn="true",
                use_disfluency_filter="false",
                use_profanity_filter="false",
            )

        # 쿼리 매개변수를 올바른 형식으로 생성
        query_params = "&".join([f"{k}={v}" for k, v in config.items()])
        STREAMING_ENDPOINT = f"wss://{API_BASE.split('://')[1]}/v1/transcribe:streaming?{query_params}"
        
        conn_kwargs = dict(extra_headers={"Authorization": "bearer " + self.token})

        async def streamer(websocket):
            with FileStreamer(filename) as f:
                while True:
                    buff = await f.read(DEFAULT_BUFFER_SIZE)
                    if buff is None or len(buff) == 0:
                        break
                    await websocket.send(buff)
                await websocket.send("EOS")

        async def transcriber(websocket):
            async for msg in websocket:
                msg = json.loads(msg)
                print(msg)
                if msg["final"]:
                    print("final ended with " + msg["alternatives"][0]["text"])
                    
        async with websockets.connect(STREAMING_ENDPOINT, **conn_kwargs) as websocket:
            await asyncio.gather(
                streamer(websocket),
                transcriber(websocket),
            )
            
        return {"status": "completed"} 