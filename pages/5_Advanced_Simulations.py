# pages/5_Advanced_Simulations.py
import streamlit as st
import pandas as pd
from lifelines import CoxPHFitter
from causalimpact import CausalImpact

st.set_page_config(layout="wide", page_title="Advanced Simulations")
st.title("The Advanced Simulation Labs")

@st.cache_data
def load_data():
    df_master = pd.read_parquet("urbaneats_master_dataset.parquet")
    try:
        df_drivers_raw = pd.read_excel("data/UrbanEats_Driver_Analytics.xlsx")
        original_cols = df_drivers_raw.columns
        df_drivers_raw.columns = [
            col.strip().lower().replace(' ', '_').replace('-', '_').replace('.', '_')
            for col in original_cols
        ]
        return df_master, df_drivers_raw
    except FileNotFoundError:
        st.error("Could not find UrbanEats_Driver_Analytics.xlsx in the 'data' folder.")
        return df_master, None

df, df_drivers = load_data()

tab1, tab2 = st.tabs(["Driver Churn Predictor (Survival Analysis)", "Causal Impact Analyzer"])

with tab1:
    st.header("Driver Churn Predictor")
    st.markdown("Using Survival Analysis to find drivers at risk of quitting and proactively retain them.")

    @st.cache_resource
    def train_survival_model(_df_master, _df_drivers):
        if _df_drivers is None: return None, None
        driver_summary = _df_drivers.copy()
        driver_summary['churned'] = (driver_summary['account_status'] == 'inactive').astype(int)
        features = ['tenure_days', 'churned', 'avg_customer_rating', 'avg_tip_per_delivery', 'completion_rate', 'on_time_rate']
        model_df = driver_summary[features].copy()
        for col in features: model_df[col] = pd.to_numeric(model_df[col], errors='coerce')
        model_df.dropna(inplace=True)
        if model_df.empty: return None, None
        cph = CoxPHFitter(penalizer=0.1)
        try:
            cph.fit(model_df, 'tenure_days', event_col='churned')
            return cph, driver_summary
        except Exception as e:
            st.warning(f"Survival model failed to converge. Error: {e}")
            return None, None

    cph_model, driver_summary_df = train_survival_model(df, df_drivers)
    st.subheader("Driver Risk Dashboard")
    if cph_model and driver_summary_df is not None:
        active_drivers = driver_summary_df[driver_summary_df['account_status'] == 'active'].copy()
        pred_df = active_drivers[['tenure_days', 'avg_customer_rating', 'avg_tip_per_delivery', 'completion_rate', 'on_time_rate']].copy()
        for col in pred_df.columns: pred_df[col] = pd.to_numeric(pred_df[col], errors='coerce')
        pred_df.dropna(inplace=True)
        if not pred_df.empty:
            survival_prob = cph_model.predict_survival_function(pred_df, times=[30, 60, 90]).T
            active_drivers['churn_prob_30d'] = 1 - survival_prob[30.0]
            st.dataframe(active_drivers[['driver_id', 'tenure_days', 'avg_customer_rating', 'avg_tip_per_delivery', 'churn_prob_30d']].sort_values('churn_prob_30d', ascending=False).head(10).style.format({'churn_prob_30d': '{:.1%}', 'avg_customer_rating': '{:.2f}', 'avg_tip_per_delivery': '${:.2f}'}).background_gradient(cmap='Reds', subset=['churn_prob_30d']))
        with st.expander("See Model Hazard Ratios"):
            st.write("This shows which factors increase the 'risk' of a driver churning.")
            st.dataframe(cph_model.summary)
    else:
        st.error("The survival model could not be trained with the current data.")

with tab2:
    st.header("Causal Impact Analyzer")
    st.markdown("Did our interventions actually work? Constructing a 'Synthetic Control' to prove causation.")
    daily_data = df.groupby(['order_placed_at', 'city_name'])['gross_margin'].sum().unstack().asfreq('D', fill_value=0)
    
    col1, col2 = st.columns(2)
    with col1:
        city_list = daily_data.columns.tolist()
        default_index = city_list.index("Denver") if "Denver" in city_list else 0
        intervention_city = st.selectbox("Select Intervention City", options=city_list, index=default_index)
        intervention_date = st.date_input("Select Intervention Date", value=pd.to_datetime("2025-07-01"))
    
    pre_period = [str(daily_data.index.min().date()), str(intervention_date - pd.Timedelta(days=1))]
    post_period = [str(intervention_date), str(daily_data.index.max().date())]
    y = daily_data[intervention_city]
    X = daily_data.drop(columns=[intervention_city])
    causal_df = pd.concat([y, X], axis=1)
    
    st.markdown(f"Analyzing impact of an intervention in **{intervention_city}** on **{intervention_date}**.")
    
    # --- FIX: Implement a more robust, two-part sanity check ---
    pre_period_data = causal_df[pre_period[0]:pre_period[1]]
    pre_period_y = pre_period_data[intervention_city]
    pre_period_X = pre_period_data.drop(columns=[intervention_city])

    # 1. Check if the intervention city itself has any data to model.
    if pre_period_y.sum() == 0:
        st.warning(f"Analysis halted: The selected city '{intervention_city}' had zero gross margin for the entire pre-intervention period. The model has no data to learn from.")
        st.info("Please select a different city or an earlier intervention date.")
    # 2. Check if there are any viable control cities to use for prediction.
    elif pre_period_X.sum().sum() == 0:
        st.warning(f"Analysis halted: All other cities (the control group) had zero gross margin for the entire pre-intervention period. No 'synthetic control' can be built.")
        st.info("This scenario is unlikely with this dataset but is a good practice to check for.")
    else:
        try:
            # --- FIX: Specify a more stable model to aid convergence ---
            # By giving the model a simpler structure to start with, we prevent it from failing
            # when the default "find best" algorithm gets stuck.
            impact = CausalImpact(causal_df, pre_period, post_period, model_args={'niter': 5000, 'nseasons': 7})
            
            fig = impact.plot(figsize=(12, 6))
            st.pyplot(fig)
            st.text(impact.summary())
        except Exception as e:
            st.error(f"Could not run Causal Impact analysis. The model failed to converge even with stabilization. This can happen if no control cities are good predictors for the intervention city. Error: {e}")