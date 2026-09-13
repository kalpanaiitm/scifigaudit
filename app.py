from io import BytesIO

import streamlit as st
from PIL import Image, UnidentifiedImageError

from scifigaudit.analysis import analyse_figure
from scifigaudit.report import report_json
from scifigaudit.sample import create_sample_figure
from scifigaudit.validation import validate_upload

st.set_page_config(page_title="SciFigAudit", page_icon="📊", layout="wide")
st.title("📊 SciFigAudit")
st.subheader("Privacy-conscious scientific-figure preflight checker")
st.info(
    "Free public demonstration. It screens technical and accessibility signals; "
    "it does not approve a figure, verify research integrity, or replace journal guidance."
)

if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0

with st.sidebar:
    st.header("Responsible use")
    st.markdown(
        "- Use published, fictional, or non-sensitive figures\n"
        "- Do not upload confidential or commercially sensitive research\n"
        "- Check the requirements of your chosen journal\n"
        "- A qualified person must inspect every result"
    )
    acknowledged = st.checkbox(
        "I understand these limitations",
        key=f"acknowledged_{st.session_state.upload_key}",
    )
    st.download_button(
        "Download fictional sample",
        data=create_sample_figure(),
        file_name="scifigaudit_fictional_sample.png",
        mime="image/png",
    )
    if st.button("Clear this session"):
        st.session_state.upload_key += 1
        st.rerun()

with st.expander("Privacy and assessment limitations", expanded=True):
    st.markdown(
        "- Image bytes are used only in the active app session; this app creates no upload directory or database.\n"
        "- Filenames and image contents are not intentionally logged. Hosting infrastructure may create operational metadata.\n"
        "- Automated checks are heuristic and may produce false positives or false negatives.\n"
        "- DPI metadata may be missing or misleading; pixel dimensions and final publication size also matter.\n"
        "- This version does not read axis text, detect fabrication, or assess scientific correctness."
    )

upload = st.file_uploader(
    "Upload one PNG, JPEG, or TIFF figure (maximum 10 MB)",
    type=["png", "jpg", "jpeg", "tif", "tiff"],
    key=f"figure_upload_{st.session_state.upload_key}",
)
caption = st.text_area(
    "Optional figure description or alt text",
    max_chars=1500,
    help="Add a short description so the report can include a human-review prompt.",
    key=f"description_{st.session_state.upload_key}",
)

if upload is not None:
    data = upload.getvalue()
    error = validate_upload(data, upload.type)
    if error:
        st.error(error)
    else:
        try:
            image = Image.open(BytesIO(data))
            image.load()
            st.image(image, caption="Uploaded figure preview", use_container_width=True)
            if st.button("Run figure audit", type="primary", disabled=not acknowledged):
                result = analyse_figure(image, caption)
                st.metric("Preflight score", f"{result.score}%")
                st.caption("A heuristic preparation score—not journal approval or a scientific-quality rating.")
                st.progress(result.score / 100)

                left, right = st.columns(2)
                with left:
                    st.subheader("Automated checks")
                    for check in result.checks:
                        icon = {"pass": "✅", "review": "⚠️", "info": "ℹ️"}[check.status]
                        with st.expander(f"{icon} {check.label}"):
                            st.write(check.message)
                            st.caption(check.evidence)
                with right:
                    st.subheader("Human-review checklist")
                    for item in result.human_review:
                        st.markdown(f"- {item}")

                st.warning(
                    "Pre-submission screen only. Consult the target journal and inspect the figure at its final size. "
                    "This is not a determination of accessibility, integrity, validity, or acceptance."
                )
                st.download_button(
                    "Download JSON audit report",
                    data=report_json(result),
                    file_name="scifigaudit_report.json",
                    mime="application/json",
                )
        except (UnidentifiedImageError, OSError, ValueError):
            st.error("The file could not be decoded safely as a supported image.")
else:
    st.caption("No figure has been uploaded. Download the fictional sample if you would like to test the app.")
