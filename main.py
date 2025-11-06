import streamlit as st
import csv
import random
import pandas as pd
from pathlib import Path

# ==========================
# PAGE CONFIG & STYLING
# ==========================
st.set_page_config(page_title="Program Rating Optimizer", layout="wide")

st.markdown("""
    <style>
    /* Background & font */
    body {
        background-color: #f9fafc;
        font-family: 'Poppins', sans-serif;
    }

    /* Title */
    .title {
        text-align: center;
        color: #2E86C1;
        font-size: 2.2em;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #5D6D7E;
        font-size: 1.1em;
        margin-bottom: 30px;
    }

    /* Card style */
    .stDataFrame, .stAlert, .stSuccess, .stInfo {
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 10px;
        background-color: #2E86C1;
        color: white;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #1B4F72;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📺 Program Rating Optimizer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Genetic Algorithm-based Scheduling System</div>', unsafe_allow_html=True)

# ---------------- FILE PATH ----------------
file_path = Path("modify_program_ratings.csv")

@st.cache_data
def read_csv_to_dict(file_path):
    """Reads CSV and converts it into a dictionary of program: ratings list."""
    program_ratings = {}
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]
            program_ratings[program] = ratings
    return program_ratings


if file_path.exists():
    ratings = read_csv_to_dict(file_path)

    # Parameters
    GEN = 100
    POP = 50
    EL_S = 2

    all_programs = list(ratings.keys())
    all_time_slots = list(range(6, 24))

    # ---------------- FITNESS FUNCTION ----------------
    def fitness_function(schedule):
        total_rating = 0
        for time_slot, program in enumerate(schedule):
            if program in ratings and time_slot < len(ratings[program]):
                total_rating += ratings[program][time_slot]
        return total_rating

    def initialize_pop(programs, time_slots):
        if not programs:
            return [[]]
        all_schedules = []
        for i in range(len(programs)):
            for schedule in initialize_pop(programs[:i] + programs[i + 1:], time_slots):
                all_schedules.append([programs[i]] + schedule)
        return all_schedules

    def finding_best_schedule(all_schedules):
        best_schedule = []
        max_ratings = 0
        for schedule in all_schedules:
            total_ratings = fitness_function(schedule)
            if total_ratings > max_ratings:
                max_ratings = total_ratings
                best_schedule = schedule
        return best_schedule

    def crossover(schedule1, schedule2):
        crossover_point = random.randint(1, len(schedule1) - 2)
        child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
        child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
        return child1, child2

    def mutate(schedule):
        mutation_point = random.randint(0, len(schedule) - 1)
        new_program = random.choice(all_programs)
        schedule[mutation_point] = new_program
        return schedule

    def genetic_algorithm(initial_schedule, generations=GEN, population_size=POP, crossover_rate=0.8, mutation_rate=0.02, elitism_size=EL_S):
        population = [initial_schedule]
        for _ in range(population_size - 1):
            random_schedule = initial_schedule.copy()
            random.shuffle(random_schedule)
            population.append(random_schedule)

        for generation in range(generations):
            population.sort(key=lambda schedule: fitness_function(schedule), reverse=True)
            new_population = population[:elitism_size]

            while len(new_population) < population_size:
                parent1, parent2 = random.choices(population, k=2)
                if random.random() < crossover_rate:
                    child1, child2 = crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()

                if random.random() < mutation_rate:
                    child1 = mutate(child1)
                if random.random() < mutation_rate:
                    child2 = mutate(child2)

                new_population.extend([child1, child2])

            population = new_population

        return population[0]

    # ---------------- TRIAL SELECTION ----------------
    st.sidebar.header("⚙️ Genetic Algorithm Settings")
    trial = st.sidebar.radio("Select a trial", ["Trial 1", "Trial 2", "Trial 3"])

    if "trial_results" not in st.session_state:
        st.session_state.trial_results = {"Trial 1": None, "Trial 2": None, "Trial 3": None}

    st.sidebar.markdown("---")

    if trial == "Trial 1":
        co_r = st.sidebar.slider("Trial 1 - Crossover Rate", 0.0, 0.95, 0.8, 0.01)
        mut_r = st.sidebar.slider("Trial 1 - Mutation Rate", 0.01, 0.05, 0.02, 0.01)
        run_trial = st.sidebar.button("🚀 Run Trial 1")
    elif trial == "Trial 2":
        co_r = st.sidebar.slider("Trial 2 - Crossover Rate", 0.0, 0.95, 0.8, 0.01)
        mut_r = st.sidebar.slider("Trial 2 - Mutation Rate", 0.01, 0.05, 0.02, 0.01)
        run_trial = st.sidebar.button("🚀 Run Trial 2")
    else:
        co_r = st.sidebar.slider("Trial 3 - Crossover Rate", 0.0, 0.95, 0.8, 0.01)
        mut_r = st.sidebar.slider("Trial 3 - Mutation Rate", 0.01, 0.05, 0.02, 0.01)
        run_trial = st.sidebar.button("🚀 Run Trial 3")

    # ---------------- RUN & SAVE TRIAL ----------------
    if run_trial:
        with st.spinner("🧠 Running Genetic Algorithm... Please wait"):
            all_possible_schedules = initialize_pop(all_programs, all_time_slots)
            initial_best_schedule = finding_best_schedule(all_possible_schedules)
            rem_t_slots = len(all_time_slots) - len(initial_best_schedule)

            genetic_schedule = genetic_algorithm(
                initial_best_schedule, generations=GEN, population_size=POP,
                crossover_rate=co_r, mutation_rate=mut_r, elitism_size=EL_S
            )

            final_schedule = initial_best_schedule + genetic_schedule[:rem_t_slots]
            df = pd.DataFrame({
                "Time Slot": [f"{t:02d}:00" for t in all_time_slots[:len(final_schedule)]],
                "Program": final_schedule
            })
            total_rating = fitness_function(final_schedule)

            st.session_state.trial_results[trial] = {"df": df, "rating": total_rating, "co": co_r, "mut": mut_r}

        st.success("✅ Trial completed successfully!")

    # ---------------- DISPLAY RESULTS ----------------
    result = st.session_state.trial_results.get(trial)
    if result:
        st.markdown(f"### 🧾 {trial} Results")
        st.caption(f"Crossover: `{result['co']:.2f}` | Mutation: `{result['mut']:.2f}`")
        st.dataframe(result["df"], use_container_width=True)
        st.success(f"⭐ Total Ratings Achieved: **{result['rating']:.2f}**")
    else:
        st.info(f"No result yet for {trial}. Run this trial to generate results.")
else:
    st.warning("⚠️ File `modify_program_ratings.csv` not found in directory.")
