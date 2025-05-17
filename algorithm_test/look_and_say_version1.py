"""
1 -> 1은 1개 -> 11
1은 2게 -> 21
21 > 2가 1개 1이 1게 -> 1211
1211 -> 1가 1개 2이 1개 1이 2개 -> 111221

[개수][숫자]
1 -> 혼자 -> 1개 = 11
2 -> 혼자 -> 1개 = 12
1 -> 두개 -> 2개 = 21


>>> 본 문제 <<<
양의 정수 n 이 주어질때 n번째 항 (Ln)의 자릿수 중 가운대 두 자리수 (m)을 구한다
(단 첫번째 항은 1이고 입력값 n은 3보다 크고 100보다 크다)

예) 입력 n=5, 출력 m=12,
    입력 n=8, 출력 m=21

>>> 문제 해석 <<<
n 이 5일 경우 -> 항별 생성 과정이 나온다는것이고 (L1 ~ L5)까지 생성은 한다면 다음과 같은 사고 과정을 거칠 수 있다
L1 -> 1 (초기값은 1이라는 고정으로 하여 진행)
L2 -> 1을 읽는다 -> 1이 1개 -> 11
L3 -> 11을 읽는다 -> 1개 2개 -> 21
L4 -> 21을 읽는다 -> [2가 1개, 1이 1개] -> 1211
L5 -> 11211을 읽는다 -> [
    1이 1개,
    2가 1개,
    1이 2개,
] -> 111221

그러면 총 인덱스는 다음과 같이 존재할 수 있다
index : 0, 1, 2, 3, 4, 5
value : 1, 1, 1, 2, 2, 1

>>> 제약 조건 <<<
1. 다음 값이 이전 값에 영향을 받음 (항이 하나라도 틀리면 값이 아예 달라지기 떄문에)

>>> 꼭 지켜야할 핵심 <<<
1. 초기값은 무조건 1
2. 수열 생성 조건이 연속된 값 세기
3. 결과 누적
4. 갱신
"""

start_value: int = int(input("숫자를 입력하세요: "))


def look_and_say(n: int) -> str:
    """재귀 수열 생성

    Args:
        n (int): 생성할 항의 인덱스

    Returns:
        str: 생성된 수열
    """
    if n == 1:
        return "1"

    prev: str = look_and_say(n - 1)
    return say(prev)


def say(s: str) -> str:
    """문자열 읽어서 [개수][숫자] 변환

    Args:
        s (str): 입력 문자열

    Returns:
        str: 변환된 문자열
    """
    result: str = ""
    index: int = 0
    while index < len(s):
        count: int = 1
        while index + 1 < len(s) and s[index] == s[index + 1]:
            count += 1
            index += 1
        result += str(count) + s[index]
        index += 1
    return result


def get_middle_two_digits(s: str) -> str:
    """문자열에서 가운데 두 자리를 반환합

    Args:
        s: 입력 문자열

    Returns:
        가운데 두 자리 문자열
    """
    string_length = len(s)
    if string_length < 2:
        return s

    # 중앙값을 구하기
    middle_index = string_length // 2
    return s[middle_index - 1 : middle_index + 1]


data = look_and_say(start_value)[:]
print(get_middle_two_digits(data))
