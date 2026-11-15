
import streamlit as st
import pandas as pd
import random

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="TV Scheduling - Genetic Algorithm",
    page_icon="📺",
    layout="wide"
)

st.title("TV Scheduling Using Genetic Algorithm")
st.write(
    "An intelligent TV scheduling system that uses "
    "Genetic Algorithms to maximise programme ratings."
)

# ==========================================
# 2. LOAD CSV DATASET
# ==========================================

def load_data():
    df = pd.read_csv("program_ratings.csv")

    first_column = df.columns[0]
    df = df.set_index(first_column)

    return df.astype(float)

try:
    ratings = load_data()
    programs = ratings.index.tolist()
    hours = [int(col.replace("Hour ", "")) for col in ratings.columns]

    st.success("Programme ratings dataset loaded successfully!")

except Exception as e:
    st.error(f"Unable to load CSV file: {e}")
    st.stop()


# ==========================================
# 3. GENETIC ALGORITHM SETTINGS
# ==========================================

GEN = 100
POP = 50
EL_S = 2

# ==========================================
# 4. FITNESS FUNCTION
# ==========================================

def fitness_function(schedule):
    total_rating = 0

    for i, program in enumerate(schedule):
        hour_column = f"Hour {hours[i]}"
        total_rating += ratings.loc[program, hour_column]

    return total_rating


# ==========================================
# 5. INITIALIZE POPULATION
# ==========================================

def initialize_population(population_size):

    population = []

    for _ in range(population_size):
        schedule = [
            random.choice(programs)
            for _ in hours
        ]

        population.append(schedule)

    return population


# ==========================================
# 6. SELECTION
# ==========================================

def selection(population):

    candidates = random.sample(population, 3)

    return max(candidates, key=fitness_function)


# ==========================================
# 7. CROSSOVER
# ==========================================

def crossover(parent1, parent2):

    point = random.randint(1, len(parent1) - 1)

    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]

    return child1, child2


# ==========================================
# 8. MUTATION
# ==========================================

def mutate(schedule):

    position = random.randint(0, len(schedule) - 1)

    schedule[position] = random.choice(programs)

    return schedule


# ==========================================
# 9. GENETIC ALGORITHM
# ==========================================

def genetic_algorithm(
    crossover_rate,
    mutation_rate,
    seed=42
):

    random.seed(seed)

    population = initialize_population(POP)

    for generation in range(GEN):

        population.sort(
            key=fitness_function,
            reverse=True
        )

        new_population = [
            schedule.copy()
            for schedule in population[:EL_S]
        ]

        while len(new_population) < POP:

            parent1 = selection(population)
            parent2 = selection(population)

            if random.random() < crossover_rate:

                child1, child2 = crossover(
                    parent1, parent2
                )

            else:

                child1 = parent1.copy()
                child2 = parent2.copy()

            if random.random() < mutation_rate:
                child1 = mutate(child1)

            if random.random() < mutation_rate:
                child2 = mutate(child2)

            new_population.append(child1)

            if len(new_population) < POP:
                new_population.append(child2)

        population = new_population

    best_schedule = max(
        population,
        key=fitness_function
    )

    return best_schedule


# ==========================================
# 10. DISPLAY DATASET
# ==========================================

with st.expander("View Programme Ratings Dataset"):

    st.dataframe(
        ratings,
        use_container_width=True
    )


# ==========================================
# 11. USER INPUT PARAMETERS
# ==========================================

st.header("Genetic Algorithm Parameters")

st.write(
    "Adjust the crossover and mutation rates "
    "to experiment with different schedules."
)

trial_parameters = []

columns = st.columns(3)

default_values = [
    (0.80, 0.02),
    (0.60, 0.03),
    (0.90, 0.04)
]

for i, column in enumerate(columns):

    with column:

        st.subheader(f"Trial {i + 1}")

        co_r = st.slider(
            "Crossover Rate (CO_R)",
            min_value=0.0,
            max_value=0.95,
            value=default_values[i][0],
            step=0.05,
            key=f"co_{i}"
        )

        mut_r = st.slider(
            "Mutation Rate (MUT_R)",
            min_value=0.01,
            max_value=0.05,
            value=default_values[i][1],
            step=0.01,
            key=f"mut_{i}"
        )

        trial_parameters.append((co_r, mut_r))


# ==========================================
# 12. RUN THREE EXPERIMENTS
# ==========================================

st.divider()

if st.button("Run All Three Trials", type="primary"):

    results = []

    for i, (co_r, mut_r) in enumerate(trial_parameters):

        with st.spinner(f"Running Trial {i + 1}..."):

            best_schedule = genetic_algorithm(
                crossover_rate=co_r,
                mutation_rate=mut_r,
                seed=42 + i
            )

            total_rating = fitness_function(
                best_schedule
            )

            schedule_data = []

            for j, program in enumerate(best_schedule):

                hour = hours[j]

                schedule_data.append({
                    "Time Slot": f"{hour:02d}:00",
                    "Programme": program,
                    "Rating": ratings.loc[
                        program, f"Hour {hour}"
                    ]
                })

            schedule_df = pd.DataFrame(schedule_data)

            results.append({
                "Trial": f"Trial {i + 1}",
                "CO_R": co_r,
                "MUT_R": mut_r,
                "Total Rating": total_rating,
                "Schedule": schedule_df
            })

    # ======================================
    # 13. DISPLAY EXPERIMENT COMPARISON
    # ======================================

    st.success("All three experiments completed!")

    st.header("Experiment Comparison")

    comparison = pd.DataFrame([
        {
            "Trial": result["Trial"],
            "CO_R": result["CO_R"],
            "MUT_R": result["MUT_R"],
            "Total Rating": result["Total Rating"]
        }
        for result in results
    ])

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    # ======================================
    # 14. DISPLAY INDIVIDUAL SCHEDULES
    # ======================================

    st.header("Generated TV Schedules")

    for result in results:

        st.subheader(result["Trial"])

        st.write(
            f"Crossover Rate: {result['CO_R']} | "
            f"Mutation Rate: {result['MUT_R']}"
        )

        st.metric(
            "Total Programme Rating",
            f"{result['Total Rating']:.2f}"
        )

        st.dataframe(
            result["Schedule"],
            use_container_width=True,
            hide_index=True
        )

    # ======================================
    # 15. BEST EXPERIMENT
    # ======================================

    best_result = max(
        results,
        key=lambda x: x["Total Rating"]
    )

    st.divider()

    st.header("Best Performing Experiment")

    st.success(
        f"{best_result['Trial']} achieved the "
        f"highest total rating of "
        f"{best_result['Total Rating']:.2f}."
    )

    st.write(
        f"CO_R: {best_result['CO_R']} | "
        f"MUT_R: {best_result['MUT_R']}"
    )
