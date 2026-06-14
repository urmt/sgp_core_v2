#!/usr/bin/env python3
"""
RD-HIST.2B — Create shuffled Q3 responses for C3 clustering.
"""

import random
import json

# The 20 Q3 responses with their study IDs
q3_responses = [
    {"id": 1, "study": "T038", "response": "Universes were generated with continuous dynamics and the emergence of separable clusters was measured."},
    {"id": 2, "study": "RD-10B.M5", "response": "Audits were classified by whether descriptions collapsed or were maintained, and gain was compared."},
    {"id": 3, "study": "T040", "response": "Ten candidates were tested and all required separation."},
    {"id": 4, "study": "RD-5", "response": "Removal fraction was varied and recovery metrics were measured."},
    {"id": 5, "study": "RD-10B.J2", "response": "Multiple sequences were generated and the same four features appeared in all of them."},
    {"id": 6, "study": "IF-3", "response": "A co-occurrence matrix was built, noise was filtered, and clustering was applied."},
    {"id": 7, "study": "RD-10B.J4", "response": "Each junction was removed and the effect on the others was measured."},
    {"id": 8, "study": "RD-10B.0", "response": "One world was represented in multiple ways and the same detectors were applied to each."},
    {"id": 9, "study": "T043", "response": "Universes were generated and detectors were applied to determine which appeared first."},
    {"id": 10, "study": "RD-10B.R1", "response": "The study sequence was re-read and the timing of gain relative to interaction was recorded."},
    {"id": 11, "study": "RD-10B.M6b", "response": "Comparisons were classified by type and collapse rates were measured."},
    {"id": 12, "study": "RD-019", "response": "Box width was varied and the effect on packing structure and outcome was measured."},
    {"id": 13, "study": "IF-ST", "response": "Reconstruction was tested under four degradation conditions and breakpoints were identified."},
    {"id": 14, "study": "RD-10B.J6", "response": "Each junction was expressed as an operator and composition was tested."},
    {"id": 15, "study": "RD-06", "response": "Pre-perturbation level was measured and its predictive power for recovery was tested."},
    {"id": 16, "study": "RD-10B.3", "response": "Worlds were generated without pattern vocabulary and patterns were detected after evolution."},
    {"id": 17, "study": "RD-10B.R0R", "response": "A classification scheme was applied to prior studies, separating them into two groups based on what remained stable."},
    {"id": 18, "study": "RD-10B.R3b", "response": "Audits were decomposed by type and the contribution of each component was analyzed."},
    {"id": 19, "study": "RD-05", "response": "Removal fraction was varied and recovery metrics were measured."},
    {"id": 20, "study": "T042", "response": "Universes were analyzed for proximity structure and the chain was tested."}
]

# Shuffle with a fixed seed for reproducibility
random.seed(42)  # Different from any previous seed
shuffled = q3_responses.copy()
random.shuffle(shuffled)

# Create the shuffled file
output = """# RD-HIST.2B — Shuffled Q3 Responses (for C3 clustering)

**Question:** What changed between the beginning and the end of the study?

**Rule 0:** One sentence only. No theoretical vocabulary. No invented objects. No abstractions beyond what the study operationally did.

---

## Shuffled Responses

"""

for i, item in enumerate(shuffled, 1):
    output += f'{i}. "{item["response"]}"\n\n'

output += """---

## Response Key

| # | Study | Original ID |
|---|-------|-------------|
"""

for i, item in enumerate(shuffled, 1):
    output += f'| {i} | {item["study"]} | {item["study"]} |\n'

output += """
---

**Note:** This file contains the same 20 Q3 responses as RD_HIST_2A_Q3_RAW.md, but in a different random order. This is used for C3 clustering to test order effects.
"""

# Write the file
with open('/home/student/sgp_core_v2/audits/RD_HIST_2B_Q3_SHUFFLED.md', 'w') as f:
    f.write(output)

# Also save the shuffled order as JSON for reference
shuffled_order = [{"position": i+1, "original_id": item["study"], "response": item["response"]} for i, item in enumerate(shuffled)]
with open('/home/student/sgp_core_v2/audits/RD_HIST_2B_SHUFFLED_ORDER.json', 'w') as f:
    json.dump({
        "seed": 42,
        "description": "Shuffled order of Q3 responses for C3 clustering",
        "responses": shuffled_order
    }, f, indent=2)

print(f"Created shuffled Q3 responses (seed=42)")
print(f"Original order: {[item['study'] for item in q3_responses]}")
print(f"Shuffled order: {[item['study'] for item in shuffled]}")
