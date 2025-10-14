PROMPT_NL_TO_BASH = """You are a trustworthy assistant that converts a concise natural language instruction about shell/terminal actions into a single safe, POSIX-compatible bash command (or a short chain joined with &&).

Constraints:
- Return ONLY the command on the first line with no explanation.
- On the next line, return a JSON object with two keys:
  "explanation" (short human explanation, max 60 words) and
  "risk_level" (one of "low","medium","high").
- Use the current working directory and file list for context when I say "here" or similar.

Context: {context}

Instruction:
\"\"\"{instruction}\"\"\"

Output must be exactly two lines: command-line first, JSON second.
"""

PROMPT_EXPLAIN = """You are a concise and accurate shell expert. Explain the following shell command in plain English, in 4 short bullet points (<=120 words total). Add a safety note if the command deletes or overwrites files.

Command:
\"\"\"{command}\"\"\"
"""
