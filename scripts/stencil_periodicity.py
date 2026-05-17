"""
Voynich Stencil Periodicity & Spatial Alignment Audit
Mathematical search for physical template repetitions in Beinecke MS 408.
Analyzes:
1. Exact Block Duplications (repeating sequences of 3+ words and their offsets).
2. Vertical Character Alignment (measuring line-to-line vertical index correlations).
3. Spacing Autocorrelation (spikes in character distances pointing to a physical grille size).
"""
import argparse
import json
import re
from collections import defaultdict, Counter

from corpus_provenance import ensure_publication_inputs


def parse_args():
    parser = argparse.ArgumentParser(description="Spatial periodicity and alignment audit")
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

def analyze_block_duplications(words, min_len=3):
    """
    Find exact repeating multi-word phrases and count the distances (offsets) between them.
    """
    phrase_positions = defaultdict(list)
    
    # Extract all n-grams of min_len
    for i in range(len(words) - min_len + 1):
        phrase = tuple(words[i:i+min_len])
        phrase_positions[phrase].append(i)
        
    # Analyze distances for phrases that repeat
    distances = []
    highly_repeated = []
    
    for phrase, positions in phrase_positions.items():
        if len(positions) > 1:
            for j in range(len(positions) - 1):
                dist = positions[j+1] - positions[j]
                distances.append(dist)
            highly_repeated.append((phrase, len(positions), positions))
            
    # Sort highly repeated phrases
    highly_repeated.sort(key=lambda x: x[1], reverse=True)
    return highly_repeated, Counter(distances)

def analyze_vertical_alignment(input_file):
    """
    Measures vertical character alignment. If a Cardan Grille was slid down line-by-line,
    characters should align vertically at the same horizontal column index (with small shifts).
    """
    lines_chars = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('<f'): continue
            parts = line.split('>', 1)
            if len(parts) < 2: continue
            content = re.sub(r'[^a-zA-Z.]', '', parts[1].strip())  # keep periods as spacer indicators
            if len(content) > 10:
                lines_chars.append(content)
                
    # Measure column matches between adjacent lines
    column_matches = defaultdict(int)
    total_comparisons = 0
    
    for i in range(len(lines_chars) - 1):
        l1 = lines_chars[i]
        l2 = lines_chars[i+1]
        min_len = min(len(l1), len(l2))
        
        for j in range(min_len):
            if l1[j] == l2[j] and l1[j] != '.':
                column_matches[l1[j]] += 1
            total_comparisons += 1
            
    return Counter(column_matches), total_comparisons

def analyze_character_autocorrelation(corpus, max_lag=100):
    """
    Calculate the autocorrelation of character occurrences to search for periodic spikes.
    If a stencil had a fixed width of K characters, the same characters will repeat
    at intervals of K, 2K, 3K...
    """
    chars = [c for c in corpus if c.isalpha()]
    n = len(chars)
    if n == 0: return []
    
    # Calculate unigram mean probability
    char_counts = Counter(chars)
    char_probs = {c: count/n for c, count in char_counts.items()}
    
    autocorr = []
    for lag in range(1, max_lag + 1):
        matches = 0
        comparisons = 0
        for i in range(n - lag):
            if chars[i] == chars[i + lag]:
                matches += 1
            comparisons += 1
            
        p_match = matches / comparisons if comparisons > 0 else 0
        # Expected random match probability is sum(p_i^2)
        p_expected = sum(p**2 for p in char_probs.values())
        
        # Deviation (Autocorrelation score)
        score = p_match - p_expected
        autocorr.append((lag, score))
        
    # Sort by highest positive score deviation
    autocorr.sort(key=lambda x: x[1], reverse=True)
    return autocorr

def main():
    args = parse_args()

    ensure_publication_inputs(
        voynich_path=args.input,
        allow_placeholder_inputs=args.allow_placeholder_inputs,
    )
    input_file = args.input
    
    # Load and clean words
    word_list = []
    corpus = ""
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('<f'): continue
            parts = line.split('>', 1)
            if len(parts) < 2: continue
            content = re.sub(r'[*!=]', '', parts[1]).strip()
            words = [re.sub(r'[^a-zA-Z]', '', w).strip() for w in re.split(r'[\s.-]', content)]
            words = [w for w in words if w]
            word_list.extend(words)
            corpus += "".join(words)

    print("=" * 80)
    print("CLINICAL ANALYSIS: SPATIAL PERIODICITY & STENCIL REPETITION AUDIT")
    print("=" * 80)
    print(f"Total Words Scanned: {len(word_list):,}")
    print()
    
    # 1. Block Duplications
    print("1. MULTI-WORD PHRASE DUPLICATIONS (Exact Stencil Reuse)")
    print("-" * 80)
    repeated_phrases, dist_counts = analyze_block_duplications(word_list, min_len=3)
    
    print(f"Total Repeating 3-Word Phrases Found: {len(repeated_phrases)}")
    print()
    print("Top 5 Repeating Phrases and their word-index offsets:")
    for phrase, count, positions in repeated_phrases[:5]:
        phrase_str = " ".join(phrase)
        offsets = [positions[j+1] - positions[j] for j in range(len(positions)-1)]
        print(f"  - \"{phrase_str}\" (repeats {count} times) | Offsets: {offsets[:5]}")
    print()
    
    # Show most common physical spacing intervals
    print("Most common spacing intervals (word-distances) between duplicates:")
    for dist, freq in dist_counts.most_common(5):
        print(f"  - Distance of {dist:<4} words: {freq} times")
    print()
    
    # 2. Vertical Line-to-Line Alignment
    print("2. VERTICAL CHARACTER MATCHING ALONG PHYSICAL COLUMNS")
    print("-" * 80)
    matches, total_comp = analyze_vertical_alignment(input_file)
    total_matches = sum(matches.values())
    match_rate = (total_matches / total_comp) * 100 if total_comp > 0 else 0
    
    print(f"Total character column comparisons: {total_comp:,}")
    print(f"Total exact vertical column matches: {total_matches:,} ({match_rate:.2f}%)")
    print("Most frequent vertically aligned characters:")
    for char, count in matches.most_common(5):
        print(f"  - Column match of '{char}': {count} times")
    print()
    
    # 3. Autocorrelation Spikes (Grille Width Detection)
    print("3. CHARACTER AUTOCORRELATION SPIKES (Detecting Grid Width)")
    print("-" * 80)
    lags = analyze_character_autocorrelation(corpus, max_lag=60)
    print("Top 10 strongest periodic lags (character spacing offsets):")
    print("-" * 80)
    print(f"{'Rank':<5} | {'Lag (Char Offset)':<20} | {'Probability Deviation':<25}")
    print("-" * 80)
    for rank, (lag, score) in enumerate(lags[:10], 1):
        print(f"{rank:<5} | {lag:<20} | {score*100:<+24.4f}%")
        
    print()
    print("=" * 80)
    print("SPATIAL SUMMARY")
    print("=" * 80)
    
    # Find top lag spikes that point to a physical size
    top_lags = [lag for lag, score in lags[:5]]
    print(f"1. Strong periodic lags are detected at offsets: {top_lags}.")
    print("2. Repeating phrase distances and column matches are consistent with layout constraints.")
    print("3. Formal significance testing against shuffled/null controls is required")
    print("   before treating any single peak as a definitive physical dimension.")
    print("=" * 80)

    if args.json_out:
        results = {
            "input_file": input_file,
            "word_count": len(word_list),
            "top_repeated_phrases": [
                {
                    "phrase": list(phrase),
                    "count": count,
                    "positions": positions,
                }
                for phrase, count, positions in repeated_phrases[:100]
            ],
            "distance_histogram_top": [
                {"distance": dist, "frequency": freq}
                for dist, freq in dist_counts.most_common(50)
            ],
            "vertical_alignment": {
                "total_comparisons": total_comp,
                "total_matches": total_matches,
                "match_rate": match_rate,
                "top_chars": [
                    {"char": c, "count": n}
                    for c, n in matches.most_common(20)
                ],
            },
            "autocorrelation_top": [
                {"lag": lag, "score": score}
                for lag, score in lags[:60]
            ],
        }
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"JSON results written to: {args.json_out}")

if __name__ == '__main__':
    main()
