import streamlit as st
import os
from datetime import datetime

from audio_recorder_streamlit import audio_recorder

from audio_to_text import convert_audio_to_text
from text_to_audio import convert_text_to_audio, translate_text

from database import (
    create_user,
    login_user,
    save_conversion,
    get_conversions,
    update_conversion,
    get_dashboard_stats,
    get_conversion_chart_data,
    get_language_chart_data,
    delete_conversion,
    delete_all_conversions
)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Audio ↔ Text Converter",
    page_icon="🎙️",
    layout="centered"
)


# ==========================================
# SESSION STATE
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "upload_result" not in st.session_state:
    st.session_state.upload_result = None

if "recording_result" not in st.session_state:
    st.session_state.recording_result = None

if "tts_result" not in st.session_state:
    st.session_state.tts_result = None


# ==========================================
# LOGIN / SIGNUP
# ==========================================

if not st.session_state.logged_in:

    st.title("🎙️ Audio ↔ Text Converter")

    st.write(
        "Convert Audio to Text and Text to Audio."
    )

    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "👤 Signup"]
    )


    # ==========================================
    # LOGIN
    # ==========================================

    with login_tab:

        st.subheader("🔐 Login")

        login_email = st.text_input(
            "Email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "🔐 Login",
            key="login_button"
        ):

            if not login_email or not login_password:

                st.warning(
                    "Please enter email and password!"
                )

            else:

                user = login_user(
                    login_email,
                    login_password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.user = user

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password!"
                    )


    # ==========================================
    # SIGNUP
    # ==========================================

    with signup_tab:

        st.subheader("👤 Create Account")

        name = st.text_input(
            "Full Name",
            key="signup_name"
        )

        email = st.text_input(
            "Email",
            key="signup_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "👤 Create Account",
            key="signup_button"
        ):

            if not name.strip() or not email.strip() or not password:

                st.warning(
                    "Please fill all fields!"
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match!"
                )

            else:

                success, message = create_user(
                    name,
                    email,
                    password
                )

                if success:

                    st.success(message)

                    st.info(
                        "Please login with your account."
                    )

                else:

                    st.error(message)


# ==========================================
# MAIN APPLICATION
# ==========================================

else:

    user = st.session_state.user
    user_id = user["id"]


    # ==========================================
    # SIDEBAR
    # ==========================================

    st.sidebar.title("🎙️ Audio Converter")

    st.sidebar.write(
        f"👤 **{user['name']}**"
    )

    st.sidebar.write(
        f"📧 {user['email']}"
    )

    st.sidebar.divider()

    option = st.sidebar.radio(
        "Select Feature",
        [
            "📊 Dashboard",
            "🎙️ Audio to Text",
            "🔊 Text to Audio",
            "📜 Conversion History"
        ]
    )

    st.sidebar.divider()


    # ==========================================
    # LOGOUT
    # ==========================================

    if st.sidebar.button("🚪 Logout"):

        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.upload_result = None
        st.session_state.recording_result = None
        st.session_state.tts_result = None

        st.rerun()


    # ==========================================
    # DASHBOARD
    # ==========================================

    if option == "📊 Dashboard":

        st.title("📊 Dashboard")

        st.write(
            f"Welcome back, **{user['name']}**! 👋"
        )

        stats = get_dashboard_stats(user_id)

        col1, col2 = st.columns(2)

        col1.metric(
            "🔢 Total Conversions",
            stats["total"]
        )

        col2.metric(
            "🎙️ Audio → Text",
            stats["audio_to_text"]
        )

        col3, col4 = st.columns(2)

        col3.metric(
            "🔊 Text → Audio",
            stats["text_to_audio"]
        )

        col4.metric(
            "🌐 Most Used Language",
            stats["most_used_language"]
        )

        st.divider()

        st.subheader(
            "📊 Conversion Type Statistics"
        )

        conversion_data = get_conversion_chart_data(
            user_id
        )

        if conversion_data:

            chart_data = {
                item["conversion_type"]: item["total"]
                for item in conversion_data
            }

            st.bar_chart(chart_data)

        else:

            st.info("No conversion data available.")


        st.divider()

        st.subheader("🌐 Language Usage")

        language_data = get_language_chart_data(
            user_id
        )

        if language_data:

            chart_data = {
                item["language"]: item["total"]
                for item in language_data
            }

            st.bar_chart(chart_data)

        else:

            st.info("No language data available.")


    # ==========================================
    # AUDIO TO TEXT
    # ==========================================

    elif option == "🎙️ Audio to Text":

        st.title("🎙️ Audio to Text")

        input_method = st.radio(
            "Select Input Method",
            [
                "📁 Upload Audio",
                "🎤 Record Audio"
            ]
        )


        # ==========================================
        # UPLOAD AUDIO
        # ==========================================

        if input_method == "📁 Upload Audio":

            uploaded_file = st.file_uploader(
                "Upload an Audio File",
                type=["mp3", "wav", "m4a", "ogg"]
            )

            if uploaded_file is not None:

                st.audio(uploaded_file)

                if st.button("🎙️ Convert Uploaded Audio"):

                    os.makedirs(
                        "uploads",
                        exist_ok=True
                    )

                    timestamp = datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )

                    file_name = (
                        f"{timestamp}_{uploaded_file.name}"
                    )

                    file_path = os.path.join(
                        "uploads",
                        file_name
                    )

                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    with st.spinner(
                        "Converting audio to text..."
                    ):

                        text, language = convert_audio_to_text(
                            file_path
                        )

                    conversion_id = save_conversion(
                        user_id=user_id,
                        conversion_type="Audio to Text",
                        input_text=uploaded_file.name,
                        output_text=text,
                        language=language,
                        audio_file=file_path
                    )

                    st.session_state.upload_result = {
                        "conversion_id": conversion_id,
                        "text": text,
                        "language": language,
                        "timestamp": timestamp,
                        "file_path": file_path
                    }


            if st.session_state.upload_result:

                result = st.session_state.upload_result

                st.success("Audio converted successfully!")

                st.info(
                    f"Detected Language: {result['language']}"
                )

                edited_text = st.text_area(
                    "📝 Edit Transcribed Text",
                    value=result["text"],
                    height=250,
                    key=f"upload_{result['conversion_id']}"
                )

                if st.button(
                    "💾 Save Edited Text",
                    key=f"save_upload_{result['conversion_id']}"
                ):

                    update_conversion(
                        result["conversion_id"],
                        edited_text
                    )

                    st.session_state.upload_result[
                        "text"
                    ] = edited_text

                    st.success(
                        "Edited text saved successfully!"
                    )

                st.download_button(
                    "⬇️ Download Text",
                    edited_text,
                    file_name=f"transcription_{result['timestamp']}.txt"
                )


        # ==========================================
        # RECORD AUDIO
        # ==========================================

        else:

            st.write(
                "Click the microphone and start speaking."
            )

            audio_bytes = audio_recorder(
                text="",
                icon_name="microphone",
                icon_size="2x"
            )

            if audio_bytes:

                st.audio(
                    audio_bytes,
                    format="audio/wav"
                )

                if st.button("🎙️ Convert Recording"):

                    os.makedirs(
                        "uploads",
                        exist_ok=True
                    )

                    timestamp = datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )

                    file_path = os.path.join(
                        "uploads",
                        f"recording_{timestamp}.wav"
                    )

                    with open(file_path, "wb") as f:
                        f.write(audio_bytes)

                    with st.spinner(
                        "Converting speech to text..."
                    ):

                        text, language = convert_audio_to_text(
                            file_path
                        )

                    conversion_id = save_conversion(
                        user_id=user_id,
                        conversion_type="Audio to Text",
                        input_text="Microphone Recording",
                        output_text=text,
                        language=language,
                        audio_file=file_path
                    )

                    st.session_state.recording_result = {
                        "conversion_id": conversion_id,
                        "text": text,
                        "language": language,
                        "timestamp": timestamp,
                        "file_path": file_path
                    }


            if st.session_state.recording_result:

                result = st.session_state.recording_result

                st.success(
                    "Speech converted successfully!"
                )

                edited_text = st.text_area(
                    "📝 Edit Transcribed Text",
                    value=result["text"],
                    height=250,
                    key=f"record_{result['conversion_id']}"
                )

                if st.button(
                    "💾 Save Edited Text",
                    key=f"save_record_{result['conversion_id']}"
                ):

                    update_conversion(
                        result["conversion_id"],
                        edited_text
                    )

                    st.session_state.recording_result[
                        "text"
                    ] = edited_text

                    st.success(
                        "Edited text saved successfully!"
                    )

                st.download_button(
                    "⬇️ Download Text",
                    edited_text,
                    file_name=f"recording_{result['timestamp']}.txt"
                )


    # ==========================================
    # TEXT TO AUDIO
    # ==========================================

    elif option == "🔊 Text to Audio":

        st.title("🔊 Text to Audio")

        text = st.text_area(
            "Enter your text",
            height=200
        )

        language_options = {
            "English": "en",
            "Hindi": "hi",
            "Telugu": "te"
        }

        selected_language = st.selectbox(
            "Select Output Language",
            list(language_options.keys())
        )

        if st.button("🔊 Convert Text to Audio"):

            if text.strip():

                language_code = language_options[
                    selected_language
                ]

                with st.spinner(
                    "Generating audio..."
                ):

                    if language_code != "en":

                        translated_text = translate_text(
                            text,
                            language_code
                        )

                    else:

                        translated_text = text

                    audio_path = convert_text_to_audio(
                        translated_text,
                        language_code
                    )

                conversion_id = save_conversion(
                    user_id=user_id,
                    conversion_type="Text to Audio",
                    input_text=text,
                    output_text=translated_text,
                    language=language_code,
                    audio_file=audio_path
                )

                st.session_state.tts_result = {
                    "conversion_id": conversion_id,
                    "translated_text": translated_text,
                    "audio_path": audio_path
                }

            else:

                st.warning(
                    "Please enter some text!"
                )


        if st.session_state.tts_result:

            result = st.session_state.tts_result

            st.success(
                "Audio Generated Successfully!"
            )

            st.subheader("📝 Output Text")

            st.text_area(
                "Translated Text",
                value=result["translated_text"],
                height=200,
                disabled=True
            )

            if os.path.exists(result["audio_path"]):

                st.subheader("🔊 Generated Audio")

                st.audio(result["audio_path"])

                with open(
                    result["audio_path"],
                    "rb"
                ) as f:

                    st.download_button(
                        "⬇️ Download Audio",
                        f.read(),
                        file_name=os.path.basename(
                            result["audio_path"]
                        ),
                        mime="audio/mp3"
                    )


    # ==========================================
    # CONVERSION HISTORY
    # ==========================================

    elif option == "📜 Conversion History":

        st.title("📜 My Conversion History")

        conversions = get_conversions(user_id)


        # ==========================================
        # DELETE ALL
        # ==========================================

        if conversions:

            st.warning(
                "⚠️ This will permanently delete all "
                "your conversion history."
            )

            if st.button(
                "🗑️ Delete All My History",
                type="primary"
            ):

                success, audio_files = (
                    delete_all_conversions(user_id)
                )

                if success:

                    for file_path in audio_files:

                        try:

                            if (
                                file_path
                                and os.path.exists(file_path)
                            ):

                                os.remove(file_path)

                        except Exception as e:

                            print(
                                "File Delete Error:",
                                e
                            )

                    st.session_state.upload_result = None
                    st.session_state.recording_result = None
                    st.session_state.tts_result = None

                    st.success(
                        "All history and audio files "
                        "deleted successfully!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Unable to delete history."
                    )


        # ==========================================
        # DISPLAY HISTORY
        # ==========================================

        if conversions:

            for conversion in conversions:

                title = (
                    f"{conversion['conversion_type']} | "
                    f"{conversion['created_at']}"
                )

                with st.expander(title):

                    st.write(
                        f"**Language:** "
                        f"{conversion['language']}"
                    )

                    st.write("### 📥 Input")

                    st.write(
                        conversion["input_text"]
                    )

                    st.write("### 📤 Output")

                    st.write(
                        conversion["output_text"]
                    )


                    # AUDIO FILE
                    audio_file = conversion["audio_file"]

                    if (
                        audio_file
                        and os.path.exists(audio_file)
                        and conversion["conversion_type"]
                        == "Text to Audio"
                    ):

                        st.write(
                            "### 🔊 Generated Audio"
                        )

                        st.audio(audio_file)


                    # ==========================================
                    # DELETE SINGLE CONVERSION
                    # ==========================================

                    if st.button(
                        "🗑️ Delete This Conversion",
                        key=f"delete_{conversion['id']}"
                    ):

                        success, audio_file = (
                            delete_conversion(
                                conversion["id"],
                                user_id
                            )
                        )

                        if success:

                            try:

                                if (
                                    audio_file
                                    and os.path.exists(audio_file)
                                ):

                                    os.remove(audio_file)

                            except Exception as e:

                                print(
                                    "File Delete Error:",
                                    e
                                )

                            st.success(
                                "Conversion and related file "
                                "deleted successfully!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Unable to delete conversion."
                            )

        else:

            st.info(
                "You don't have any conversions yet."
            )