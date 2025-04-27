import os
import tempfile
import json
import logging
from typing import List
from io import DEFAULT_BUFFER_SIZE
import websockets

from fastapi import APIRouter, Depends, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from app.services.streaming import RTZROpenAPIClient, FileStreamer, API_BASE
from app.services.audio_converter import any_to_wav
from app.settings import VITO_CLIENT_ID, VITO_CLIENT_SECRET

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/streaming",
    tags=["streaming"],
)

# 클라이언트 연결 관리자
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    """
    오디오 파일을 업로드하고 임시 저장합니다.
    """
    try:
        # 임시 파일로 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        contents = await file.read()
        temp_file.write(contents)
        temp_file.close()
        
        # 임시 파일 경로 반환
        return {"filename": temp_file.name}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    웹소켓 연결을 통해 음성 스트리밍을 처리합니다.
    """
    logger.info(f"새 웹소켓 연결 시도 - client_id: {client_id}")
    
    # WebSocket 연결 수락
    await websocket.accept()
    logger.info(f"웹소켓 연결됨 - client_id: {client_id}")
    
    # 테스트 모드
    if client_id == 'test':
        try:
            # 간단한 응답
            await websocket.send_text(json.dumps({"status": "connected", "message": "테스트 연결 성공"}))
            
            # 클라이언트 메시지 대기
            while True:
                try:
                    data = await websocket.receive_text()
                    logger.info(f"테스트 클라이언트로부터 메시지 수신: {data}")
                    
                    # 메시지 에코
                    await websocket.send_text(json.dumps({"status": "echo", "message": f"에코: {data}"}))
                except WebSocketDisconnect:
                    logger.info("테스트 웹소켓 연결 종료")
                    break
                except Exception as e:
                    logger.error(f"테스트 웹소켓 오류: {str(e)}")
                    await websocket.send_text(json.dumps({"error": str(e)}))
        except Exception as e:
            logger.error(f"테스트 웹소켓 처리 오류: {str(e)}")
        return
    
    # 파일 처리 모드
    temp_files = []  # 변환된 임시 파일 목록
    
    try:
        # 클라이언트로부터 파일 경로 받기
        logger.info("클라이언트로부터 메시지 대기 중")
        data = await websocket.receive_text()
        file_path = data
        logger.info(f"수신한 파일 경로: {file_path}")
        
        # 음성 인식 클라이언트 생성
        logger.info("RTZROpenAPIClient 생성 중")
        client = RTZROpenAPIClient(VITO_CLIENT_ID, VITO_CLIENT_SECRET)
        
        # WebSocket 응답 처리 함수
        async def handle_transcription(filename):
            try:
                # 파일이 존재하는지 확인
                if not os.path.exists(filename):
                    await websocket.send_text(
                        json.dumps({"error": f"파일을 찾을 수 없습니다: {filename}"})
                    )
                    return
                
                # 파일 변환 시도 (필요한 경우)
                try:
                    await websocket.send_text(
                        json.dumps({"status": "처리 중", "message": "오디오 파일 처리 중..."})
                    )
                    
                    # 오디오 파일을 WAV 포맷으로 변환 (필요한 경우)
                    wav_file_path = any_to_wav(filename)
                    if wav_file_path != filename:  # 변환된 경우에만 목록에 추가
                        temp_files.append(wav_file_path)
                        filename = wav_file_path  # 변환된 파일로 업데이트
                except Exception as e:
                    # 변환 오류가 발생해도 원본 파일로 계속 진행
                    await websocket.send_text(
                        json.dumps({"warning": f"오디오 변환 오류: {str(e)}, 원본 파일로 계속합니다."})
                    )
                
                # 스트리밍 설정
                config = {
                    "sample_rate": "8000",
                    "encoding": "LINEAR16",
                    "use_itn": "true",
                    "use_disfluency_filter": "false",
                    "use_profanity_filter": "false",
                }
                
                # 스트리밍 처리 진행 과정을 클라이언트에게 전송하는 래퍼 함수
                async def streaming_with_updates():
                    try:
                        # 외부 웹소켓 연결 설정
                        # 쿼리 매개변수를 올바른 형식으로 생성
                        query_params = "&".join([f"{k}={v}" for k, v in config.items()])
                        STREAMING_ENDPOINT = f"wss://{API_BASE.split('://')[1]}/v1/transcribe:streaming?{query_params}"
                        
                        conn_kwargs = {"extra_headers": {"Authorization": f"bearer {client.token}"}}
                        
                        async with websockets.connect(STREAMING_ENDPOINT, **conn_kwargs) as ext_ws:
                            # 파일 스트리밍 함수
                            with FileStreamer(filename) as f:
                                while True:
                                    buff = await f.read(DEFAULT_BUFFER_SIZE)
                                    if buff is None or len(buff) == 0:
                                        break
                                    await ext_ws.send(buff)
                                await ext_ws.send("EOS")
                            
                            # 음성 인식 결과 처리
                            async for msg in ext_ws:
                                result = json.loads(msg)
                                # 결과를 클라이언트에게 전송
                                await websocket.send_text(msg)
                                
                                if result.get("final"):
                                    final_text = result["alternatives"][0]["text"]
                                    await websocket.send_text(
                                        json.dumps({"status": "완료", "text": final_text})
                                    )
                    except Exception as e:
                        await websocket.send_text(
                            json.dumps({"error": str(e)})
                        )
                
                # 스트리밍 처리 시작
                await streaming_with_updates()
                
                # 임시 파일 삭제
                if os.path.exists(filename) and filename.startswith(tempfile.gettempdir()):
                    os.remove(filename)
                
            except Exception as e:
                await websocket.send_text(
                    json.dumps({"error": str(e)})
                )
        
        # 음성 인식 처리 시작
        await handle_transcription(file_path)
        
    except WebSocketDisconnect:
        logger.info("WebSocket 연결 종료")
    except Exception as e:
        logger.error(f"WebSocket 오류: {str(e)}")
        try:
            await websocket.send_text(
                json.dumps({"error": str(e)})
            )
        except:
            pass
    finally:
        # 변환된 임시 파일 삭제
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass 