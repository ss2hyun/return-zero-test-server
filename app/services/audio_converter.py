import os
import subprocess
import tempfile
import uuid

def webm_to_wav(webm_file_path: str, sample_rate: int = 8000):
    """
    WebM 오디오 파일을 WAV 파일로 변환합니다.
    
    Args:
        webm_file_path: WebM 파일 경로
        sample_rate: 샘플 레이트 (기본값: 8000Hz)
        
    Returns:
        변환된 WAV 파일 경로
    """
    try:
        # 임시 WAV 파일 생성
        output_file = os.path.join(
            tempfile.gettempdir(),
            f"{uuid.uuid4()}_{sample_rate}.wav"
        )
        
        # FFmpeg 명령어를 사용하여 WebM 파일을 WAV로 변환
        command = [
            'ffmpeg',
            '-i', webm_file_path,
            '-ar', str(sample_rate),
            '-ac', '1',  # 단일 채널 (모노)
            '-f', 'wav',
            output_file
        ]
        
        # 명령어 실행
        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 오류: {e.stderr.decode() if e.stderr else str(e)}")
        raise Exception(f"오디오 변환 중 오류 발생: {str(e)}")
    except Exception as e:
        raise Exception(f"오디오 변환 중 오류 발생: {str(e)}")


def any_to_wav(input_file_path: str, sample_rate: int = 8000):
    """
    모든 오디오 파일을 WAV 파일로 변환합니다.
    
    Args:
        input_file_path: 입력 오디오 파일 경로
        sample_rate: 샘플 레이트 (기본값: 8000Hz)
        
    Returns:
        변환된 WAV 파일 경로
    """
    try:
        # 파일 확장자 확인
        file_ext = os.path.splitext(input_file_path)[1].lower()
        
        # 이미 WAV 파일인 경우 직접 반환
        if file_ext == '.wav':
            return input_file_path
            
        # 임시 WAV 파일 생성
        output_file = os.path.join(
            tempfile.gettempdir(),
            f"{uuid.uuid4()}_{sample_rate}.wav"
        )
        
        # FFmpeg 명령어를 사용하여 오디오 파일을 WAV로 변환
        command = [
            'ffmpeg',
            '-i', input_file_path,
            '-ar', str(sample_rate),
            '-ac', '1',  # 단일 채널 (모노)
            '-f', 'wav',
            output_file
        ]
        
        # 명령어 실행
        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 오류: {e.stderr.decode() if e.stderr else str(e)}")
        raise Exception(f"오디오 변환 중 오류 발생: {str(e)}")
    except Exception as e:
        raise Exception(f"오디오 변환 중 오류 발생: {str(e)}") 