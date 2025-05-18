"""
-- version 1의 문제점 오류 -- 
1. 재귀를 사용하는건 직관적이여서 좋을꺼같은데 호출할때마다 이전항을 반복 계산하는게 비효율적일 수 있을꺼같음 
"""



def look_and_say_iterative(n: int) -> str:
    """문자열 읽어서 [개수][숫자] 변환

    Args:
        n (int): 생성할 항의 인덱스

    Returns:
        str: 생성할 수열 
    """
    if n <= 3 or n >= 100:
        raise ValueError("n은 3보다 크고 100보다 작은 양의 정수여야 한다")
    
    current: str = "1"
    for _ in range(1, n):
        next_term: str = ""
        index: int = 0 
        
        # 현재 항을 읽어서 다음 항을 생성
        while index < len(current):
            count: int = 1
            
            # 현재 항의 인덱스가 마지막 인덱스가 아니고 현재 인덱스와 다음 인덱스의 값이 같으면
            while index + 1 < len(current) and current[index] == current[index + 1]:
                count += 1
                index += 1

            next_term += str(count) + current[index]
            index += 1

        current = next_term
    return current

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
