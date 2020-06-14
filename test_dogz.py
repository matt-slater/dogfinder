from dogfinder import dogz
import logging


class TestDogz:
    def test_get_doggie_diff(self):
        test_cases = [
            {
                "name": "more dogs,  none removed",
                "new": set(["1", "2", "3"]),
                "old": set(["1", "2"]),
                "expected": set(["3"]),
            },
            {
                "name": "more dogs,  one removed",
                "new": set(["1", "3"]),
                "old": set(["1", "2"]),
                "expected": set(["3"]),
            },
            {
                "name": "all new",
                "new": set(["3"]),
                "old": set([]),
                "expected": set(["3"]),
            },
            {
                "name": "remove only",
                "new": set(["3"]),
                "old": set(["1", "2", "3"]),
                "expected": set(),
            },
            {
                "name": "remove only",
                "new": set(["ozzy"]),
                "old": set(["ozzy", "snowball"]),
                "expected": set(),
            },
        ]
        log = logging.getLogger()
        for case in test_cases:
            actual = dogz.get_doggie_diff(case["new"], case["old"], log)
            assert actual == case["expected"], "failed test: " + case["name"] + ":::::: expected: " + str(case["expected"]) + " :::::: got: " + str(actual)
