#!/usr/bin/env python3
"""
SunoAPI.org 간단 사용 예제
==========================
가장 간단한 형태의 음악 생성 코드

API 키 발급: https://sunoapi.org/api-key
"""

import os
import requests
import time

# ===========================================
# 1. API 키 설정 (필수!)
# ===========================================
API_KEY = "82e425e2848ce562d55daeed482cc061"  # <-- 여기에 API 키 입력
# 또는 환경변수: export SUNO_API_KEY="your_api_key"
API_KEY = os.getenv("SUNO_API_KEY", API_KEY)

BASE_URL = "https://api.sunoapi.org/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 콜백 URL (필수!) - 실제 서버가 없으면 더미 URL 사용
# polling으로 상태 확인하므로 실제로 콜백을 받지 않아도 됨
CALLBACK_URL = "https://example.com/callback"


# ===========================================
# 2. 음악 생성 - 간단 모드
# ===========================================
def generate_simple():
    """설명으로 음악 생성 (Non-custom 모드)"""
    
    response = requests.post(
        f"{BASE_URL}/generate",
        headers=HEADERS,
        json={
            "customMode": False,
            "instrumental": False,
            "model": "V4_5ALL",
            "prompt": "‘홍길동 가실 분’이라는 노래를 만들어줘. 여기서 홍길동은 상봉동 먹자골목에 위치한 횟집이야. 대방어가 제철에 가장 빛나는, 줄 서서 먹는 동네 횟집이다. 영민이가 금요일 혹은 주말 저녁만 되면 JMS 멤버들에게 홍길동 가실 분을 찾아. 그러면 주로 오제원, 김진, 박찬준 등이 ‘저염~’이라고 대답해. 하지만 그건 98%의 확률도 거짓말이야. 그냥 영민이의 마음을 떠보려는 심산이지. 그러면 영민이는 결국 혼자 포장해와서 집에서 소주를 한잔 기울이면서 회를 먹게 돼. 영민은 그냥 평일에 지친 몸과 마음을 회 한점과 소주 한잔으로 떨칠 수 있는 친구를 찾고 있을 뿐인데, 그걸 매번 실현하지 못하게 되는 외로움과 고독함도 어느정도는 강조해줘.",
            "callBackUrl": CALLBACK_URL  # 필수!
        }
    )
    
    data = response.json()
    print(f"응답: {data}")
    
    if data["code"] == 200:
        return data["data"]["taskId"]
    else:
        raise Exception(f"오류: {data['msg']}")


# ===========================================
# 3. 음악 생성 - 가사 모드
# ===========================================
def generate_with_lyrics():
    """가사로 음악 생성 (Custom 모드)"""
    
    lyrics = """
[Verse 1]
どこかで鐘が鳴って
らしくない言葉が浮かんで 寒さが心地よくて
あれ なんで恋なんかしてんだろう

[Pre-Chorus]
聖夜だなんだと繰り返す歌と
わざとらしくきらめく街のせいかな

[Chorus]
会いたいと思う回数が
会えないと痛いこの胸が
君のことどう思うか教えようとしてる
いいよ そんなこと自分で分かってるよ
サンタとやらに頼んでも仕方ないよなぁ
できれば横にいて欲しくて
どこにも行っても欲しくなくて
僕のことだけをずっと考えていて欲しい
でもこんなこと伝えたら格好悪いし
長くなるだけだからまとめるよ
君が好きだ
"""
    
    response = requests.post(
        f"{BASE_URL}/generate",
        headers=HEADERS,
        json={
            "customMode": True,
            "instrumental": False,
            "model": "V4_5ALL",
            "prompt": lyrics,
            "style": """Okinawan Shima-uta / Ryukyu minyo style reinterpretation: sanshin-led folk arrangement with warm island atmosphere, moderate tempo with gentle bounce, light eisa/paranku percussion and hand claps, call-and-response singing with slightly nasal open tone, short instrumental breaks led by sanshin, natural live-session mix with minimal processing; avoid synths, modern drum kit, sidechain, glossy mastering, and autotune artifacts.""",
            "title": "Christmas Song okinawa style",
            "vocalGender": "m",
            "callBackUrl": CALLBACK_URL  # 필수!
        }
    )
    
    data = response.json()
    print(f"응답: {data}")
    
    if data["code"] == 200:
        return data["data"]["taskId"]
    else:
        raise Exception(f"오류: {data['msg']}")


# ===========================================
# 4. 작업 상태 확인
# ===========================================
def check_status(task_id):
    """작업 상태 조회"""
    
    response = requests.get(
        f"{BASE_URL}/generate/record-info",
        headers=HEADERS,
        params={"taskId": task_id}
    )
    
    return response.json()


# ===========================================
# 5. 완료까지 대기
# ===========================================
def wait_for_completion(task_id, timeout=300):
    """작업 완료 대기"""
    
    print(f"\n⏳ 음악 생성 대기 중... (Task ID: {task_id})")
    
    start = time.time()
    while time.time() - start < timeout:
        result = check_status(task_id)
        
        if result["code"] != 200:
            raise Exception(f"오류: {result['msg']}")
        
        status = result["data"]["status"]
        print(f"   상태: {status}")
        
        if status == "SUCCESS":
            return result["data"]["response"]["sunoData"]
        elif status in ["FAILED", "ERROR"]:
            raise Exception(f"생성 실패: {result['data'].get('errorMessage')}")
        
        time.sleep(10)
    
    raise TimeoutError("시간 초과")


# ===========================================
# 6. 다운로드
# ===========================================
def download_song(song, output_dir="./downloads"):
    """음악 파일 다운로드"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    audio_url = song.get("audioUrl")
    if not audio_url:
        print("아직 다운로드 URL이 없습니다")
        return None
    
    title = song.get("title", song["id"])
    filename = f"{title}_{song['id'][:8]}.mp3"
    filepath = os.path.join(output_dir, filename)
    
    print(f"📥 다운로드: {title}")
    
    response = requests.get(audio_url)
    with open(filepath, "wb") as f:
        f.write(response.content)
    
    print(f"   ✅ 저장: {filepath}")
    return filepath


# ===========================================
# 메인 실행
# ===========================================
if __name__ == "__main__":
    # 간단 모드로 생성
    # task_id = generate_simple()
    
    # 또는 가사 모드로 생성
    task_id = generate_with_lyrics()
    
    # 완료 대기
    songs = wait_for_completion(task_id)
    
    # 결과 출력 및 다운로드
    print(f"\n🎵 생성된 곡: {len(songs)}개")
    for song in songs:
        print(f"\n  제목: {song['title']}")
        print(f"  태그: {song['tags']}")
        print(f"  길이: {song['duration']}초")
        print(f"  URL: {song['audioUrl']}")
        
        # 다운로드
        download_song(song)
    
    print("\n✅ 완료!")