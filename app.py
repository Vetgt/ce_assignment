import streamlit as st
from main import read_csv_to_dict, genetic_algorithm, fitness_function

st.title("📺 Program Scheduling using Genetic Algorithm")

url = "https://raw.githubusercontent.com/Vetgt/ce_assignment/main/program_ratings.csv"

import requests, io, csv

try:
    s = requests.get(url).content.decode('utf-8')
    with open("temp.csv", "w", encoding="utf-8") as f:
        f.write(s)
    ratings = read_csv_to_dict("temp.csv")
    st.success("✅ CSV loaded successfully from GitHub!")
except Exception as e:
    st.error(f"❌ Failed to load CSV: {e}")
    st.stop()

generations = st.slider("Generations", 10, 500, 100)
population = st.slider("Population Size", 10, 200, 50)

if st.button("Run Optimization"):
    best_schedule = genetic_algorithm(ratings, generations=generations, population_size=population)
    total_score = fitness_function(best_schedule, ratings)

    st.subheader("📅 Optimal Schedule")
    for i, program in enumerate(best_schedule, start=6):
        st.write(f"Time Slot {i:02d}:00 - {program}")

    st.write(f"**Total Ratings:** {total_score:.2f}")
