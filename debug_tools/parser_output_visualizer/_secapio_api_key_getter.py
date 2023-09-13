import os

import streamlit as st


class SecapioApiKeyGetter:
    def __init__(self, st_container) -> None:
        self.st_container = st_container
        self.api_key = os.environ.get("SECAPIO_API_KEY")
        self.api_key = self.api_key or st.session_state.get("secapio_api_key")

    def get(self):
        if self.api_key:
            return self.api_key

        return self._ask_user_for_api_key()

    def _ask_user_for_api_key(self):
        with self.st_container:
            empty = st.empty()
            container = empty.container()

            container.write(
                "It seems you're trying to download a new document that isn't currently in our database. We're currently using *sec-api.io* to handle the removal of the title 10-Q page and to download 10-Q Section HTML files. In the future, we aim to download these HTML files directly from the SEC EDGAR. For now, you can get a free API key from [sec-api.io](https://sec-api.io) and input it below."
            )
            self.api_key = container.text_input(
                type="password",
                label="Enter your API key here:",
            )
            msg = "**Note:** We suggest setting the `SECAPIO_API_KEY` environment variable, possibly in an `.env` file. This method allows you to utilize the API key without the need for manual entry each time."
            container.info(msg)
            if not self.api_key:
                st.stop()

            empty.empty()
            st.session_state["secapio_api_key"] = self.api_key
            return self.api_key
