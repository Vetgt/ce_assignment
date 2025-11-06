import streamlit as st
import csv
import random
import pandas as pd
from pathlib import Path

# =======================
# PAGE CONFIG
# =======================
st.set_page_config(page_title="Program Rating Optimizer", layout="wide")

# =======================
# CUSTOM DARK THEME CSS
# =======================
st.markdown("""
    <style>
    /* Global background and text color */
    .stApp {
        background-color: #0e1117;
        color: #f0f2f6;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: #e5e7eb;
        font-weight: 600;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1e222b !important;
        color: #f0f2f6;
    }

    /* Buttons */
    .stButton>button {
        background-color: #2b313e;
        color: #f0f2f6;
        border: 1px solid #3a3f4b;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3f4654;
        border-color: #6b7280;
        color: white;
    }

    /* DataFrame */
    .stDataFrame {
        background-color: #1a1d23;
        border-radius: 10px;
        padding: 0.5em;
    }

    /* Alerts */
    .stSuccess {
        background-color: #1b4332 !important;
        color: #d8f3dc !important;
        border-radius: 6px;
        padding: 0.6em;
    }
    .stInfo {
        background-color: #1e3a8a !important;
        color: #bfdbfe !important;
        border-radius: 6px;
        padding: 0.6em;
    }
    .stWarning {
        background-color: #78350f !important;
        color: #fde68a !important;
        border-radius: 6px;
        padding: 0.6em;
    }

    /* Sliders */
    .stSlider label {
        color: #f0f2f6 !important;
        font-weight: 500;
    }

    /* Divider line */
    hr {
        border: 1px solid #2d323c;
    }
    </style>
""", unsafe_allow_html=True)

# =======================
# PAGE HEADER
# =======================
st.title("Program Rating Optimizer")
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#d1d5db; font-size:16px;'>Optimize your TV program scheduling using a Genetic Algorithm. "
    "Adjust parameters, run trials, and compare the best schedules efficiently.</p>",
    unsafe_allow_html=True
)

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


# =======================
# MAIN APP BODY
# =======================
if file_path.exists():
    # Read ratings data
    ratings = read_csv_to_dict(file_path)

    # Parameters
    GEN = 100
    POP = 50
    EL_S = 2

    all_programs = list(ratings.keys())  # all programs
    all_time_slots = list(range(6, 24))  # 6:00 to 23:00

    # ---------------- FITNESS FUNCTION ----------------
    def fitness_function(schedule):
        total_rating = 0
        for time_slot, program in enumerate(schedule):
            if program in ratings and time_slot < len(ratings[program]):
                total_rating += ratings[program][time_slot]
        return total_rating

    # ---------------- INITIALIZATION ----------------
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

    # ---------------- GA OPERATORS ----------------
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
            new_population = []
            population.sort(key=lambda schedule: fitness_function(schedule), reverse=True)
            new_population.extend(population[:elitism_size])

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

    # ---------------- SIDEBAR ----------------
    st.sidebar.header("Trial Configuration")
    st.sidebar.markdown("Adjust GA parameters and execute multiple trials for comparison.")

    trial = st.sidebar.radio("Select Trial", ["Trial 1", "Trial 2", "Trial 3"])

    if "trial_results" not in st.session_state:
        st.session_state.trial_results = {"Trial 1": None, "Trial 2": None, "Trial 3": None}

    if trial == "Trial 1":
        co_r = st.sidebar.slider("Crossover Rate", 0.0, 0.95, 0.8, 0.01)
        mut_r = st.sidebar.slider("Mutation Rate", 0.01, 0.05, 0.02, 0.01)
        run_trial = st.sidebar.button("Run Trial 1")
    elif trial == "Trial 2":
        co_r = st.sidebar.slider("Crossover Rate", 0.0, 0.95, 0.8, 0.01)
        mut_r = st.sidebar.slider("Mutation Rate", 0.01, 0.05, 0.02, 0.01)
        run_trial = st.sidebar.button("Run Trial 2")
    else:
        co_r = st.sidebar.slider("Crossover Rate", 0.0, 0.95, 0.8, 0.01)
        mut_r = st.sidebar.slider("Mutation Rate", 0.01, 0.05, 0.02, 0.01)
        run_trial = st.sidebar.button("Run Trial 3")

    # ---------------- RUN & SAVE TRIAL ----------------
    if run_trial:
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

        # Save to session state
        st.session_state.trial_results[trial] = {"df": df, "rating": total_rating, "co": co_r, "mut": mut_r}

    # ---------------- DISPLAY RESULTS ----------------
    st.markdown("<hr>", unsafe_allow_html=True)
    result = st.session_state.trial_results.get(trial)
    if result:
        st.subheader(f"{trial} Results")
        st.markdown(f"<p style='color:#9ca3af;'>Crossover Rate: {result['co']:.2f} | Mutation Rate: {result['mut']:.2f}</p>", unsafe_allow_html=True)
        st.dataframe(result["df"], use_container_width=True)
        st.success(f"Total Ratings: {result['rating']:.2f}")
    else:
        st.info(f"No result yet for {
