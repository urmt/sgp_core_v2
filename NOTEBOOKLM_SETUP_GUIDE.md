# NotebookLM Upload Guide for SFH-SGP Report

## Quick Start

1. Go to **notebooklm.google.com**
2. Create a new notebook
3. Upload `NOTEBOOKLM_SFH_SGP_REPORT.md` as a source
4. Click **Generate** in the Audio Overview section

## Recommended Settings for Best Results

### Format: Deep Dive
This creates a long-form conversation between two hosts — ideal for explaining complex research to a layperson.

### Custom Instructions (before generating):
```
Create a conversational 2-person discussion between a curious, questioning host and an explanatory host. 

Make it accessible for a general audience — avoid jargon where possible, and explain technical terms when they come up.

Structure:
1. Start with the puzzle/problem that motivated this research
2. Walk through each of the 5 key findings (F001-F005) in order
3. Explain what the findings mean for the bigger picture
4. Discuss the implications and what it means for the field
5. End with where this research goes next

Make the hosts sound like real people having a genuine conversation — ask follow-up questions, build on each other's points, and use natural speech patterns.
```

### Expertise Level
Set to "General" so hosts explain concepts clearly rather than assuming background knowledge.

---

## What NotebookLM Will Do

The two hosts will:
- Introduce the research as a "detective story" about why a system was failing
- Walk through each finding, explaining what was discovered and why it matters
- Use analogies to make concepts accessible (e.g., "it's like using a broken flashlight in an already-lit room")
- Build a narrative from problem → investigation → discovery → implications
- End with open questions about what comes next

The conversation typically runs 15-25 minutes for a document of this size.

---

## Tips

- After generation, you can ask NotebookLM follow-up questions about specific details
- You can download the audio for offline listening
- If the conversation misses something important, you can regenerate with different instructions
- Share the public link with anyone — they don't need a Google account

---

## Source Files

- `NOTEBOOKLM_SFH_SGP_REPORT.md` — Main report (this is what you upload)
- `STRICT_THEORY_FINAL/SFH_SGP_CANONICAL_THEORY.json` — Technical JSON (not needed for audio)