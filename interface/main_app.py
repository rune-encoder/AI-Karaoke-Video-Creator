# Standard Library Imports
import gradio as gr

# Local Application Imports
from .callbacks import (
    process_audio_callback,
    fetch_reference_lyrics_callback,
    save_fetched_lyrics_callback,
    modify_lyrics_callback,
    generate_subtitles_and_video_callback,
)

from .helpers import (
    check_modify_ai_availability,
    check_generate_karaoke_availability,
)

from modules import (
    get_available_colors,
    get_font_list,
)

import pandas as pd

# Main App Interface
def main_app(cache_dir, output_dir):
    with gr.Blocks() as app:

        # Get available fonts and colors for subtitles
        available_fonts = get_font_list()
        available_colors = get_available_colors()

        # ══════════════════════════════════════════════════════════════════════
        # -------------- State Management for the Application -------------------
        # ══════════════════════════════════════════════════════════════════════
        state_working_dir = gr.State(value="")
        state_lyrics_json = gr.State(value=None)
        state_lyrics_display = gr.State(value="")
        state_fetched_lyrics_json = gr.State(value=None)
        state_fetched_lyrics_display = gr.State(value="")

        gr.Markdown("# 🎤 Karaoke Generator")

        # ══════════════════════════════════════════════════════════════════════
        # -------------- Process Audio & and Transcribe Vocals -----------------
        # ══════════════════════════════════════════════════════════════════════
        gr.Markdown("# _____")
        with gr.Row():
            with gr.Column():
                audio_input = gr.File(
                    label="Upload Audio",
                    file_types=["audio"],
                    type="filepath"
                )

                # --- ADVANCED AUDIO SETTINGS ---
                with gr.Accordion("Advanced Audio Processing Settings", open=False):
                    force_audio_processing = gr.Checkbox(
                        label="Re-run Audio Processing?",
                        value=False,
                        info="Forces re-running the entire audio pipeline (stem separation, transcription, etc.)."
                    )

                process_audio_button = gr.Button(
                    "Process Audio",
                    variant="primary"
                )

        # ══════════════════════════════════════════════════════════════════════
        # ----------------- Fetch & Modify Reference Lyrics --------------------
        # ══════════════════════════════════════════════════════════════════════
        gr.Markdown("# _____")
        with gr.Row():
            with gr.Column():
                fetched_lyrics_box = gr.Textbox(
                    label="Reference Lyrics (Editable)",
                    lines=20,
                    interactive=True,
                )
                with gr.Row():
                    fetch_button = gr.Button("🌐 Fetch Reference Lyrics")
                    save_button = gr.Button("💾 Update Reference Lyrics")

            with gr.Column():
                raw_lyrics_box = gr.Dataframe(
                    value = pd.DataFrame({
                        "Processed Lyrics (Used for Karaoke)": ["" for _ in range(12)]
                    }),
                    headers=["Processed Lyrics (Used for Karaoke)"],
                    label="Processed Lyrics (Used for Karaoke)",
                    datatype=["str"],
                    interactive=False,
                    show_label=False,
                    max_height=465,
                )
                with gr.Row():
                    modify_button = gr.Button(
                        "🪄 Modify with AI",
                        variant="primary",
                        interactive=False
                    )

        with gr.Row():
            # --- ADVANCED LYRICS SETTINGS ---
            with gr.Accordion("Advanced Lyrics Settings", open=False):
                force_refetch_lyrics = gr.Checkbox(
                    label="Re-Fetch Reference Lyrics?",
                    value=False,
                    info="Ignores the local `reference_lyrics.json` and fetches new lyrics from the API."
                )
                force_ai_modification = gr.Checkbox(
                    label="Re-run AI Lyric Modification?",
                    value=False,
                    info="Ignores previously AI generated `modified_lyrics.json` and re-aligns the lyrics with AI."
                )

        # ══════════════════════════════════════════════════════════════════════
        # ----------------- Generate Karaoke Subtitles & Video -----------------
        # ══════════════════════════════════════════════════════════════════════
        gr.Markdown("# _____")
        gr.Markdown("## Generate Karaoke Subtitles & Video")

        with gr.Row():
            # --- Subtitles basic options ---
            font_input = gr.Dropdown(
                choices=available_fonts, 
                value="Maiandra GD", 
                label="Font"
            )
            primary_color_input = gr.Dropdown(
                choices=available_colors, 
                value="White", 
                label="Font Color"
            )
            secondary_color_input = gr.Dropdown(
                choices=available_colors, 
                value="Yellow", 
                label="Font Highlight Color"
            )
        with gr.Row():
            fontsize_input = gr.Slider(
                minimum=12, 
                maximum=84, 
                step=1, 
                value=38, 
                label="Font Size"
            )

        # --- ADVANCED VIDEO SETTINGS ---
        with gr.Accordion("Advanced Video Settings", open=False):
            gr.Markdown(
                "These options let you tweak video encoding quality, resolution, bitrate, etc.  "
                "Defaults are recommended for most users."
            )
            with gr.Row():
                force_subtitles_overwrite = gr.Checkbox(
                    label="Re-Generate Karaoke Subtitles?",
                    value=True,
                    info="If `karaoke_subtitles.ass` already exists, overwrite it with a newly generated file."
                )
            with gr.Row():
                with gr.Column():
                    resolution_input = gr.Dropdown(
                        choices=["640x480", "1280x720", "1920x1080"],
                        value="1280x720",
                        label="Resolution"
                    )
                    preset_input = gr.Dropdown(
                        choices=["ultrafast", "fast", "medium", "slow"],
                        value="fast",
                        label="FFmpeg Preset"
                    )
                with gr.Column():
                    crf_input = gr.Slider(
                        minimum=0, 
                        maximum=51, 
                        step=1, 
                        value=23, 
                        label="CRF (Video Quality)"
                    )
                    fps_input = gr.Slider(
                        minimum=15, 
                        maximum=60, 
                        step=1, 
                        value=24, 
                        label="Frames per Second"
                    )
                with gr.Column():
                    bitrate_input = gr.Dropdown(
                        label="Video Bitrate",
                        choices=["1000k", "2000k", "3000k", "4000k", "5000k", "Auto"],
                        value="3000k", 
                        interactive=True
                    )
                    audio_bitrate_input = gr.Dropdown(
                        label="Audio Bitrate",
                        choices=["64k", "128k", "192k", "256k", "320k", "Auto"],
                        value="192k", 
                        interactive=True
                    )

        generate_karaoke_button = gr.Button(
            "Generate Karaoke", 
            variant="primary",
            interactive=False
        )

        # We can display the final video in a gr.Video component
        karaoke_video_output = gr.Video(label="Karaoke Video", interactive=False)
        # karaoke_status_output = gr.Textbox(label="Karaoke Generation Status")

        # ══════════════════════════════════════════════════════════════════════
        # ----------------------- Wire up the callbacks -----------------------
        # ══════════════════════════════════════════════════════════════════════

        # (Primary) Process Audio Button
        # Updates States: working directory, lyrics data, and lyrics to display
        # Displays the updated `state_lyrics_display` in the `raw_lyrics_box`
        process_audio_button.click(
            # `.click()` event: Update the status of our states
            fn=process_audio_callback,
            inputs=[
                audio_input,
                force_audio_processing,
                state_working_dir,
                state_lyrics_json,
                state_lyrics_display,
                
                # Hidden state: cache_dir
                gr.State(cache_dir),  
            ],
            outputs=[
                state_working_dir,
                state_lyrics_json,
                state_lyrics_display
            ]
        ).then(
            # `.then()` event: After states are updated, display them in display box
            fn=lambda disp: disp,
            inputs=state_lyrics_display,
            outputs=raw_lyrics_box
        ).then(
            fn=check_modify_ai_availability,
            inputs=[state_working_dir],
            outputs=modify_button
        ).then(
            # After finishing `process_audio_callback`, check if we can enable `Modify with AI` and `Generate Karaoke` buttons
            fn=check_generate_karaoke_availability,
            inputs=[state_working_dir],
            outputs=generate_karaoke_button
        )

        # (Secondary) 🌐 Fetch Reference Lyrics Button
        # Updates States: fetched lyrics, fetched lyrics to display
        # Displays the updated `state_fetched_lyrics_display` in the `fetched_lyrics_box`
        fetch_button.click(
            fn=fetch_reference_lyrics_callback,
            inputs=[
                force_refetch_lyrics,
                state_working_dir,
                state_fetched_lyrics_json,
                state_fetched_lyrics_display
            ],
            outputs=[
                state_fetched_lyrics_json,
                state_fetched_lyrics_display
            ]
        ).then(
            fn=lambda disp: disp,
            inputs=state_fetched_lyrics_display,
            outputs=fetched_lyrics_box
        ).then(
            # After fetching the lyrics, check if we can enable `Modify with AI` button
            fn=check_modify_ai_availability,
            inputs=[state_working_dir],
            outputs=modify_button
        )

        # (Secondary) 💾 Update Reference Lyrics Button
        # Updates States: fetched lyrics, fetched lyrics to display
        # Displays the updated `state_fetched_lyrics_display` in the `fetched_lyrics_box`
        save_button.click(
            fn=save_fetched_lyrics_callback,
            inputs=[
                fetched_lyrics_box,
                state_working_dir,
                state_fetched_lyrics_json,
                state_fetched_lyrics_display
            ],
            outputs=[
                state_fetched_lyrics_json,
                state_fetched_lyrics_display
            ]
        ).then(
            # After updating the fetched lyrics, check if we can enable `Modify with AI` button
            fn=check_modify_ai_availability,
            inputs=[state_working_dir],
            outputs=modify_button
        )

        # (Secondary) 🪄 Modify with AI Button
        # Updates States: lyrics, lyrics to display
        # Displays the updated `state_lyrics_display` in the `lyrics_box`
        modify_button.click(
            fn=modify_lyrics_callback,
            inputs=[
                force_ai_modification,
                state_working_dir,
                state_lyrics_json,
                state_lyrics_display
            ],
            outputs=[
                state_lyrics_json,
                state_lyrics_display
            ]
        ).then(
            fn=lambda disp: disp,
            inputs=state_lyrics_display,
            outputs=raw_lyrics_box
        ).then(
            # After lyric modification, check if we can enable `Generate Karaoke` button
            fn=check_generate_karaoke_availability,
            inputs=[state_working_dir],
            outputs=generate_karaoke_button
        )

        # (Primary) Generate Karaoke Button
        # Generates the subtitles and karaoke video
        # Displays the generated video in the `karaoke_video_output`
        generate_karaoke_button.click(
            fn=generate_subtitles_and_video_callback,
            inputs=[
                state_working_dir,

                # Subtitles parameters
                font_input,
                fontsize_input,
                primary_color_input,
                secondary_color_input,

                # Video parameters
                resolution_input,
                preset_input,
                crf_input,
                fps_input,
                bitrate_input,
                audio_bitrate_input,

                # Additional or override flags
                force_subtitles_overwrite,

                # Hidden state: output_dir
                gr.State(output_dir) 
            ],
            outputs=[karaoke_video_output]  # or karaoke_status_output, or both
        )

    return app
