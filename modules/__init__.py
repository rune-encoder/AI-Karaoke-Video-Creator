from .config import initialize_directories

from .audio_processing import (
    initialize_working_directory,
    extract_audio_metadata
)

from .stem_processing import (
    separate_audio_stems,
    merge_audio_stems
)

from .lyrics_processing import (
    transcribe_audio_lyrics,
    fetch_and_save_lyrics,
    perform_lyric_enhancement
)
