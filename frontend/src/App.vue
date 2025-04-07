<template>
  <div class="app">
    <header>
      <h1>Willkommen auf der nutzungsfreundlichen Lernplattform</h1>
    </header>
    <div class="next-meeting-box">
      <div class="meeting-text">
        Dein nächster Kurstermin findet statt am: {{ meetingStartFormatted }} – {{ meetingEndFormatted }}
        <br />
        Thema: Einführung in die digitale Diversität
      </div>
      <button
        class="meeting-button"
        :disabled="!meetingActive"
        @click="handleMeetingClick"
      >
        Jetzt der Videokonferenz beitreten <span class="meeting-emojis">📹👥</span>
      </button>
    </div>
    <main class="main-content">
      <aside class="courses-box">
        <h2>Kurse</h2>
        <ul class="course-list">
          <li v-for="course in courses" :key="course.id">
            <h3>{{ course.title }}</h3>
            <p>{{ course.description }}</p>
          </li>
        </ul>
      </aside>
      <section class="learning-paths">
        <h2>Lernpfade</h2>
        <ul class="learningpath-list">
          <li v-for="lp in learningPaths" :key="lp.id">
            <h3>{{ lp.name }}</h3>
            <ul class="course-list-inside">
              <li v-for="course in lp.courses" :key="course.id">
                {{ course.title }}
              </li>
            </ul>
          </li>
        </ul>
        <!-- Nutzungsstatistiken Grafik und Zielanpassung -->
        <div class="stats-chart">
          <h2>Nutzungsstatistiken (Lernminuten pro Tag)</h2>
          <div class="target-input">
            <label for="dailyTarget">Individuelles Tagesziel (Minuten):</label>
            <input
              id="dailyTarget"
              type="number"
              v-model.number="dailyTargetInput"
              min="0"
            />
            <button @click="saveDailyTarget">Ziel speichern</button>
          </div>
          <canvas id="statsChart"></canvas>
        </div>
      </section>
    </main>
    <!-- Support-Chatbot Overlay -->
    <div class="chat-overlay">
      <button class="chat-btn" @click="toggleChat">
        ?
      </button>
      <div v-if="chatOpen" class="chat-window">
        <div class="chat-header">
          <img src="./assets/assistant.jpg" alt="Portrait von Steve" class="assistant-portrait" />
          <span>Steve (KI-Assistent)</span>
          <button class="close-btn" @click="toggleChat">&times;</button>
        </div>
        <div class="chat-body">
          <p class="chat-message">
          </p>
        <div v-for="msg in chatMessages" :key="msg.timestamp" class="chat-message">
          <span class="timestamp">{{ msg.timestamp }}</span> - {{ msg.text }}
        </div>
        </div>
        <div class="chat-footer">
          <input type="text" placeholder="Nachricht eingeben..." v-model="chatInput" @keyup.enter="sendMessage" />
          <button @click="sendMessage">Senden</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref, computed } from "vue";
import { Chart, registerables } from "chart.js";
import annotationPlugin from "chartjs-plugin-annotation";

Chart.register(...registerables, annotationPlugin);

export default {
  name: "App",
  setup() {
    const courses = ref([]);
    const learningPaths = ref([]);
    const stats = ref([]);
    const dailyTarget = ref(60);
    const dailyTargetInput = ref(60);
    const chatOpen = ref(false);
    const chatInput = ref("");
    const chatMessages = ref([]);
    let statsChart = null;

    // Berechne Meeting-Startzeit (aktuelle Zeit + 2 Minuten) und Endzeit (Startzeit + 60 Minuten)
    const meetingStartTime = ref(new Date(Date.now() + 2 * 60 * 1000));
    const meetingEndTime = ref(new Date(meetingStartTime.value.getTime() + 60 * 60 * 1000));

    const meetingStartFormatted = computed(() => {
      return meetingStartTime.value.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    });
    const meetingEndFormatted = computed(() => {
      return meetingEndTime.value.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    });

    // Reaktive Variable, die angibt, ob der Kurs (Meeting) begonnen hat
    const meetingActive = ref(false);

    // Überprüfe jede Sekunde, ob die Startzeit erreicht wurde
    setInterval(() => {
      meetingActive.value = (new Date() >= meetingStartTime.value);
    }, 1000);

    // Event-Handler für den Meeting-Button
    const handleMeetingClick = () => {
      if (!meetingActive.value) {
        alert("Der Kurs hat noch nicht begonnen.");
      } else {
        alert("Videokonferenz wird gestartet...");
      }
    };

    /**
     * Ruft die aktuellen Kurs-, Lernpfad-, Statistikdaten sowie das tägliche Ziel vom Backend ab.
     */
    const fetchData = async () => {
      try {
        const coursesResponse = await fetch("http://127.0.0.1:8000/api/courses");
        courses.value = await coursesResponse.json();
        const lpResponse = await fetch("http://127.0.0.1:8000/api/learning-paths");
        learningPaths.value = await lpResponse.json();
        const statsResponse = await fetch("http://127.0.0.1:8000/api/stats");
        stats.value = await statsResponse.json();
        const settingsResponse = await fetch("http://127.0.0.1:8000/api/settings");
        const settingsData = await settingsResponse.json();
        dailyTarget.value = settingsData.daily_target;
        dailyTargetInput.value = settingsData.daily_target;
        createStatsChart();
      } catch (error) {
        console.error("Fehler beim Abrufen der Daten:", error);
      }
    };

    /**
     * Erzeugt die Statistik-Grafik inkl. einer horizontalen Linie, die das tägliche Lernziel darstellt.
     * Zudem wird für jeden Balken überprüft, ob das Ziel erreicht wurde, und die Farbe entsprechend gesetzt.
     */
    const createStatsChart = () => {
      const ctx = document.getElementById("statsChart").getContext("2d");
      const labels = stats.value.map(item => item.date);
      const data = stats.value.map(item => item.minutes);
      // Dynamische Farben für jeden Balken: Ziel erreicht => #ffb368, sonst Standardfarbe.
      const backgroundColors = data.map(minutes =>
        minutes >= dailyTarget.value ? "#ffb368" : "rgba(0, 76, 151, 0.5)"
      );
      const borderColors = data.map(minutes =>
        minutes >= dailyTarget.value ? "#ffb368" : "rgba(0, 76, 151, 1)"
      );
      if (statsChart !== null) {
        statsChart.destroy();
      }
      statsChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [{
            label: "Lernminuten",
            data: data,
            backgroundColor: backgroundColors,
            borderColor: borderColors,
            borderWidth: 1
          }]
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
                    color: "#ffffff"
                  }
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: "Minuten"
              }
            },
            x: {
              title: {
                display: true,
                text: "Datum"
              }
            }
          }
        }
      });
    };

    /**
     * Sendet das neue tägliche Ziel an das Backend und aktualisiert die Anzeige.
     */
    const saveDailyTarget = async () => {
      try {
        await fetch("http://127.0.0.1:8000/api/settings", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ daily_target: dailyTargetInput.value })
        });
        dailyTarget.value = dailyTargetInput.value;
        createStatsChart();
      } catch (error) {
        console.error("Fehler beim Aktualisieren des täglichen Ziels:", error);
      }
    };

    /**
     * Liefert den aktuellen Zeitstempel als String.
     */
    const getCurrentTimestamp = () => {
      const now = new Date();
      return now.toLocaleTimeString();
    };

    /**
     * Schaltet das Chatfenster um.
     */
    const toggleChat = () => {
      chatOpen.value = !chatOpen.value;
      // Beim Öffnen des Chats initial eine Begrüßungsnachricht von Steve hinzufügen.
      if (chatOpen.value && chatMessages.value.length === 0) {
        const greeting = `Hallo, mein Name ist Steve. Du hast Fragen zur Bedienung dieser Lernplattform oder Fragen zum aktuellen Inhalt? Ich helfe dir gerne weiter.`;
        addChatMessage(greeting);
      }
    };

    /**
     * Fügt die vom User eingegebene Nachricht dem Chat hinzu und simuliert eine automatische Antwort.
     */
    const sendMessage = () => {
      if (chatInput.value.trim() !== "") {
        addChatMessage(chatInput.value.trim());
        chatInput.value = "";
        // Nach 3 Sekunden automatische Antwort von Steve.
        setTimeout(() => {
          const autoResponse = `Klicke hierzu oben im Menü auf 'Profil'. Solltest du dort nicht fündig werden, kontaktiere mich gerne erneut.`;
          addChatMessage(autoResponse);
        }, 3000);
      }
    };

        /**
     * Fügt eine Nachricht zum Chatverlauf hinzu.
     * @param {string} text Nachrichtentext.
     */
    const addChatMessage = (text) => {
      const timestamp = new Date().toLocaleTimeString();
      chatMessages.value.push({ text, timestamp });
    };

    onMounted(() => {
      fetchData();
    });

    return {
      courses,
      learningPaths,
      dailyTarget,
      dailyTargetInput,
      chatOpen,
      chatInput,
      chatMessages,
      toggleChat,
      sendMessage,
      saveDailyTarget,
      getCurrentTimestamp,
      meetingStartFormatted,
      meetingEndFormatted,
      meetingActive,
      handleMeetingClick
    };
  } // Ende der setup-Funktion
}; // Ende des export default
</script>

<style scoped>
.app {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  color: #004c97;
  background-color: #ffffff;
}

/* Header */
header {
  background-color: #004c97;
  padding: 1rem;
  color: #ffffff;
  text-align: center;
}

/* Neuer Meeting-Kasten */
.next-meeting-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f5f5;
  padding: 1rem 2rem;
  border-bottom: 1px solid #004c97;
}
.meeting-text {
  font-size: 1rem;
}
.meeting-button {
  background-color: #cccccc; /* Standard: grau */
  color: #ffffff;
  border: none;
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  transition: background-color 0.3s;
}

.meeting-button:enabled {
  background-color: #004c97; /* Aktiv: blau */
}

.meeting-button:disabled:hover {
  cursor: not-allowed;
}

/* Für die Emojis im Button */
.meeting-emojis {
  font-size: 1.5rem;
  color: #ffb368;
  margin-left: 0.5rem;
}
.meeting-emojis {
  font-size: 1.5rem;
  color: #ffb368;
  margin-left: 0.5rem;
}

/* Main Content Layout */
.main-content {
  display: flex;
  padding: 2rem;
}

/* Kurse: linkes Drittel in eigenem Kasten */
.courses-box {
  width: 33%;
  padding: 1rem;
  border: 1px solid #004c97;
  margin-right: 2rem;
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
  color: #004c97;
}

/* Lernpfade: restliche Breite */
.learning-paths {
  flex-grow: 1;
  background-color: #ffffff;
  color: #004c97;
}

/* Listen-Stile */
.course-list,
.learningpath-list,
.course-list-inside {
  list-style-type: none;
  padding-left: 0;
  text-align: left;
}

.course-list li,
.learningpath-list li,
.course-list-inside li {
  margin-bottom: 1rem;
  padding: 0.5rem;
  border-bottom: 1px solid #004c97;
}

/* Statistik-Grafik */
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
  border: 1px solid #004c97;
  border-radius: 4px;
  margin-right: 0.5rem;
  color: #004c97;
}
.target-input button {
  padding: 0.25rem 0.5rem;
  background-color: #004c97;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* Chat Overlay Button */
.chat-overlay {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
}

.chat-btn {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background-color: #004c97;
  color: #ffffff;
  font-size: 2rem;
  border: none;
  cursor: pointer;
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.2);
}

/* Chatfenster */
.chat-window {
  position: fixed;
  bottom: 90px;
  right: 1rem;
  width: 300px;
  background: #ffffff;
  border: 1px solid #004c97;
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  color: #004c97;
}
.chat-header {
  background-color: #004c97;
  color: #ffffff;
  padding: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.assistant-portrait {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 0.5rem;
}
.chat-header img {
  object-fit: cover;
}
.close-btn {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 1.2rem;
  cursor: pointer;
}
.chat-body {
  flex-grow: 1;
  padding: 0.5rem;
  overflow-y: auto;
  font-size: 0.9rem;
}
.chat-message {
  margin-bottom: 0.5rem;
}
.timestamp {
  font-size: 0.75rem;
  color: #555;
  margin-right: 0.25rem;
}
.message-content {
  font-size: 0.9rem;
}
.chat-footer {
  display: flex;
  padding: 0.5rem;
  border-top: 1px solid #004c97;
}
.chat-footer input {
  flex-grow: 1;
  padding: 0.5rem;
  border: 1px solid #004c97;
  border-radius: 4px;
  color: #004c97;
}
.chat-footer button {
  margin-left: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #004c97;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
