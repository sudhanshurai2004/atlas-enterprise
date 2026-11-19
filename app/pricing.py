MODEL_INPUT_PER_1K = 0.000125
MODEL_OUTPUT_PER_1K = 0.000375


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    return round(
        (input_tokens / 1000 * MODEL_INPUT_PER_1K)
        + (output_tokens / 1000 * MODEL_OUTPUT_PER_1K),
        6,
    )
