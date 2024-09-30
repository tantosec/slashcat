from unittest.mock import Mock


MOCK_EXAMPLE_HASHES = {
    "0": {
        "name": "MD5",
        "category": "Raw Hash",
        "slow_hash": False,
        "password_len_min": 0,
        "password_len_max": 256,
        "is_salted": False,
        "kernel_type": ["pure", "optimized"],
        "example_hash_format": "plain",
        "example_hash": "8743b52063cd84097a65d1633f5c74f5",
        "example_pass": "hashcat",
        "benchmark_mask": "?b?b?b?b?b?b?b",
        "benchmark_charset1": "N/A",
        "autodetect_enabled": True,
        "self_test_enabled": True,
        "potfile_enabled": True,
        "custom_plugin": False,
        "plaintext_encoding": ["ASCII", "HEX"],
    },
    "10": {
        "name": "md5($pass.$salt)",
        "category": "Raw Hash salted and/or iterated",
        "slow_hash": False,
        "password_len_min": 0,
        "password_len_max": 256,
        "is_salted": True,
        "salt_type": "generic",
        "salt_len_min": 0,
        "salt_len_max": 256,
        "kernel_type": ["pure", "optimized"],
        "example_hash_format": "plain",
        "example_hash": "3d83c8e717ff0e7ecfe187f088d69954:343141",
        "example_pass": "hashcat",
        "benchmark_mask": "?b?b?b?b?b?b?b",
        "benchmark_charset1": "N/A",
        "autodetect_enabled": True,
        "self_test_enabled": True,
        "potfile_enabled": True,
        "custom_plugin": False,
        "plaintext_encoding": ["ASCII", "HEX"],
    },
    "11": {
        "name": "Joomla < 2.5.18",
        "category": "Forums, CMS, E-Commerce",
        "slow_hash": False,
        "password_len_min": 0,
        "password_len_max": 256,
        "is_salted": True,
        "salt_type": "generic",
        "salt_len_min": 0,
        "salt_len_max": 256,
        "kernel_type": ["pure", "optimized"],
        "example_hash_format": "plain",
        "example_hash": "b78f863f2c67410c41e617f724e22f34:89384528665349271307465505333378",
        "example_pass": "hashcat",
        "benchmark_mask": "?b?b?b?b?b?b?b",
        "benchmark_charset1": "N/A",
        "autodetect_enabled": True,
        "self_test_enabled": True,
        "potfile_enabled": True,
        "custom_plugin": False,
        "plaintext_encoding": ["ASCII", "HEX"],
    },
}


ALL_WORKER_METHODS = [
    "start_job",
    "status",
    "poll",
    "stop",
    "kill",
    "identify",
    "example_hashes",
    "list_wordlists",
    "list_rules",
    "list_maskfiles",
]


def create_request_worker_mock():
    mock_fns = {}
    for k in ALL_WORKER_METHODS:
        mock_fns[k] = Mock()
    mock_fns["example_hashes"].return_value = {
        "success": True,
        "example_hashes": MOCK_EXAMPLE_HASHES,
    }

    async def request_worker_fn(method_name, data):
        if method_name not in mock_fns:
            raise RuntimeError(
                f"Method {method_name} was called but is not specified in {__file__}"
            )
        return mock_fns[method_name](data)

    return mock_fns, request_worker_fn
