# Standard Library Imports
from typing import List, Optional
import os

# Third-Party Imports
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, RootModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMENI_MODEL = "gemini-1.5-flash"

# Prompt components
PREFIX = """
You are an AI tasked with aligning and correcting transcribed lyrics from a raw speech-to-text model by comparing them to the provided corrected lyrics.

The raw transcribed lyrics may contain:
- **Incorrect words**: Words that differ from the corrected lyrics.
- **Ghost words**: Words that do not exist in the corrected lyrics.
- **Split or merged words**: For example, "it's" instead of "it is" or "it is" instead of "it's."
- **Correct words**: Words that align perfectly with the corrected lyrics.

Important:
The raw transcribed lyrics come with highly accurate word-level timing data. Do not change the start and end times of each word unless you are merging or splitting words. 
In cases of merging, use the start time of the first word and the end time of the second word. Any isolated punctuation (such as a standalone ".") should be removed.

Each word in the raw transcription includes a **probability score** (ranging from 0.0 to 1.0) that indicates the model's confidence in the word's correctness:
- High scores (≥ 0.9) generally indicate the word is **correct**.
- Low scores (< 0.8) suggest the word may be **incorrect**, a **ghost word**, or misaligned.

Your primary goal is to align the raw transcribed lyrics with the corrected lyrics while adhering to the provided constraints and schema.
Use the **probability score** as a key factor in determining the correctness of words and whether to modify or remove them.
The task is critical for refining lyrics alignment for downstream applications such as karaoke timing, lyrical analysis, or music transcription. 
Your output must be highly accurate to ensure the data is usable for these purposes.
"""

EXPECTATION = """
Your task is to:
1. Correct the raw transcribed lyrics to match the provided corrected lyrics:
  - Replace **incorrect words** with their corrected counterparts.
  - Remove **ghost words** (words not present in the corrected lyrics) by leaving them as empty strings (`""`).
  - Handle **split or merged words** by including both words in the same string without modifying the start or end times. For example:
    - "it's" → "it is"
    - "cannot" → "can not"
    - "they are" → "they're"
  - Ensure that the **capitalization** and **punctuation** match the corrected lyrics exactly. Do not infer or add punctuation where it does not exist in the corrected lyrics.

2. **Timing Constraints**:
    - The **start** and **end** times for each word **must not overlap** with previous words.
    - The timing must be **incremental**: each word's start time must be greater than or equal to the previous word's end time.
  - Under no circumstances should a word have a start time or end time earlier than the most recently processed word, either within the chunk or across chunks.
    - If timing errors are detected, adjust them to maintain incremental order while preserving the original sequence as much as possible.

3. Adhere to the following constraints:
  - Use the **probability score** provided for each word to guide decisions:
    - Words with high probabilities (≥ 0.9) are likely correct.
    - Words with low probabilities (< 0.8) should be evaluated for correctness and potentially removed if they do not align with the corrected lyrics.
  - The sequence of words must match the corrected lyrics exactly, accounting for removed or modified words.
  - Ensure output is valid JSON and follows the provided schema.

3. **Timing Consistency Across Chunks**:
  - The start time of the first word in a chunk **must be greater than or equal to** the end time of the last word from the previous chunk.
  - You will be provided with the start and end timing boundaries for the current chunk. These boundaries must be respected:
    - Words within the chunk cannot have timings earlier than the chunk's start time or later than the chunk's end time.
    - Any adjustments to timing must maintain this boundary.

4. Adhere to the following constraints:
  - Use the **probability score** provided for each word to guide decisions:
    - Words with high probabilities (≥ 0.9) are likely correct.
    - Words with low probabilities (< 0.8) should be evaluated for correctness and potentially removed if they do not align with the corrected lyrics.
  - The sequence of words must match the corrected lyrics exactly, accounting for removed or modified words.
  - Ensure output is valid JSON and follows the provided schema.
"""


EDGE_CASES = """
1. If a ghost word is detected in the transcription (a word not present in the corrected lyrics), **remove it entirely** (do not replace it with an empty string).
2. If a word appears as just a punctuation mark (e.g., a standalone "."), remove it entirely.
3. In cases where a word should be merged with an adjacent word, output the merged word using the start time of the first word and the end time of the second word.
"""

# Define the WordAlignment schema
class WordAlignment(BaseModel):
    word: str = Field(..., description="The word from the lyrics.")
    start: float = Field(
        ...,
        description="The start time of the word in seconds. Do not modify. Must be a float."
    )
    end: float = Field(
        ...,
        description="The end time of the word in seconds. Do not modify. Must be a float."
    )
    verse_number: Optional[int] = Field(
        None, 
        description="The verse number in the lyrics. Do not modify. Must remain `None`."
    )

# Define a schema for a list of WordAlignment objects
class WordAlignmentList(RootModel):
    root: List[WordAlignment]


# Initialize the parser
PARSER = PydanticOutputParser(pydantic_object=WordAlignmentList)
