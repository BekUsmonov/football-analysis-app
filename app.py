import streamlit as st
import os
import subprocess
import tempfile

st.set_page_config(page_title="Football Analysis", layout="centered")

st.title("⚽ Football Match Analysis")
st.write("Upload a football match video to analyze player movement, speed, and ball tracking.")

uploaded_file = st.file_uploader("🎥 Upload a video file", type=["mp4", "avi", "mov"])

if uploaded_file:
    # Create temp directories for input/output
    input_dir = "input_videos"
    output_dir = "output_videos"
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    input_path = os.path.join(input_dir, "uploaded_video.mp4")
    output_path = os.path.join(output_dir, "output_video.avi")

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ Video uploaded successfully!")

    if st.button("Run Analysis"):
        with st.spinner("⏳ Running analysis... this may take several minutes."):
            try:
                result = subprocess.run(
                    ["python", "main.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=600  # 10 minutes
                )

                if result.returncode == 0:
                    st.success("✅ Processing complete!")
                else:
                    st.error("❌ Script exited with errors.")
                    st.text(result.stderr)

            except subprocess.TimeoutExpired:
                st.error("⚠️ Analysis took too long and was stopped.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

        # Show console output
        st.subheader("Console Output")
        st.code(result.stdout)

        # Display output video if exists
        if os.path.exists(output_path):
            st.video(output_path)
        else:
            st.warning("⚠️ No output video found. Check the console logs above.")
