def compute_checksum(data: bytes) -> int:
    if len(data) % 2 != 0:
        data = data + b'\x00'
    checksum = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        checksum += word
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    return ~checksum & 0xFFFF


def verify_checksum(data: bytes, checksum: int) -> bool:
    computed_checksum = compute_checksum(data)
    return computed_checksum == checksum


if __name__ == "__main__":
    data = b"hello world!"
    cs = compute_checksum(data)
    assert verify_checksum(data, cs), "Test 1 failed"
    print("Test 1 passed")

    data = b"hello"
    cs = compute_checksum(data)
    assert verify_checksum(data, cs), "Test 2 failed"
    print("Test 2 passed")

    data = b"hello world!"
    cs = compute_checksum(data)
    corrupted = bytes([data[0] ^ 0x01]) + data[1:]
    assert not verify_checksum(corrupted, cs), "Test 3 failed"
    print("Test 3 passed")