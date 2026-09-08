# AI-Powered Portfolio Risk & Performance Dashboard

This project analyzes the historical performance and risk of individual assets and a custom portfolio using real market data from Yahoo Finance.

The main goal of this project was to build a complete automated finance & data science workflow. From proofreading inputs to downloading raw data to calculating financial metrics from each asset, the project uses AI in a practical way to help user create custom visual dashboards and understand portfolio metrics.

The project started as a finance notebook, and later was converted into a modular Streamlit application.

## Project Overview

The dashboard allows users to analyze a group of stocks or ETFs over a selected time period. Users can either enter the inputs manually through the Streamlit sidebar or describe the analysis they want using natural language.

For example, a user can type:

```text
Analyze Apple, Tesla, and Nvidia from April 2020 to  September 2024 with weights of 50%, 30%, and 20%.
```

The data pipeline is comprised as of:

User prompt or sidebar
        ↓
ai_inputs.py       # interpret AI prompt, if used
        ↓
inputs.py          # validate and standardize inputs
        ↓
pipeline.py        # download data and coordinate analysis
        ↓
finance.py         # perform calculations
        ↓
app.py             # display tables, charts, and summary

Each file handles a specific part of the data pipeline, with the goal of having a seamless experience for the user.

The calculations, data-sense and financial knowledge were fully written by me. AI was used to validate code and to create the Streamlit application.

The AI integration and input validation also had the aid of AI to be written. The architecture was also designed by me.

## Learnings

This project helped me better understand financial metrics: risk and returns. 

Additionally, this project helped me develop data automation and input check. The design and use of architecture made me a better professional, while empowering me with skills that the classroom cannot teach.

Using real data helped me understand that working with messy data is valuable, as longa as we have good procedures to clean, refine and utilize them.

Having the aid of AI was useful to learn how to collaborate with such tools, which are increasing in importance on today's job market.


## References

- [Streamlit forms](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form)
- [Streamlit session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
- [Google Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
