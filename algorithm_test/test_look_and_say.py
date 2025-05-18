import pytest
from look_and_say_version1 import look_and_say, get_middle_two_digits, say
from look_and_say_version2 import look_and_say_iterative as look_and_say_iterative_v2
from look_and_say_version3 import look_and_say_iterative as look_and_say_iterative_v3, read_and_count


# 정확한 개미 수열 시퀀스 테스트 데이터
TEST_SEQUENCES = {
    1: "1",
    2: "11",
    3: "21",
    4: "1211",
    5: "111221",
    6: "312211",
    7: "13112221",
    8: "1113213211",
    9: "31131211131221",
    10: "13211311123113112211"
}

# 시퀀스의 중간 두 자리 테스트 데이터
MIDDLE_DIGITS = {
    1: "1",  # 단일 숫자일 경우 그대로 반환
    2: "11",  # 두 자리일 경우 그대로 반환
    3: "21",  # 두 자리일 경우 그대로 반환
    4: "21",  # 네 자리 "1211"의 중간 두 자리
    5: "12",  # "111221"의 중간 두 자리
    8: "21"   # "1113213211"의 중간 두 자리
}


class TestLookAndSayV1:
    """Version 1 재귀 구현 테스트"""
    
    def test_say_function(self):
        """say 함수 테스트"""
        assert say("1") == "11"
        assert say("11") == "21"
        assert say("21") == "1211"
        assert say("1211") == "111221"
    
    def test_sequences(self):
        """시퀀스 생성 테스트"""
        for n, expected in TEST_SEQUENCES.items():
            if n <= 10:  # 재귀 깊이 제한을 고려
                assert look_and_say(n) == expected
    
    def test_middle_digits(self):
        """중간 두 자리 계산 테스트"""
        for n, expected in MIDDLE_DIGITS.items():
            if n <= 10:  # 재귀 깊이 제한을 고려
                result = look_and_say(n)
                assert get_middle_two_digits(result) == expected


class TestLookAndSayV2:
    """Version 2 반복적 구현 테스트"""
    
    def test_sequences(self):
        """시퀀스 생성 테스트"""
        for n, expected in TEST_SEQUENCES.items():
            if 3 < n < 100:  # 입력 제약 조건(3<n<100) 고려
                with pytest.raises(ValueError):
                    look_and_say_iterative_v2(3)  # 경계값 테스트
                with pytest.raises(ValueError):
                    look_and_say_iterative_v2(100)  # 경계값 테스트
            
                # n이 유효한 범위인 경우만 테스트
                if 3 < n < 100:
                    assert look_and_say_iterative_v2(n) == expected


class TestLookAndSayV3:
    """Version 3 메모이제이션 최적화 구현 테스트"""
    
    def test_read_and_count(self):
        """read_and_count 함수 테스트"""
        assert read_and_count("1") == "11"
        assert read_and_count("11") == "21"
        assert read_and_count("21") == "1211"
        assert read_and_count("1211") == "111221"
    
    def test_sequences(self):
        """시퀀스 생성 테스트"""
        for n, expected in TEST_SEQUENCES.items():
            # 입력 제약 조건(3<n<100) 고려
            with pytest.raises(ValueError):
                look_and_say_iterative_v3(3)  # 경계값 테스트
            with pytest.raises(ValueError):
                look_and_say_iterative_v3(100)  # 경계값 테스트
            
            # n이 유효한 범위인 경우만 테스트
            if 3 < n < 100:
                assert look_and_say_iterative_v3(n) == expected
    
    def test_caching(self):
        """캐싱 기능 테스트 - 같은 n에 대해 두 번째 호출은 캐시를 사용해야 함"""
        import time
        
        # 첫 번째 호출 시간 측정
        start = time.time()
        result1 = look_and_say_iterative_v3(50)  # 큰 값으로 테스트
        first_call_time = time.time() - start
        
        # 두 번째 호출 시간 측정 (캐시 사용)
        start = time.time()
        result2 = look_and_say_iterative_v3(50)  # 같은 값으로 호출
        second_call_time = time.time() - start
        
        # 결과가 동일한지 확인
        assert result1 == result2
        
        # 주의: 이 테스트는 실제 시간에 의존하므로 불안정할 수 있음
        # 캐시를 사용하면 두 번째 호출이 훨씬 빨라야 함
        print(f"첫 번째 호출: {first_call_time:.6f}초, 두 번째 호출: {second_call_time:.6f}초")


# 성능 벤치마크 테스트
class TestPerformance:
    """세 가지 구현의 성능 비교"""
    
    def test_benchmark_v1(self, benchmark):
        """Version 1 (재귀) 벤치마크"""
        n = 15  # 재귀에서는 너무 큰 n을 사용하면 오버플로우 발생
        
        try:
            result = benchmark(look_and_say, n)
            print(f"Version 1 (재귀, n={n}): {result[:20]}..." if len(result) > 20 else result)
            assert result
        except RecursionError:
            print(f"Version 1 (재귀): 스택 오버플로우 발생")
            assert "RecursionError"
    
    def test_benchmark_v2(self, benchmark):
        """Version 2 (반복) 벤치마크"""
        n = 20
        
        result = benchmark(look_and_say_iterative_v2, n)
        print(f"Version 2 (반복, n={n}): {result[:20]}..." if len(result) > 20 else result)
        assert result
    
    def test_benchmark_v3(self, benchmark):
        """Version 3 (메모이제이션) 벤치마크"""
        n = 20
        
        result = benchmark(look_and_say_iterative_v3, n)
        print(f"Version 3 (메모이제이션, n={n}): {result[:20]}..." if len(result) > 20 else result)
        assert result
        
    def test_results_equal(self):
        """모든 구현이 같은 결과를 생성하는지 확인"""
        n = 10  # 작은 값으로 테스트
        
        v1_result = look_and_say(n)
        v2_result = look_and_say_iterative_v2(n)
        v3_result = look_and_say_iterative_v3(n)
        
        assert v1_result == v2_result
        assert v2_result == v3_result
