# AI-Powered Portfolio Risk & Performance Dashboard

This project analyzes the historical performance and risk of individual assets and a custom portfolio using real market data from Yahoo Finance.

The main goal of this project was to build a complete automated finance and data science workflow: from validating user inputs, to downloading raw market data, to calculating asset and portfolio metrics, to displaying the results in an interactive dashboard.

The project uses AI in a practical way to help users create custom portfolio analyses and understand the results in plain language.

The project started as a finance analysis notebook and was later converted into a modular Streamlit application.

## Project Overview

The dashboard allows users to analyze a group of stocks or ETFs over a selected time period. Users can either enter inputs manually through the Streamlit sidebar or describe the analysis they want using natural language.

For example, a user can type:

```text
Analyze Apple, Tesla, and Nvidia from April 2020 to September 2024 with weights of 50%, 30%, and 20%.
```

The data pipeline is structured as follows:

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

Each file handles a specific part of the workflow, with the goal of creating a more organized and reliable user experience.

The financial calculations, metric logic, data validation structure, and overall project architecture were designed and implemented by me. AI was used as a development assistant for debugging, code validation, implementation support, and parts of the Streamlit interface.

## Learnings

This project helped me better understand financial metrics related to risk, return, volatility, drawdown, correlation, and portfolio performance.
It also helped me develop stronger skills in data automation, input validation, modular code organization, and dashboard design. Turning the original notebook into a Streamlit application made the project feel closer to a real data product, not just a static analysis.

Working with real market data also showed me the importance of having good procedures to clean, validate, and organize data before using it for analysis.

Using AI as part of the development process helped me learn how to collaborate with these tools in a practical way. Instead of using AI to replace the financial logic, I used it to support the workflow, improve the interface, and make the final product easier to use.

```markdown
## Core Principle

Python calculates. AI structures inputs and explains results.
```

## References

- [Streamlit forms](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form)
- [Streamlit session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
- [Google Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
