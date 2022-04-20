mkdir -p ~/.streamlit/

echo "\
[server]\n\
port = $PORT\n\
enableCORS = false\n\
headless = true\n\
maxUploadSize = 500\n\
maxMessageSize = 1000\n\
\n\
" > ~/.streamlit/config.toml
