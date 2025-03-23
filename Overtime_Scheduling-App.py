# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 17:31:53 2025

@author: Nsuhoridem Jackson
"""

import streamlit as st
import pandas as pd
from ortools.linear_solver import pywraplp

#=============================================================================
#                       STREAMLIT UI IMPROVEMENTS
#=============================================================================

# Set Streamlit Page Configuration
st.set_page_config(page_title="Overtime Scheduling App", page_icon="🕒", layout="wide")

# Add a stylish header
st.markdown(
    """
    <style>
       .main-title {
            text-align: center;
            font-size: 70px; /* Increased size */
            font-weight: bold;
            font-color: blue;
        }
        .sub-title {
            text-align: center;
            font-size: 36px; /* Increased size */
            color: #6E6E6E;
         }
        [data-testid="stSidebar"] {
            background-color: #002147 !important;
            padding: 20px !important;
            border: 3px solid #FFFFFF !important;
            width: 500px !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        .sidebar-input label {
            font-weight: bold;
        }
        .sidebar-input input {
            color: black !important;
            font-size: 16px !important;
            font-weight: bold !important;
            background-color: white !important;
            border-radius: 5px !important;
        }
        /* Fix for number input fields to ensure visibility */
        section[data-testid="stSidebar"] input {
            color: black !important;
            font-size: 16px !important;
            font-weight: bold !important;
            background-color: white !important;
            border: 1px solid #ccc !important;
            padding: 5px !important;
        }
    </style>
    """, unsafe_allow_html=True
)

# Add a stylish header
st.markdown(
    """
    <h1 color= blue; class='main-title'>📊 OTMaster</h1>
    <h2 class='sub-title'>Optimize your workforce productivity and manage overtime efficiently</h2>
    <p style='text-align: center; color: green; font-size: 22px;'><i>With Google OR-Tools</i></p>
    """, unsafe_allow_html=True
)

# Instructions for file format
st.sidebar.header("📌 Employee Data: File Upload Instructions")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("Ensure your Excel file contains the following columns:")
st.sidebar.write("Ensure columns are labelled exactly as shown:")
st.sidebar.markdown("- **Employee Name** (Text)\n- **Average Productivity (Parts/Hr)** (Numeric)\n- **Hourly Wage** (Numeric)")
st.sidebar.warning("Ensure there are no empty cells in these columns.")

#=============================================================================
#                       FILE UPLOADER DESIGN
#=============================================================================
# Add custom CSS for styling
# Add custom CSS for styling
st.markdown(
    """
    <style>
        .upload-container {
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            background-color: #e3f2fd;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            margin: auto;
            width: 50%;
        }
        .upload-title {
            font-size: 28px;
            font-weight: bold;
            color: #0d47a1;
        }
        .upload-subtitle {
            font-size: 18px;
            color: #1565c0;
        }
        .stFileUploader {
            text-align: center;
            display: flex;
            justify-content: center;
        }
        
        .sidebar-input label {
            font-weight: bold;
        }
        .sidebar-input input {
            color: black !important;
            font-size: 16px !important;
            font-weight: bold !important;
            background-color: white !important;
            border-radius: 5px !important;
        }
    </style>
    """, unsafe_allow_html=True
)

# Centered Upload Section
st.markdown("""
    <div class='upload-container'>
        <p class='upload-title'></p>
        <p class='upload-subtitle'>Upload Your Employee Data And Optimize Overtime Allocation</p>
    </div>
    """, unsafe_allow_html=True)

# Upload Excel file with Streamlit file uploader
uploaded_file = st.file_uploader("", type=["xlsx"], help="Upload an Excel file with employee details")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### 📂 Employee Data Preview:")
    st.dataframe(df)


    #=============================================================================
    #                       EXTRACT DATA FROM FILE
    #=============================================================================
    
    productivity = df['Average Productivity (Parts/Hr)'].tolist()
    hourly_wage = df['Hourly Wage'].tolist()
    employee_name = df['Employee Name'].tolist()
    num_employees = len(productivity)
    
    #=============================================================================
    #                       USER INPUT PARAMETERS
    #=============================================================================
    
  #  with st.sidebar:
  #      st.header("⚙️ Optimization Settings")
 #       Max_budget_P = st.number_input("💰 Maximum Overtime Budget:", min_value=0, value=300000, format='%d', key='budget')
  #      Max_Overtime_Q = st.number_input("⏳ Maximum Overtime Hours:", min_value=0, value=1000, format='%d', key='overtime')
  #      Min_allocation = st.number_input("🔽 Minimum Overtime per Employee:", min_value=0, value=50, format='%d', key='min_alloc')
   #     Max_difference = st.number_input("⚖️ Max Difference Between Employees:", min_value=0, value=40, format='%d', key='max_diff')
    
    #=============================================================================
#                       USER INPUT PARAMETERS (Centered and Always Visible)
#=============================================================================

st.markdown("### ⚙️ Optimization Settings")

col1, col2 = st.columns(2)
with col1:
    Max_budget_P = st.number_input("💰 Maximum Overtime Budget:", min_value=0, value=300000, format='%d', key='budget')
    Min_allocation = st.number_input("🔽 Minimum Overtime per Employee:", min_value=0, value=50, format='%d', key='min_alloc')

with col2:
    Max_Overtime_Q = st.number_input("⏳ Maximum Overtime Hours:", min_value=0, value=1000, format='%d', key='overtime')
    Max_difference = st.number_input("⚖️ Max Difference Between Employees:", min_value=0, value=40, format='%d', key='max_diff')

    
    #=============================================================================
    #                       OPTIMIZATION PROCESS
    #=============================================================================
    
    if st.button("🚀 Run Optimization"):
        solver = pywraplp.Solver.CreateSolver('CBC')
        if not solver:
            st.error("Solver initialization failed!")
        
        # Define decision variables (overtime hours assigned per employee)
        x = [solver.IntVar(0, solver.infinity(), f'x_{i+1}') for i in range(num_employees)]
        
        # Objective Function: Maximize Total Productivity
        objective = solver.Objective()
        for i in range(num_employees):
            objective.SetCoefficient(x[i], productivity[i])
        objective.SetMaximization()
        
        #=============================================================================
        #                       CONSTRAINTS
        #=============================================================================
        
        # Total Overtime Hours Constraint
        solver.Add(solver.Sum(x) <= Max_Overtime_Q)
        
        # Budget Constraint
        solver.Add(solver.Sum([hourly_wage[i] * x[i] for i in range(num_employees)]) <= Max_budget_P)
        
        # Minimum and Maximum Allocation Constraints
        for i in range(num_employees):
            solver.Add(x[i] >= Min_allocation)
            #solver.Add(x[i] <= Max_allocation)
        
         #Fairness Constraint: Limit the difference between employees' overtime hours
        for i in range(num_employees):
            for j in range(i + 1, num_employees):
                solver.Add(x[i] - x[j] <= Max_difference)
                solver.Add(x[j] - x[i] <= Max_difference)
        
        #=============================================================================
        #                       SOLVING THE OPTIMIZATION PROBLEM
        #=============================================================================
        
        status = solver.Solve()
        
        #=============================================================================
        #                       DISPLAY RESULTS
        #=============================================================================
        
        if status == pywraplp.Solver.OPTIMAL:
            st.success("✅ Optimization Completed Successfully!")
            st.write("### 🏆 Optimal Overtime Allocation:")
            results = {"Employee": [], "Overtime Hours": []}
            for i in range(num_employees):
                results["Employee"].append(employee_name[i])
                results["Overtime Hours"].append(round(x[i].solution_value()))
            df_results = pd.DataFrame(results)
            st.dataframe(df_results)
            st.metric(label="📈 Maximum Achievable Productivity", value=f"{round(solver.Objective().Value())} Units/Annum")
        else:
            st.error("No optimal solution found. Please adjust constraints and try again.")



#streamlit run Overtime_Scheduling-App.py
#cd C:/Users/Nsuhoridem Jackson/OneDrive/Desktop/MENG/OPTIMIZATION/PROJECT
