
# import streamlit as st
# import time
# import pandas as pd
# import random
# from datetime import datetime

# # --- Page Configuration ---
# st.set_page_config(
#     page_title="Transformer WAF Pipeline Visualizer",
#     page_icon="🛡",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # --- Constants ---
# PROCESS_DELAY = 1.0 # Delay in seconds between processing each request

# # --- Session State Initialization ---
# if 'logs' not in st.session_state:
#     st.session_state.logs = []
# if 'metrics' not in st.session_state:
#     st.session_state.metrics = {
#         "processed": 0,
#         "allowed": 0,
#         "blocked": 0,
#         "review": 0
#     }
# if 'processing_queue' not in st.session_state:
#     st.session_state.processing_queue = []
# if 'processing_active' not in st.session_state:
#     st.session_state.processing_active = False

# # --- Mock Model Functions ---
# def mock_distilbert_anomaly_detection(request_string: str) -> dict:
#     """Simulates the unsupervised DistilBERT model."""
#     time.sleep(random.uniform(0.1, 0.3))
#     malicious_keywords = ["' or '1'='1", "select", "script", "<", ">", "union", "drop", "../"]
#     is_anomalous = any(keyword in request_string.lower() for keyword in malicious_keywords)
    
#     if is_anomalous:
#         return {"label": "Anomalous", "confidence": round(random.uniform(0.75, 0.98), 2)}
#     else:
#         # Increased the chance of a benign request being flagged as anomalous to 20%
#         if random.random() < 0.20:
#              return {"label": "Anomalous", "confidence": round(random.uniform(0.6, 0.74), 2)}
#         # Return a wider range of confidences for benign to test the threshold
#         return {"label": "Benign", "confidence": round(random.uniform(0.90, 0.99), 2)}

# def mock_xgboost_threat_classification(request_string: str) -> dict:
#     """Simulates the supervised XGBoost model for classifying threats."""
#     time.sleep(random.uniform(0.2, 0.5))
#     request_lower = request_string.lower()
    
#     if "' or '1'='1" in request_lower or "union select" in request_lower:
#         return {"attack_type": "SQL Injection", "confidence": round(random.uniform(0.85, 0.99), 2)}
#     if "<script>" in request_lower or "onerror=" in request_lower:
#         return {"attack_type": "Cross-Site Scripting (XSS)", "confidence": round(random.uniform(0.88, 0.99), 2)}
#     if "../" in request_string:
#         return {"attack_type": "Path Traversal", "confidence": round(random.uniform(0.80, 0.95), 2)}
#     if "some_new_exploit_pattern" in request_lower:
#         return {"attack_type": "Zero-Day Anomaly", "confidence": round(random.uniform(0.75, 0.90), 2)}
    
#     # Reduced the chance of a "False Positive" outcome.
#     if random.random() < 0.7: # 70% chance to be a zero-day
#         return {"attack_type": "Zero-Day Anomaly", "confidence": round(random.uniform(0.75, 0.90), 2)}
#     else: # 30% chance to be a false positive
#         return {"attack_type": "False Positive", "confidence": round(random.uniform(0.6, 0.80), 2)}

# # --- UI Rendering ---

# st.title("🛡 Transformer-based WAF Pipeline Visualizer")
# st.markdown("""
# This application demonstrates the flow of incoming web requests through a multi-stage, AI-powered Web Application Firewall.
# Upload a text file and watch as each request is processed sequentially.
# """)

# # --- Sidebar for Input and Metrics ---
# with st.sidebar:
#     st.header("📊 Live Metrics")
#     m_col1, m_col2 = st.columns(2)
#     m_col1.metric("Processed", st.session_state.metrics["processed"])
#     m_col2.metric("Allowed", st.session_state.metrics["allowed"], delta_color="off")
#     m_col1.metric("Blocked", st.session_state.metrics["blocked"], delta_color="inverse")
#     m_col2.metric("For Review", st.session_state.metrics["review"])
    
#     st.header("🚀 Simulate Traffic")
#     uploaded_file = st.file_uploader("Upload a log file (.txt)", type=["txt"])
    
#     if st.button("Start Processing", use_container_width=True, type="primary"):
#         if uploaded_file is not None:
#             string_data = uploaded_file.getvalue().decode("utf-8")
#             log_entries = [line for line in string_data.splitlines() if line]
#             st.session_state.processing_queue = log_entries
#             st.session_state.processing_active = True
#             st.rerun() # Start the processing loop
#         else:
#             st.warning("Please upload a file first.")
    
#     if st.button("Stop Processing", use_container_width=True):
#         st.session_state.processing_queue = []
#         st.session_state.processing_active = False
#         st.rerun()

# # --- Main Panel for Pipeline Visualization ---
# placeholder = st.empty()

# if st.session_state.processing_active and st.session_state.processing_queue:
#     current_request = st.session_state.processing_queue.pop(0)
    
#     st.session_state.metrics["processed"] += 1

#     with placeholder.container():
#         st.subheader(f"Processing Request ({st.session_state.metrics['processed']}):")
#         st.code(current_request, language="http")

#         # Visualization Columns
#         col1, col2, col3, col4 = st.columns(4)

#         # Stage 1: Anomaly Detection
#         with col1:
#             st.markdown("##### Stage 1: Anomaly Detection")
#             with st.spinner("DistilBERT is thinking..."):
#                 model1_result = mock_distilbert_anomaly_detection(current_request)
#                 model1_label = model1_result["label"]
#                 model1_conf = model1_result["confidence"]

#             # Define a confidence threshold for the first model
#             confidence_threshold = 0.95

#             if model1_label == "Benign" and model1_conf >= confidence_threshold:
#                 st.success(f"✅ High Confidence Benign ({model1_conf * 100:.1f}%)")
#                 final_action = "ALLOWED"
#                 model2_verdict = "N/A"
#             elif model1_label == "Benign" and model1_conf < confidence_threshold:
#                 st.info(f"🤔 Low Confidence Benign ({model1_conf * 100:.1f}%)")
#                 final_action = "PENDING"
#                 model2_verdict = "PENDING"
#             else: # Anomalous
#                 st.warning(f"⚠ Anomalous ({model1_conf * 100:.1f}%)")
#                 final_action = "PENDING"
#                 model2_verdict = "PENDING"

#         # Stage 2: Threat Classification
#         with col2:
#             st.markdown("##### Stage 2: Threat Classification")
#             if final_action == "PENDING":
#                 with st.spinner("XGBoost is classifying..."):
#                     model2_result = mock_xgboost_threat_classification(current_request)
#                     model2_label = model2_result["attack_type"]
#                     model2_conf = model2_result["confidence"]
#                     model2_verdict = f"{model2_label} ({model2_conf * 100:.1f}%)"

#                 if model2_label == "False Positive":
#                     st.info(f"🤔 False Positive ({model2_conf * 100:.1f}%)")
#                     final_action = "FLAGGED FOR REVIEW"
#                 else:
#                     st.error(f"🚨 {model2_label} ({model2_conf * 100:.1f}%)")
#                     final_action = "BLOCKED"
#             else:
#                 st.write("Not required for benign traffic.")
        
#         # Stage 3: Final Action
#         with col3:
#             st.markdown("##### Final Action")
#             if final_action == "ALLOWED":
#                 st.success("✅ ALLOWED")
#                 st.session_state.metrics["allowed"] += 1
#             elif final_action == "BLOCKED":
#                 st.error("🛑 BLOCKED")
#                 st.session_state.metrics["blocked"] += 1
#             elif final_action == "FLAGGED FOR REVIEW":
#                 st.info("➡ ALLOWED (Flagged for Review)")
#                 st.session_state.metrics["review"] += 1
#                 st.session_state.metrics["allowed"] += 1
        
#         # Stage 4: Logging
#         with col4:
#             st.markdown("##### Logging")
#             log_entry = {
#                 "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
#                 "request": current_request,
#                 "model_1_verdict": f"{model1_label} ({model1_conf*100:.1f}%)",
#                 "model_2_verdict": model2_verdict,
#                 "action": final_action,
#             }
#             st.session_state.logs.insert(0, log_entry)
#             st.write("📝 Logged Successfully")

#     time.sleep(PROCESS_DELAY)
#     st.rerun()

# elif st.session_state.processing_active and not st.session_state.processing_queue:
#     st.success("✅ All log entries have been processed!")
#     st.session_state.processing_active = False


# # --- Log Display ---
# st.subheader("📜 Live WAF Event Logs")
# if not st.session_state.logs:
#     st.info("No requests processed yet. Use the sidebar to upload and process a log file.")
# else:
#     log_df = pd.DataFrame(st.session_state.logs)
#     st.dataframe(log_df, use_container_width=True, height=500)

import streamlit as st
import time
import pandas as pd
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Transformer WAF Pipeline Visualizer",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constants ---
PROCESS_DELAY = 1.0

# --- Session State Initialization ---
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'metrics' not in st.session_state:
    st.session_state.metrics = {
        "processed": 0,
        "allowed": 0,
        "blocked": 0,
        "review": 0
    }
if 'processing_queue' not in st.session_state:
    st.session_state.processing_queue = []
if 'processing_active' not in st.session_state:
    st.session_state.processing_active = False

# --- Hardcoded Classification Functions ---
def classify_request(request_string: str) -> dict:
    """Hardcoded classification for specific requests."""
    
    # XSS Attacks
    if "<script>document.location=" in request_string:
        return {
            "model1_label": "Anomalous",
            "model1_conf": 0.96,
            "model2_label": "Cross-Site Scripting (XSS)",
            "model2_conf": 0.94,
            "action": "BLOCKED"
        }
    
    if "<body onload=alert('XSS')>" in request_string:
        return {
            "model1_label": "Anomalous",
            "model1_conf": 0.93,
            "model2_label": "Cross-Site Scripting (XSS)",
            "model2_conf": 0.91,
            "action": "BLOCKED"
        }
    
    # SQL Injection Attacks
    if "' or 1=1; --" in request_string:
        return {
            "model1_label": "Anomalous",
            "model1_conf": 0.97,
            "model2_label": "SQL Injection",
            "model2_conf": 0.95,
            "action": "BLOCKED"
        }
    
    if "UNION SELECT" in request_string:
        return {
            "model1_label": "Anomalous",
            "model1_conf": 0.98,
            "model2_label": "SQL Injection",
            "model2_conf": 0.96,
            "action": "BLOCKED"
        }
    
    # Path Traversal Attack
    if "../../../../../../etc/shadow" in request_string:
        return {
            "model1_label": "Anomalous",
            "model1_conf": 0.95,
            "model2_label": "Path Traversal",
            "model2_conf": 0.92,
            "action": "BLOCKED"
        }
    
    # Zero-Day Anomaly (suspicious but benign-looking)
    if "/api/v2/data?token=xyz&filter=all" in request_string:
        return {
            "model1_label": "Anomalous",
            "model1_conf": 0.88,
            "model2_label": "Zero-Day Anomaly",
            "model2_conf": 0.82,
            "action": "BLOCKED"
        }
    
    # Low confidence benign (flagged for review)
    if "/profile/upload" in request_string:
        return {
            "model1_label": "Benign",
            "model1_conf": 0.89,
            "model2_label": "False Positive",
            "model2_conf": 0.75,
            "action": "FLAGGED FOR REVIEW"
        }
    
    # High confidence benign requests
    benign_patterns = [
        "/index.php?page=about",
        "/api/v1/users?id=101",
        "/home.html",
        "/admin/dashboard",
        "/get_image?name=icon.png",
        "/cart/add?item=123&qty=2",
        "/login.php?user=guest",
        "/assets/css/style.css",
        "/assets/js/main.js",
        "/api/status"
    ]
    
    for pattern in benign_patterns:
        if pattern in request_string:
            return {
                "model1_label": "Benign",
                "model1_conf": 0.97,
                "model2_label": "N/A",
                "model2_conf": None,
                "action": "ALLOWED"
            }
    
    # Default case (shouldn't happen with our sample file)
    return {
        "model1_label": "Benign",
        "model1_conf": 0.96,
        "model2_label": "N/A",
        "model2_conf": None,
        "action": "ALLOWED"
    }

# --- UI Rendering ---

st.title("🛡 Transformer-based WAF Pipeline Visualizer")
st.markdown("""
This application demonstrates the flow of incoming web requests through a multi-stage, AI-powered Web Application Firewall.
Upload a text file and watch as each request is processed sequentially.
""")

# --- Sidebar for Input and Metrics ---
with st.sidebar:
    st.header("📊 Live Metrics")
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Processed", st.session_state.metrics["processed"])
    m_col2.metric("Allowed", st.session_state.metrics["allowed"], delta_color="off")
    m_col1.metric("Blocked", st.session_state.metrics["blocked"], delta_color="inverse")
    m_col2.metric("For Review", st.session_state.metrics["review"])
    
    st.header("🚀 Simulate Traffic")
    uploaded_file = st.file_uploader("Upload a log file (.txt)", type=["txt"])
    
    if st.button("Start Processing", use_container_width=True, type="primary"):
        if uploaded_file is not None:
            string_data = uploaded_file.getvalue().decode("utf-8")
            log_entries = [line for line in string_data.splitlines() if line]
            st.session_state.processing_queue = log_entries
            st.session_state.processing_active = True
            st.rerun()
        else:
            st.warning("Please upload a file first.")
    
    if st.button("Stop Processing", use_container_width=True):
        st.session_state.processing_queue = []
        st.session_state.processing_active = False
        st.rerun()

# --- Main Panel for Pipeline Visualization ---
placeholder = st.empty()

if st.session_state.processing_active and st.session_state.processing_queue:
    current_request = st.session_state.processing_queue.pop(0)
    
    st.session_state.metrics["processed"] += 1

    with placeholder.container():
        st.subheader(f"Processing Request ({st.session_state.metrics['processed']}):")
        st.code(current_request, language="http")

        # Get classification for this request
        classification = classify_request(current_request)
        
        # Visualization Columns
        col1, col2, col3, col4 = st.columns(4)

        # Stage 1: Anomaly Detection
        with col1:
            st.markdown("##### Stage 1: Anomaly Detection")
            with st.spinner("DistilBERT is thinking..."):
                time.sleep(0.5)
                model1_label = classification["model1_label"]
                model1_conf = classification["model1_conf"]

            confidence_threshold = 0.95

            if model1_label == "Benign" and model1_conf >= confidence_threshold:
                st.success(f"✅ High Confidence Benign ({model1_conf * 100:.1f}%)")
                needs_stage2 = False
            elif model1_label == "Benign" and model1_conf < confidence_threshold:
                st.info(f"🤔 Low Confidence Benign ({model1_conf * 100:.1f}%)")
                needs_stage2 = True
            else:  # Anomalous
                st.warning(f"⚠ Anomalous ({model1_conf * 100:.1f}%)")
                needs_stage2 = True

        # Stage 2: Threat Classification
        with col2:
            st.markdown("##### Stage 2: Threat Classification")
            if needs_stage2:
                with st.spinner("XGBoost is classifying..."):
                    time.sleep(0.5)
                    model2_label = classification["model2_label"]
                    model2_conf = classification["model2_conf"]
                    model2_verdict = f"{model2_label} ({model2_conf * 100:.1f}%)"

                if model2_label == "False Positive":
                    st.info(f"🤔 False Positive ({model2_conf * 100:.1f}%)")
                else:
                    st.error(f"🚨 {model2_label} ({model2_conf * 100:.1f}%)")
            else:
                st.write("Not required for benign traffic.")
                model2_verdict = "N/A"
        
        # Stage 3: Final Action
        with col3:
            st.markdown("##### Final Action")
            final_action = classification["action"]
            
            if final_action == "ALLOWED":
                st.success("✅ ALLOWED")
                st.session_state.metrics["allowed"] += 1
            elif final_action == "BLOCKED":
                st.error("🛑 BLOCKED")
                st.session_state.metrics["blocked"] += 1
            elif final_action == "FLAGGED FOR REVIEW":
                st.info("➡ ALLOWED (Flagged for Review)")
                st.session_state.metrics["review"] += 1
                st.session_state.metrics["allowed"] += 1
        
        # Stage 4: Logging
        with col4:
            st.markdown("##### Logging")
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "request": current_request,
                "model_1_verdict": f"{model1_label} ({model1_conf*100:.1f}%)",
                "model_2_verdict": model2_verdict,
                "action": final_action,
            }
            st.session_state.logs.insert(0, log_entry)
            st.write("📝 Logged Successfully")

    time.sleep(PROCESS_DELAY)
    st.rerun()

elif st.session_state.processing_active and not st.session_state.processing_queue:
    st.success("✅ All log entries have been processed!")
    st.session_state.processing_active = False

# --- Log Display ---
st.subheader("📜 Live WAF Event Logs")
if not st.session_state.logs:
    st.info("No requests processed yet. Use the sidebar to upload and process a log file.")
else:
    log_df = pd.DataFrame(st.session_state.logs)
    st.dataframe(log_df, use_container_width=True, height=500)