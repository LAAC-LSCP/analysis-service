"""
Generic entrypoint

TODO: get rid of this boilerplate
"""


def run_app() -> None:
    print(add_numbers(1, 2))

    return


def add_numbers(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    run_app()
