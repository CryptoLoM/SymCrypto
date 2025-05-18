import math
from collections import Counter

alphabet_1 = "абвгдежзийклмнопрстуфхцчшщьыэюя"  # 'ь' - 'ы'
alphabet_2 = "абвгдежзийклмнопрстуфхцчшщыьэюя"  # 'ы' - 'ь'

common_rus_bigrams = ["ст", "но", "то", "на", "ен"]


with open("01.txt", "r", encoding="utf-8") as f:
    cipher_text = f.read().replace("\n", "").strip()


def bigram_frequencies(text):
    return Counter(text[i:i+2] for i in range(len(text) - 1))

top5_bigrams = [bg for bg, _ in bigram_frequencies(cipher_text).most_common(5)]


def get_index_map(alphabet):
    return {ch: idx for idx, ch in enumerate(alphabet)}


def mod_inverse(a, m):
    def egcd(x, y):
        if y == 0:
            return x, 1, 0
        g, x1, y1 = egcd(y, x % y)
        return g, y1, x1 - (x // y) * y1
    g, x, _ = egcd(a, m)
    return x % m if g == 1 else None


def decrypt(cipher_text, a, b, alphabet):
    m = len(alphabet)
    mod = m * m
    index_map = get_index_map(alphabet)
    a_inv = mod_inverse(a, mod)
    if a_inv is None:
        return None
    plaintext = []
    for i in range(0, len(cipher_text) - 1, 2):
        if cipher_text[i] not in index_map or cipher_text[i+1] not in index_map:
            continue
        Y = index_map[cipher_text[i]] * m + index_map[cipher_text[i+1]]
        X = (a_inv * (Y - b)) % mod
        first = X // m
        second = X % m
        if 0 <= first < m and 0 <= second < m:
            plaintext.append(alphabet[first] + alphabet[second])
    return ''.join(plaintext)


def entropy_H1(text):
    freq = Counter(text)
    total = sum(freq.values())
    return -sum((c / total) * math.log2(c / total) for c in freq.values()) 


results = []
for alphabet in [alphabet_1, alphabet_2]:
    m = len(alphabet)
    mod = m * m
    index_map = get_index_map(alphabet)
    for i in range(len(top5_bigrams)):
        for j in range(i + 1, len(top5_bigrams)):
            for pi in range(len(common_rus_bigrams)):
                for pj in range(pi + 1, len(common_rus_bigrams)):
                    try:
                        c1, c2 = top5_bigrams[i], top5_bigrams[j]
                        p1, p2 = common_rus_bigrams[pi], common_rus_bigrams[pj]
                        X1 = index_map[p1[0]] * m + index_map[p1[1]]
                        X2 = index_map[p2[0]] * m + index_map[p2[1]]
                        Y1 = index_map[c1[0]] * m + index_map[c1[1]]
                        Y2 = index_map[c2[0]] * m + index_map[c2[1]]
                        dx = (X1 - X2) % mod
                        dy = (Y1 - Y2) % mod
                        inv = mod_inverse(dx, mod)
                        if inv is None:
                            continue
                        a = (dy * inv) % mod
                        b = (Y1 - a * X1) % mod
                        decrypted = decrypt(cipher_text, a, b, alphabet)
                        if decrypted and len(decrypted) > 100:
                            H1 = entropy_H1(decrypted)
                            results.append((H1, decrypted, a, b, alphabet))
                    except Exception:
                        continue


results.sort()
best_H1, best_text, best_a, best_b, best_alphabet = results[0]
# print(f"kays:{len(results)}")
# print(results)
print(f"Найкращий результат:")
print(f"Ключ: a = {best_a}, b = {best_b}")
print(f"Ентропія: H1 = {best_H1:.4f}")
print(f"Порядок букв: {'ь після ы' if best_alphabet.index('ь') > best_alphabet.index('ы') else 'ь перед ы'}")
print(f"Перші 300 символів дешифрування:\n{best_text[:300]}")   
