<template>
  <div class="app">
    <header>
      <nav aria-label="Hauptnavigation">
        <div class="header-buttons" v-if="authStore.token">
          <button class="header-button" @click="logout">Abmelden 🚪</button>
          <button class="header-button" v-if="route.name !== 'Home'" @click="goHome">Zur Hauptseite 🏠</button>
        </div>
      </nav>
      <h1>Willkommen auf der Lernplattform</h1>
    </header>

    <div v-if="!isLoginPage">
      <div class="next-meeting-box" role="region" aria-label="Nächster Termin">
        <div class="meeting-text">
          Dein nächster Kurstermin findet statt am:
          {{ meetingStartFull }} – {{ meetingEndFull }}<br />
          Thema: Digitale Diversität
        </div>
        <button class="meeting-button" :disabled="!meetingActive" @click="handleMeetingClick">
          Jetzt der Videokonferenz beitreten <span class="meeting-emojis">📹👥</span>
        </button>
      </div>

      <div class="chat-overlay" v-if="authStore.user && authStore.user.show_chat" aria-live="polite">
        <button class="chat-btn" @click="toggleChat" aria-haspopup="dialog" :aria-expanded="chatOpen" aria-label="Chat öffnen">?</button>
        <div v-if="chatOpen" class="chat-window" role="dialog" aria-label="Chat-Unterstützung">
          <div class="chat-header">
            <img src="./assets/assistant.jpg" alt="Portrait von Steve" class="assistant-portrait" />
            <span>Steve (KI-Assistent)</span>
            <button class="close-btn" @click="toggleChat" aria-label="Chat schließen">&times;</button>
          </div>
          <div class="chat-body">
            <div v-for="(msg, idx) in chatMessages" :key="idx" class="chat-message">
              <span class="timestamp">{{ msg.timestamp }}</span> - {{ msg.text }}
            </div>
          </div>
          <div class="chat-footer">
            <input type="text" v-model="chatInput" @keyup.enter="sendMessage" aria-label="Chat-Nachricht eingeben" />
            <button class="mic-btn" @click="toggleSpeechRecognition">
              <span v-if="isListening">🛑</span><span v-else>🎤</span>
            </button>
            <button @click="sendMessage">Senden</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showMisclickAlert" class="misclick-alert" role="alertdialog" aria-modal="true" aria-labelledby="misclickTitle">
      <p id="misclickTitle">
        Es scheint, dass Du häufig knapp das Ziel deiner Klicks verfehlst. Möchtest Du die Schriftgröße erhöhen?
      </p>
      <button @click="onMisclickOk">OK</button>
      <button @click="showMisclickAlert = false">Nein</button>
    </div>

    <router-view />

    <TutorialOverlay v-if="tutorialActive" @finish="finishTutorial" />

    <footer id="tutorial-footer">
      <a href="#" @click.prevent="restartTutorial">Tutorial wiederholen</a>
    </footer>

    <FontSizeSlider />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from "vue";
import { useAuthStore } from "./store/auth";
import { useTutorialStore } from "./store/tutorial";
import { useRouter, useRoute } from "vue-router";
import TutorialOverlay from "./components/TutorialOverlay.vue";
import FontSizeSlider from "./components/FontSizeSlider.vue";

export default {
  name: "App",
  components: { TutorialOverlay, FontSizeSlider },
  setup() {
    const authStore = useAuthStore();
    authStore.loadStoredAuth();

    const router = useRouter();
    const route = useRoute();

    const isLoginPage = computed(() => route.name === "LoginRegister");

    const logout = () => {
      authStore.logout();
      router.push({ name: "LoginRegister" });
    };
    const goHome = () => router.push({ name: "Home" });

    const chatOpen = ref(false);
    const chatInput = ref("");
    const chatMessages = ref([]);
    const addChatMessage = (text) => {
      chatMessages.value.push({
        text,
        timestamp: new Date().toLocaleTimeString(),
      });
    };
    const toggleChat = () => {
      chatOpen.value = !chatOpen.value;
      if (chatOpen.value && chatMessages.value.length === 0) {
        addChatMessage(
          "Hallo, mein Name ist Steve. Du hast Fragen zur Bedienung dieser Lernplattform oder Fragen zum aktuellen Inhalt? Ich helfe dir gerne weiter."
        );
      }
    };
    const sendMessage = () => {
      if (!chatInput.value.trim()) return;
      const userMsg = chatInput.value.trim();
      addChatMessage(userMsg);
      chatInput.value = "";
      setTimeout(() => {
        let response =
          "Klicke hierzu oben im Menü auf 'Profil'. Solltest du dort nicht fündig werden, kontaktiere mich gerne erneut.";
        if (userMsg.toLowerCase().includes("mittagessen")) {
          response =
            "Wie wäre es heute mit einer Gemüsepfanne mit Reis und einem frischen Salat?";
        }
        addChatMessage(response);
      }, 1500);
    };

    const isListening = ref(false);
    let recognition;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognition = new SpeechRecognition();
      recognition.lang = "de-DE";
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;
      recognition.onresult = (e) => {
        const t = e.results?.[0]?.[0]?.transcript;
        if (t) chatInput.value = t;
      };
      recognition.onend = () => (isListening.value = false);
    }
    const toggleSpeechRecognition = () => {
      if (!recognition) {
        alert("Spracherkennung wird von diesem Browser nicht unterstützt.");
        return;
      }
      if (!isListening.value) {
        recognition.start();
        isListening.value = true;
      } else {
        recognition.stop();
        isListening.value = false;
      }
    };

    const meetingStartTime = ref(new Date(Date.now() + 2 * 60 * 1000));
    const meetingEndTime = ref(new Date(meetingStartTime.value.getTime() + 60 * 60 * 1000));
    const getDayLabel = (d) => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const tomorrow = new Date(today); tomorrow.setDate(tomorrow.getDate() + 1);
      const dayAfter = new Date(today); dayAfter.setDate(dayAfter.getDate() + 2);
      const cmp = new Date(d); cmp.setHours(0, 0, 0, 0);
      if (cmp.getTime() === today.getTime()) return "(heute)";
      if (cmp.getTime() === tomorrow.getTime()) return "(morgen)";
      if (cmp.getTime() === dayAfter.getTime()) return "(übermorgen)";
      return "";
    };
    const meetingStartFull = computed(() => {
      const datePart = meetingStartTime.value.toLocaleDateString([], {
        day: "numeric", month: "long", year: "numeric"
      });
      const timePart = meetingStartTime.value.toLocaleTimeString([], {
        hour: "2-digit", minute: "2-digit"
      });
      return `${datePart} ${timePart} ${getDayLabel(meetingStartTime.value)}`;
    });
    const meetingEndFull = computed(() => {
      const datePart = meetingEndTime.value.toLocaleDateString([], {
        day: "numeric", month: "long", year: "numeric"
      });
      const timePart = meetingEndTime.value.toLocaleTimeString([], {
        hour: "2-digit", minute: "2-digit"
      });
      return `${datePart} ${timePart}`;
    });
    const meetingActive = ref(false);
    setInterval(() => {
      meetingActive.value = new Date() >= meetingStartTime.value;
    }, 1000);
    const handleMeetingClick = () => {
      if (!meetingActive.value) {
        alert("Der Kurs hat noch nicht begonnen.");
      } else {
        alert("Videokonferenz wird gestartet...");
      }
    };

    const tutorialStore = useTutorialStore();
    const tutorialActive = ref(false);
    watch(() => route.name, (nr) => tutorialStore.setRoute(nr), { immediate: true });
    const fetchTutorialStatus = async () => {
      if (!authStore.token) return;
      try {
        const res = await fetch(
          "http://127.0.0.1:8000/api/user/tutorial-status",
          { headers: { Authorization: "Bearer " + authStore.token } }
        );
        const d = await res.json();
        if (!d.completed) {
          tutorialActive.value = true;
          tutorialStore.startTutorial();
        }
      } catch {
        tutorialActive.value = true;
        tutorialStore.startTutorial();
      }
    };

    const fetchProfileOptions = async () => {
      if (!authStore.token) return;
      try {
        const res = await fetch(
          "http://127.0.0.1:8000/api/user/profile",
          { headers: { Authorization: "Bearer " + authStore.token } }
        );
        const d = await res.json();
        authStore.user = { ...authStore.user, ...d };
        const pref = d.theme_preference || "system";
        const theme =
          pref === "system"
            ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
            : pref;
        document.documentElement.setAttribute("data-theme", theme);
      } catch {}
    };

    const fetchUserProfile = async () => {
      if (!authStore.token) return;
      try {
        const res = await fetch(
          "http://127.0.0.1:8000/api/user/profile",
          { headers: { Authorization: "Bearer " + authStore.token } }
        );
        const data = await res.json();
        authStore.user = { ...authStore.user, ...data };
      } catch (e) {
        console.error("Profil-Laden fehlgeschlagen:", e);
      }
    };

    const showMisclickAlert = ref(false);
    let misclickCount = 0;
    const TH = 3, PROX = 5;
    const onMisclickOk = () => {
      const root = document.documentElement;
      const current = parseFloat(getComputedStyle(root).fontSize) || 16;
      const newSize = current + 2;
      root.style.fontSize = newSize + "px";
      document.cookie = `fontSize=${newSize}; path=/; max-age=${365 * 24 * 60 * 60}`;
      showMisclickAlert.value = false;
    };

    onMounted(() => {
      fetchTutorialStatus();
      fetchProfileOptions();
      fetchUserProfile();
      document.addEventListener("click", (e) => {
        const { clientX: x, clientY: y } = e;
        let near = false;
        document.querySelectorAll("a, button").forEach((el) => {
          const r = el.getBoundingClientRect();
          if (
            !el.contains(e.target) &&
            x >= r.left - PROX && x <= r.right + PROX &&
            y >= r.top - PROX && y <= r.bottom + PROX
          ) near = true;
        });
        if (near && ++misclickCount >= TH) {
          misclickCount = 0;
          showMisclickAlert.value = true;
        }
      });
    });

    watch(
      () => authStore.token,
      (token) => {
        if (token) {
          fetchTutorialStatus();
          fetchProfileOptions();
          fetchUserProfile();
        }
      }
    );

    const restartTutorial = () => {
      tutorialActive.value = true;
      tutorialStore.startTutorial();
    };
    const finishTutorial = async () => {
      tutorialActive.value = false;
      if (!authStore.token) return;
      try {
        await fetch("http://127.0.0.1:8000/api/user/tutorial-status", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + authStore.token
          },
          body: JSON.stringify({ completed: true }),
        });
      } catch {}
    };

    // NEW: Heartbeat to increment learning minutes
    let heartbeatInterval = null;
    const startHeartbeat = () => {
      if (heartbeatInterval) clearInterval(heartbeatInterval);
      heartbeatInterval = setInterval(() => {
        if (!authStore.token) return;
        fetch("http://127.0.0.1:8000/api/user/heartbeat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + authStore.token,
          },
        }).catch(() => {});
      }, 60 * 1000);
    };
    watch(() => authStore.token, (tok) => {
      if (tok) startHeartbeat();
      else if (heartbeatInterval) clearInterval(heartbeatInterval);
    }, { immediate: true });

    return {
      authStore,
      route,
      isLoginPage,
      logout,
      goHome,
      chatOpen,
      chatInput,
      chatMessages,
      toggleChat,
      sendMessage,
      isListening,
      toggleSpeechRecognition,
      meetingStartFull,
      meetingEndFull,
      meetingActive,
      handleMeetingClick,
      tutorialActive,
      restartTutorial,
      finishTutorial,
      showMisclickAlert,
      onMisclickOk
    };
  }
};
</script>

<style>
html[data-theme="light"] {
  --bg: #ffffff;
  --fg: #004c97;
  --btn-bg: #004c97;
  --btn-text: #ffffff;
}
html[data-theme="dark"] {
  --bg: #121212;
  --fg: #e0e0e0;
  --btn-bg: #bb86fc;
  --btn-text: #000000;
}
html[data-theme="high-contrast"] {
  --bg: #000000;
  --fg: #ffff00;
  --btn-bg: #ffff00;
  --btn-text: #000000;
}
body {
  margin: 0;
  background-color: var(--bg) !important;
  color: var(--fg) !important;
  font-family: 'Luciole', sans-serif;
}
header {
  background-color: var(--btn-bg) !important;
  color: var(--btn-text) !important;
  padding: 1rem;
  text-align: center;
}
button,
.header-button,
.meeting-button,
.chat-btn {
  background-color: var(--btn-bg) !important;
  color: var(--btn-text) !important;
  border: none;
  cursor: pointer;
}
:focus {
  outline: 3px solid #ffbf47;
  outline-offset: 2px;
}
.next-meeting-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  border-bottom: 1px solid var(--btn-bg);
}
.meeting-text {
  font-size: 1rem;
}
.meeting-button {
  background-color: #cccccc;
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
  background-color: #004c97;
}
.meeting-button:disabled {
  background-color: #cccccc !important;
  cursor: not-allowed;
}
.meeting-emojis {
  margin-left: 0.5rem;
}
.chat-overlay {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
}
.chat-btn {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  font-size: 2rem;
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.2);
}
.chat-window {
  position: fixed;
  bottom: 90px;
  right: 1rem;
  width: 360px;
  background: var(--bg);
  border: 1px solid var(--btn-bg);
  border-radius: 4px;
  display: flex;
  flex-direction: column;
}
.chat-header {
  background: var(--btn-bg);
  color: var(--btn-text);
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.assistant-portrait {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 0.5rem;
  object-fit: cover;
}
.chat-body {
  padding: 0.5rem;
  overflow-y: auto;
  flex-grow: 1;
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
.chat-footer {
  display: flex;
  padding: 0.5rem;
  border-top: 1px solid var(--btn-bg);
}
.chat-footer input {
  flex-grow: 1;
  padding: 0.5rem;
  border: 1px solid var(--btn-bg);
  border-radius: 4px;
}
.chat-footer button {
  margin-left: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}
.mic-btn {
  padding: 0.5rem;
  background-color: #eeeeee;
  border: 1px solid #004c97;
}
.misclick-alert {
  position: fixed;
  bottom: 100px;
  left: 1rem;
  background: #fffae6;
  border: 2px solid #ffbf47;
  padding: 1rem;
  border-radius: 4px;
  z-index: 2000;
}
.misclick-alert button {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #004c97;
  color: #fff;
  border-radius: 4px;
}
footer {
  text-align: center;
  padding: 1rem;
  border-top: 1px solid var(--btn-bg);
  background: var(--bg);
}
footer a {
  color: var(--btn-bg);
  text-decoration: underline;
  cursor: pointer;
}
.tutorial-highlight {
  box-shadow: 0 0 10px 5px yellow;
  position: relative;
  z-index: 1100;
}
.header-buttons button {
  background-color: #007700 !important;
  border: none !important;
  color: #ffffff !important;
  padding: 0.5rem !important;
  border-radius: 4px !important;
  cursor: pointer !important;
}
</style>