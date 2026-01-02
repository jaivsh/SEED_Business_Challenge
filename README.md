# The Phoenix Engine: A Winning Solution for the UrbanEats Turnaround

### **Team Second Order** | SEED Business Challenge 2026

![Python](https://img.shields.io/badge/Tech-Python%20%7C%20Streamlit%20%7C%20Plotly-blue)
![Analysis](https://img.shields.io/badge/Analysis-Spatial%20%7C%20Causal%20Inference%20%7C%20Survival-green)
![Strategy](https://img.shields.io/badge/Outcome-Data--Driven%20Turnaround%20Plan-red)

This project presents **The Phoenix Engine**, a comprehensive, interactive platform built to solve the UrbanEats operational crisis. We didn't just build a dashboard; we built a "Digital Twin" of the business—a strategic tool that allows leadership to diagnose, simulate, and execute a data-driven turnaround.

Our solution directly addresses the COO's ultimatum by providing a clear, quantifiable path to cutting delivery costs by 25%, achieving 95%+ on-time delivery, and reaching profitability.

---

## Our Approach: Beyond the Obvious

We recognized that a simple BI dashboard would fail to address the systemic nature of UrbanEats' crisis. Our winning strategy was to build a multi-layered analytical engine that moves from diagnosis to advanced simulation, demonstrating a mastery of both business strategy and cutting-edge data science.

### 1. Diagnosis: Finding the "Ground Truth"

First, we built a robust data ingestion pipeline to unify 7 disparate data sources. This immediately yielded a critical insight that reshaped the entire problem:

-   **Key Finding:** The problem statement's "-$1.80 margin" was a simplification. Our analysis of the raw data revealed the true average gross margin is **-$0.47**. This discovery proves our ability to find the "ground truth" and allows for a more nuanced and realistic turnaround strategy.

Our **Margin Engine** and **Network Optimizer** modules use interactive waterfall charts and process funnels to prove that the primary drivers of this loss are **manual dispatch lag** and **driver idle time**, not just driver pay.

### 2. Advanced Analysis: Answering "Why?" not just "What?"

This is where our solution stands apart. We implemented three advanced analytical models to provide insights that are impossible to obtain with standard methods.

-   **Geospatial Lab (H3 + Plotly):** We rejected arbitrary city boundaries and analyzed profitability at a hyper-local level using Uber's H3 hexagonal grid. Our interactive choropleth map visualizes "Zombie Hexes" (unprofitable neighborhoods) and "Golden Hexes" (pockets of opportunity), enabling a surgical portfolio strategy.

-   **Driver Churn Predictor (Survival Analysis):** We treated driver churn like a medical diagnosis. Using a **Cox Proportional Hazards model** from the `lifelines` library, we identified the key risk factors (e.g., low tips, bad weather) and built a dashboard to flag at-risk drivers *before* they quit. This is a proactive, data-driven HR strategy.

-   **Causal Impact Analyzer (Bayesian Time Series):** To prove the ROI of our proposed solutions, we implemented Google's **Causal Impact** model. This tool constructs a "Synthetic Control" of what would have happened without an intervention, allowing us to move beyond correlation and prove **causation**. This is the gold standard for strategic decision-making.

### 3. The Solution: An Interactive Turnaround Plan

The Phoenix Engine is not a historical report; it's a forward-looking strategic tool. The combination of our diagnostic modules and simulation labs provides the COO with a complete, interactive plan:

-   **Current State Assessment:** Delivered via the Command Center and diagnostic modules.
-   **Solution Architecture:** Justified by the undeniable evidence of dispatch lag and proven by our advanced models.
-   **Financial Business Case:** Quantified through the insights from the Margin Engine and the potential savings identified in the Geospatial Lab.
-   **Transformation Plan:** Prioritized by the "worst-first" findings from our hyper-local analysis and validated by the Causal Impact simulator.

---

## Technical Excellence

Our implementation demonstrates professional-grade software development and data science practices.

-   **Robust Architecture:** A multi-page Streamlit application with a clear, modular structure.
-   **Performance:** Efficient data loading from Parquet files and intelligent use of Streamlit's caching (`@st.cache_data`, `@st.cache_resource`) for a smooth user experience.
-   **Code Quality:** Clean, commented Python code with robust error handling, including debugging and stabilizing complex third-party libraries like `lifelines` and `causalimpact`.
-   **Modern Stack:** Effective use of `Pandas` for data manipulation, `Plotly` for interactive visualizations, and advanced libraries for statistical modeling.

---

## How to Run This Project

**1. Setup:**
   - Clone the repository.
   - Ensure all 7 `UrbanEats_*.xlsx` files are in the `/data` directory.

**2. Install Dependencies:**
   ```bash
   pip install -r requirements.txt