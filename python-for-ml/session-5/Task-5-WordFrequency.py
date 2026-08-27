from collections import Counter


def count_words(words):
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts


if __name__ == "__main__":
    data = ["Welcome", "Ali", "Hi", "Ali", "No", "Hi", "No", "Ali", "No", "Ali"]
    print(count_words(data))
    print(dict(Counter(data)))
