"""
-- version 2의 성능 개선 -- 
1. 반복문을 사용하는건 괜찮은데 한번 반복문이 돌때마다 1부터 계속 계산하는건 비효율적일 수 있음
2. 미리 계산한 결과를 저장해두고 사용하는 메모이제이션으로 중복 계산 피하기 
3. 문자열 + 연산 말고 리스트에 모았다가 join 해서 더 빠르게 생성하기
"""



def read_and_count(s: str) -> str:
    """입력 문자열을 읽고 개미 수열의 다음 항을 생성

    Args:
        s (str): 입력 문자열

    Returns:
        str: 다음 항의 문자열
    """
    next_parts: list[str] = []
    index: int = 0
            
    while index < len(s):
        count: int = 1
        
        # 연속된 같은 숫자 카운트
        while index + 1 < len(s) and s[index] == s[index + 1]:
            count += 1
            index += 1
        
        # 리스트에 추가 (문자열 연결 최적화)
        next_parts.append(f"{count}{s[index]}")
        index += 1
    
    # 한 번에 join으로 문자열 생성 (+=보다 효율적)
    return "".join(next_parts)


def look_and_say_iterative(n: int) -> str:
    """메모이제이션과 문자열 join 최적화를 적용한 개미 수열 생성

    Args:
        n (int): 생성할 항의 인덱스

    Returns:
        str: 생성된 수열
    """
    if n <= 3 or n >= 100:
        raise ValueError("n은 3보다 크고 100보다 작은 양의 정수여야 한다")
    
    # 메모이제이션을 위한 캐시 초기화
    cache: dict[int, str] = {1: "1"}
    
    # 캐시에 없는 항들을 순차적으로 계산
    for i in range(2, n + 1):
        if i not in cache:
            prev = cache[i-1]
            cache[i] = read_and_count(prev)
    
    return cache[n]

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


if __name__ == "__main__":
    start_value: int = int(input("숫자를 입력하세요: "))
    data = look_and_say_iterative(start_value)
    print(get_middle_two_digits(data))
