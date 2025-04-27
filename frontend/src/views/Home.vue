<template>
  <main class="main-content">
    <aside class="courses-box">
      <h2>Kurse</h2>
      <ul class="course-list">
        <li v-for="course in courses" :key="course.id">
          <router-link :to="`/course/${course.id}`">
            <h3>{{ course.title }}</h3>
            <p>{{ course.short_description }}</p>
          </router-link>
        </li>
      </ul>
      <div v-if="authStore.user && !authStore.user.is_child_account" class="all-courses-link">
        <router-link to="/courses/all">Zur Auswahl aller Kurse</router-link>
      </div>
    </aside>
    <section class="learning-paths">
      <div class="stats-chart" v-show="authStore.user && authStore.user.show_stats">
        <h2>Nutzungsstatistiken (Lernminuten pro Tag)</h2>
        <div class="target-input">
          <label for="dailyTarget">Individuelles Tagesziel (Minuten):</label>
          <input id="dailyTarget" type="number" v-model.number="dailyTargetInput" min="0" />
          <button @click="saveDailyTarget">Ziel speichern</button>
        </div>
        <canvas id="statsChart"></canvas>
      </div>
    </section>
  </main>
</template>

<script>
import { onMounted, ref } from "vue";
import { Chart, registerables } from "chart.js";
import annotationPlugin from "chartjs-plugin-annotation";
import { useAuthStore } from "../store/auth";
Chart.register(...registerables, annotationPlugin);

export default {
  name: "Home",
  setup() {
    const courses = ref([]);
    const stats = ref([]);
    const dailyTarget = ref(60);
    const dailyTargetInput = ref(60);
    let statsChart = null;
    const authStore = useAuthStore();

    const fetchData = async () => {
      try {
        const coursesResponse = await fetch("http://127.0.0.1:8000/api/user/courses", {
          headers: { Authorization: "Bearer " + authStore.token },
        });
        courses.value = await coursesResponse.json();

        const statsResponse = await fetch("http://127.0.0.1:8000/api/stats", {
          headers: { Authorization: "Bearer " + authStore.token },
        });
        stats.value = await statsResponse.json();

        const settingsResponse = await fetch("http://127.0.0.1:8000/api/user/settings", {
          headers: { Authorization: "Bearer " + authStore.token }
        });
        const settingsData = await settingsResponse.json();
        dailyTarget.value = settingsData.daily_target;
        dailyTargetInput.value = settingsData.daily_target;

        createStatsChart();
      } catch (error) {
        console.error("Fehler beim Abrufen der Daten:", error);
      }
    };

    const createStatsChart = () => {
      const canvas = document.getElementById("statsChart");
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      const labels = stats.value.map((item) => item.date);
      const data = stats.value.map((item) => item.minutes);
      const backgroundColors = data.map((minutes) =>
        minutes >= dailyTarget.value ? "#ffb368" : "rgba(0, 76, 151, 0.5)"
      );
      const borderColors = data.map((minutes) =>
        minutes >= dailyTarget.value ? "#ffb368" : "rgba(0, 76, 151, 1)"
      );
      if (statsChart !== null) {
        statsChart.destroy();
      }
      statsChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Lernminuten",
              data: data,
              backgroundColor: backgroundColors,
              borderColor: borderColors,
              borderWidth: 1,
            },
          ],
        },
        options: {
          plugins: {
            annotation: {
              annotations: {
                dailyTargetLine: {
                  type: "line",
                  scaleID: "y",
                  value: dailyTarget.value,
                  borderColor: "#004c97",
                  borderWidth: 2,
                  label: {
                    enabled: true,
                    content: "Tägliches Ziel",
                    backgroundColor: "#004c97",
                    color: "#ffffff",
                  },
                },
              },
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: "Minuten",
              },
            },
            x: {
              title: {
                display: true,
                text: "Datum",
              },
            },
          },
        },
      });
    };

    const saveDailyTarget = async () => {
      try {
        await fetch("http://127.0.0.1:8000/api/user/settings", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + authStore.token
          },
          body: JSON.stringify({ daily_target: dailyTargetInput.value }),
        });
        dailyTarget.value = dailyTargetInput.value;
        createStatsChart();
      } catch (error) {
        console.error("Fehler beim Aktualisieren des täglichen Ziels:", error);
      }
    };

    onMounted(() => {
      fetchData();
    });

    return {
      courses,
      dailyTarget,
      dailyTargetInput,
      saveDailyTarget,
      authStore,
    };
  },
};
</script>

<style scoped>
.main-content {
  display: flex;
  padding: 2rem;
}
.courses-box {
  width: 33%;
  padding: 1rem;
  border: 1px solid #004c97;
  margin-right: 2rem;
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
  background-color: var(--bg);
  color: var(--fg);
}
.course-list {
  list-style-type: none;
  padding-left: 0;
  text-align: left;
}
.course-list li {
  margin-bottom: 1rem;
  padding: 0.5rem;
  border-bottom: 1px solid #004c97;
}
.all-courses-link {
  margin-top: 1rem;
  text-align: center;
}
.all-courses-link a {
  font-weight: bold;
  color: var(--btn-bg);
  text-decoration: underline;
}
.learning-paths {
  flex-grow: 1;
  background-color: var(--bg);
  color: var(--fg);
}
.stats-chart {
  margin-top: 2rem;
}
.target-input {
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
}
.target-input label {
  margin-right: 0.5rem;
}
.target-input input {
  width: 80px;
  padding: 0.25rem;
  border: 1px solid var(--btn-bg);
  border-radius: 4px;
  margin-right: 0.5rem;
  color: var(--fg);
  background-color: var(--bg);
}
.target-input button {
  padding: 0.25rem 0.5rem;
  background-color: var(--btn-bg);
  color: var(--btn-text);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.dashboard-links {
  margin-top: 2rem;
  text-align: center;
  display: flex;
  justify-content: center;
  gap: 1rem;
}
.dashboard-links a {
  text-decoration: none;
  color: var(--btn-bg);
  font-weight: bold;
}
</style>