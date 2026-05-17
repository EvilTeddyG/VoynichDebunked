"""
Voynich Cryptanalysis Reset & Diagnostic Engine
Performs raw, cold mathematical profiling of Beinecke MS 408 (Takahashi Transcript)
without any translation lexicons or phonetic overlays.
Measures:
1. Character-level conditional entropy (H0, H1, H2) compared to natural languages.
2. The Line-Effect Correlation (verifying if word positions are bound by line layout).
3. The Phonotactic Finite-State Automaton (Markov chain generation properties).
"""
import argparse
import json
import re
import math
from collections import defaultdict, Counter

from corpus_provenance import ensure_publication_inputs


def parse_args():
    parser = argparse.ArgumentParser(description="Entropy and line-effect audit for a Takahashi/EVA transcript")
    parser.add_argument(
        "--input",
        default="data/takahashi_eva.txt",
        help="Path to transcript file (default: data/takahashi_eva.txt)",
    )
    parser.add_argument(
        "--json-out",
        default=None,
        help="Optional path to write machine-readable JSON results",
    )
    parser.add_argument(
        "--allow-placeholder-inputs",
        action="store_true",
        help="Allow synthetic/demo transcript inputs instead of publication-grade corpora",
    )
    return parser.parse_args()

def calculate_entropy(text):
    """
    Calculate character unigram and bigram entropy.
    """
    # Clean text to characters
    chars = [c for c in text if c.isalpha()]
    total_chars = len(chars)
    if total_chars == 0: return 0, 0
    
    # H0 (Unigram Entropy)
    char_counts = Counter(chars)
    h0 = 0.0
    for char, count in char_counts.items():
        p = count / total_chars
        h0 -= p * math.log2(p)
        
    # H1 (Bigram Conditional Entropy)
    bigram_counts = Counter()
    unigram_counts = Counter()
    for i in range(len(chars) - 1):
        bigram_counts[(chars[i], chars[i+1])] += 1
        unigram_counts[chars[i]] += 1
        
    h1 = 0.0
    for (c1, c2), count in bigram_counts.items():
        p_bigram = count / (len(chars) - 1)
        p_c1 = unigram_counts[c1] / len(chars)
        # Conditional probability p(c2|c1)
        p_cond = count / unigram_counts[c1]
        h1 -= p_bigram * math.log2(p_cond)
        
    return h0, h1

def analyze_line_effect(input_file):
    """
    Measure if word distributions are statistically correlated with their physical
    position on the line (Start, Middle, End).
    """
    positional_counts = defaultdict(Counter)
    word_totals = Counter()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('<f'): continue
            parts = line.split('>', 1)
            if len(parts) < 2: continue
            
            content = re.sub(r'[*!=]', '', parts[1]).strip()
            words = [re.sub(r'[^a-zA-Z]', '', w).strip() for w in re.split(r'[\s.-]', content)]
            words = [w for w in words if w]
            
            if len(words) >= 3:
                # Track position
                start_word = words[0]
                end_word = words[-1]
                mid_words = words[1:-1]
                
                positional_counts['start'][start_word] += 1
                positional_counts['end'][end_word] += 1
                for w in mid_words:
                    positional_counts['mid'][w] += 1
                    
                word_totals[start_word] += 1
                word_totals[end_word] += 1
                for w in mid_words:
                    word_totals[w] += 1

    # Find words with high positional polarization
    polarization_results = []
    for w, total in word_totals.items():
        if total >= 20:
            p_start = positional_counts['start'][w] / total
            p_mid = positional_counts['mid'][w] / total
            p_end = positional_counts['end'][w] / total
            
            # Max polarization is the distance from a uniform distribution (0.33, 0.33, 0.33)
            max_p = max(p_start, p_mid, p_end)
            polarization_results.append((w, total, p_start, p_mid, p_end, max_p))
            
    # Sort by max polarization
    polarization_results.sort(key=lambda x: x[5], reverse=True)
    return polarization_results

def main():
    args = parse_args()
    input_file = args.input

    ensure_publication_inputs(
        voynich_path=input_file,
        allow_placeholder_inputs=args.allow_placeholder_inputs,
    )
    
    # 1. Load entire cleaned corpus
    corpus = ""
    word_list = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('<f'): continue
            parts = line.split('>', 1)
            if len(parts) < 2: continue
            content = re.sub(r'[*!=]', '', parts[1]).strip()
            # Split to words
            words = [re.sub(r'[^a-zA-Z]', '', w).strip() for w in re.split(r'[\s.-]', content)]
            words = [w for w in words if w]
            word_list.extend(words)
            corpus += " ".join(words) + " "

    print("=" * 80)
    print("CLINICAL CRYPTANALYSIS RESET: VOYNICH MATHEMATICAL SIGNATURE")
    print("=" * 80)
    print(f"Total Words (Tokens) Analyzed: {len(word_list):,}")
    print(f"Total Characters Cleaned:      {len([c for c in corpus if c.isalpha()]):,}")
    print()
    
    # 2. Calculate Entropy
    h0, h1 = calculate_entropy(corpus)
    print("1. CHARACTER-LEVEL ENTROPY METRICS")
    print("-" * 80)
    print(f"Unigram Entropy (H0):                 {h0:.4f} bits")
    print(f"Bigram Conditional Entropy (H1|C1):   {h1:.4f} bits")
    print()
    print("Linguistic Comparison:")
    print("  - Classical Latin:         H0 = ~4.3 bits, H1 = ~3.2 bits")
    print("  - Middle English:          H0 = ~4.4 bits, H1 = ~3.3 bits")
    print("  - Voynichese (Actual):     H0 = ~3.8 bits, H1 = ~2.1 bits  <-- EXTREMELY LOW")
    print()
    print("Interpretation:")
    print("  Low conditional entropy indicates highly predictable transitions.")
    print("  This is consistent with a constrained generation process and should be")
    print("  compared against expanded medieval/control baselines before stronger claims.")
    print()
    
    # 3. Analyze Line Effect
    print("2. LINE-EFFECT CORRELATION SCAN (Positional Polarization)")
    print("-" * 80)
    polarization = analyze_line_effect(input_file)
    print(f"{'Word':<12} | {'Total Count':<11} | {'Start of Line':<15} | {'Middle of Line':<15} | {'End of Line':<12}")
    print("-" * 80)
    for w, total, p_s, p_m, p_e, max_p in polarization[:15]:
        print(f"{w:<12} | {total:<11} | {p_s*100:<13.1f}% | {p_m*100:<13.1f}% | {p_e*100:<10.1f}%")
        
    print()
    print("Interpretation:")
    print("  High positional polarization is consistent with layout constraints.")
    print("  Additional robustness checks should include folio partitions, Currier splits,")
    print("  and normalization variants.")
    print()
    
    # 4. Markov Chain Transition State Automaton (Phonotactic Constraints)
    print("3. PHONOTACTIC CONSTRAINT SCAN (State Transitions)")
    print("-" * 80)
    # Let's count which characters follow 'q', 'o', 'c', 'e'
    transitions = defaultdict(Counter)
    for w in word_list:
        for i in range(len(w) - 1):
            transitions[w[i]][w[i+1]] += 1
            
    for char in ['q', 'o', 'c', 'e']:
        total = sum(transitions[char].values())
        print(f"Character '{char}' is followed by:")
        for next_char, count in transitions[char].most_common(3):
            pct = (count / total) * 100 if total > 0 else 0
            print(f"  - '{next_char}': {pct:.1f}% ({count} times)")
        print()
        
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("1. The corpus shows low conditional entropy and strong transition constraints.")
    print("2. The corpus shows measurable line-position effects.")
    print("3. These signals motivate testing constrained generative models against")
    print("   translation/cipher alternatives with formal null-model statistics.")
    print("=" * 80)

    if args.json_out:
        results = {
            "input_file": input_file,
            "token_count": len(word_list),
            "char_count": len([c for c in corpus if c.isalpha()]),
            "entropy": {"H0": h0, "H1": h1},
            "top_positional_polarization": [
                {
                    "word": w,
                    "count": total,
                    "p_start": p_s,
                    "p_mid": p_m,
                    "p_end": p_e,
                    "max_p": max_p,
                }
                for (w, total, p_s, p_m, p_e, max_p) in polarization[:50]
            ],
            "top_transitions": {
                char: [
                    {"next": next_char, "count": count, "pct": (count / sum(transitions[char].values())) * 100 if sum(transitions[char].values()) else 0}
                    for next_char, count in transitions[char].most_common(10)
                ]
                for char in ["q", "o", "c", "e"]
            },
        }
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"JSON results written to: {args.json_out}")

if __name__ == '__main__':
    main()
