from __future__ import annotations

from pathlib import Path
import timeit


# =========================
# Read texts from /data
# =========================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"


def read_text(filename: str) -> str:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"❌ Файл не знайдено: {path}")
    return path.read_text(encoding="utf-8")


# =========================
# Substring search algorithms
# =========================
def boyer_moore_search(text: str, pattern: str) -> int:
    if pattern == "":
        return 0
    m = len(pattern)
    n = len(text)
    if m > n:
        return -1

    # bad character table
    last = {ch: i for i, ch in enumerate(pattern)}

    i = m - 1  # index in text
    j = m - 1  # index in pattern

    while i < n:
        if text[i] == pattern[j]:
            if j == 0:
                return i
            i -= 1
            j -= 1
        else:
            lo = last.get(text[i], -1)
            i += m - min(j, lo + 1)
            j = m - 1

    return -1


def kmp_search(text: str, pattern: str) -> int:
    if pattern == "":
        return 0
    m = len(pattern)
    n = len(text)
    if m > n:
        return -1

    # build LPS array (Longest Prefix Suffix)
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

    # search
    i = 0  # text index
    j = 0  # pattern index
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                return i - j
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return -1


def rabin_karp_search(text: str, pattern: str) -> int:
    if pattern == "":
        return 0
    m = len(pattern)
    n = len(text)
    if m > n:
        return -1

    base = 256
    mod = 1_000_000_007

    h = pow(base, m - 1, mod)
    p_hash = 0
    t_hash = 0

    for i in range(m):
        p_hash = (p_hash * base + ord(pattern[i])) % mod
        t_hash = (t_hash * base + ord(text[i])) % mod

    for i in range(n - m + 1):
        if p_hash == t_hash:
            # verify to avoid collisions
            if text[i : i + m] == pattern:
                return i

        if i < n - m:
            t_hash = (t_hash - ord(text[i]) * h) % mod
            t_hash = (t_hash * base + ord(text[i + m])) % mod
            t_hash %= mod

    return -1


# =========================
# Helpers for patterns + benchmarking
# =========================
def pick_existing_substring(text: str, min_len: int = 8, max_len: int = 20) -> str:
    """
    Вибирає підрядок, який ТОЧНО існує в тексті:
    беремо перше "слово" достатньої довжини.
    """
    # просте очищення для вибору слова
    chunks = []
    current = []
    for ch in text:
        if ch.isalnum() or ch in ("'", "’", "і", "ї", "є", "ґ"):
            current.append(ch)
        else:
            if current:
                chunks.append("".join(current))
                current = []
        if len(chunks) > 200:
            break
    if current:
        chunks.append("".join(current))

    for w in chunks:
        if len(w) >= min_len:
            return w[:max_len]

    # fallback: беремо будь-які 10 символів
    return text.strip()[:10]


def bench(func, text: str, pattern: str, repeat: int = 5, number: int = 1) -> float:
    """
    Повертає найкращий (мінімальний) час з repeat прогонів.
    number=1 — один пошук за прогін (логічно для великих текстів).
    """
    timer = timeit.Timer(lambda: func(text, pattern))
    return min(timer.repeat(repeat=repeat, number=number))


def format_table(rows):
    # rows: list[tuple[str, float, float, float]]
    header = "| Algorithm | Existing (s) | Missing (s) |"
    sep = "|----------|--------------:|------------:|"
    lines = [header, sep]
    for name, t_exist, t_miss in rows:
        lines.append(f"| {name:<9} | {t_exist:>12.6f} | {t_miss:>10.6f} |")
    return "\n".join(lines)


# =========================
# Main
# =========================
def main():
    text1 = read_text("article_1.txt")
    text2 = read_text("article_2.txt")

    # Якщо перевірити довжину текстів — ОСЬ ТУТ правильно робити print:
    print("LEN1:", len(text1))
    print("LEN2:", len(text2))
    print("-" * 60)

    algorithms = {
        "Boyer-Moore": boyer_moore_search,
        "KMP": kmp_search,
        "Rabin-Karp": rabin_karp_search,
    }

    missing_pattern = "___THIS_SUBSTRING_SHOULD_NOT_EXIST_123456___"

    overall_times = {name: [] for name in algorithms.keys()}

    for label, text in [("article_1", text1), ("article_2", text2)]:
        existing_pattern = pick_existing_substring(text)

        print(f"TEXT: {label}")
        print(f"Existing pattern: {existing_pattern!r}")
        print(f"Missing pattern : {missing_pattern!r}")

        rows = []
        for name, func in algorithms.items():
            t_exist = bench(func, text, existing_pattern)
            t_miss = bench(func, text, missing_pattern)
            rows.append((name, t_exist, t_miss))
            overall_times[name].extend([t_exist, t_miss])

        # print table
        print(format_table(rows))

        # best per text
        best_exist = min(rows, key=lambda x: x[1])[0]
        best_miss = min(rows, key=lambda x: x[2])[0]
        print(f"\nFastest for EXISTING in {label}: {best_exist}")
        print(f"Fastest for MISSING  in {label}: {best_miss}")
        print("=" * 60)

    # overall winner (average across all runs)
    avg = {name: sum(vals) / len(vals) for name, vals in overall_times.items()}
    overall_best = min(avg.items(), key=lambda x: x[1])[0]

    print("OVERALL (average across both texts and both patterns):")
    for name, v in sorted(avg.items(), key=lambda x: x[1]):
        print(f"- {name}: {v:.6f} s")
    print(f"\n🏁 Overall fastest: {overall_best}")


if __name__ == "__main__":
    main()

