<template>
  <div class="app">
    <header>
      <div class="header-buttons" v-if="authStore.token">
        <button class="header-button" @click="logout">Abmelden 🚪</button>
        <button v-if="route.name !== 'Home'" class="header-button" @click="goHome">Zur Hauptseite 🏠</button>
      </div>
      <h1>Willkommen auf der Lernplattform</h1>
    </header>
    <!-- Next meeting banner and chat overlay are hidden on the Login page -->
    <div v-if="!isLoginPage">
      <div class="next-meeting-box">
        <div class="meeting-text">
          Dein nächster Kurstermin findet statt am: {{ meetingStartFull }} – {{ meetingEndFull }}<br />
          Thema: Digitale Diversität
        </div>
        <button class="meeting-button" :disabled="!meetingActive" @click="handleMeetingClick">
          Jetzt der Videokonferenz beitreten <span class="meeting-emojis">📹👥</span>
        </button>
      </div>
      <div class="chat-overlay">
        <button class="chat-btn" @click="toggleChat">?</button>
        <div v-if="chatOpen" class="chat-window">
          <div class="chat-header">
            <img src="./assets/assistant.jpg" alt="Portrait von Steve" class="assistant-portrait" />
            <span>Steve (KI-Assistent)</span>
            <button class="close-btn" @click="toggleChat">&times;</button>
          </div>
          <div class="chat-body">
            <div v-for="msg in chatMessages" :key="msg.timestamp" class="chat-message">
              <span class="timestamp">{{ msg.timestamp }}</span> - {{ msg.text }}
            </div>
          </div>
          <div class="chat-footer">
            <input type="text" placeholder="Nachricht eingeben..." v-model="chatInput" @keyup.enter="sendMessage" />
            <button class="mic-btn" @click="toggleSpeechRecognition">
              <span v-if="isListening">🛑</span>
              <span v-else>🎤</span>
            </button>
            <button @click="sendMessage">Senden</button>
          </div>
        </div>
      </div>
    </div>
    <router-view />
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "./store/auth";
import { useRouter, useRoute } from "vue-router";
export default {
  name: "App",
  setup() {
    const authStore = useAuthStore();
    authStore.loadStoredAuth();
    const router = useRouter();
    const route = useRoute();

    // Determine if the current route is the Login/Register page.
    const isLoginPage = computed(() => route.name === "LoginRegister");

    // Chat functionality
    const chatOpen = ref(false);
    const chatInput = ref("");
    const chatMessages = ref([]);
    const toggleChat = () => {
      chatOpen.value = !chatOpen.value;
      if (chatOpen.value && chatMessages.value.length === 0) {
        const greeting =
          "Hallo, mein Name ist Steve. Du hast Fragen zur Bedienung dieser Lernplattform oder Fragen zum aktuellen Inhalt? Ich helfe dir gerne weiter.";
        addChatMessage(greeting);
      }
    };
    const sendMessage = () => {
      if (chatInput.value.trim() !== "") {
        addChatMessage(chatInput.value.trim());
        chatInput.value = "";
        setTimeout(() => {
          const autoResponse =
            "Klicke hierzu oben im Menü auf 'Profil'. Solltest du dort nicht fündig werden, kontaktiere mich gerne erneut.";
          addChatMessage(autoResponse);
        }, 3000);
      }
    };
    const addChatMessage = (text) => {
      const timestamp = new Date().toLocaleTimeString();
      chatMessages.value.push({ text, timestamp });
    };

    // Meeting functionality
    const meetingStartTime = ref(new Date(Date.now() + 2 * 60 * 1000));
    const meetingEndTime = ref(new Date(meetingStartTime.value.getTime() + 60 * 60 * 1000));
    const getDayLabel = (dateObj) => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      const dayAfter = new Date(today);
      dayAfter.setDate(dayAfter.getDate() + 2);
      const compare = new Date(dateObj);
      compare.setHours(0, 0, 0, 0);
      if (compare.getTime() === today.getTime()) return "(heute)";
      if (compare.getTime() === tomorrow.getTime()) return "(morgen)";
      if (compare.getTime() === dayAfter.getTime()) return "(übermorgen)";
      return "";
    };
    const meetingStartFull = computed(() => {
      const datePart = meetingStartTime.value.toLocaleDateString([], { day: "numeric", month: "long", year: "numeric" });
      const timePart = meetingStartTime.value.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      return `${datePart} ${timePart} ${getDayLabel(meetingStartTime.value)}`;
    });
    const meetingEndFull = computed(() => {
      const datePart = meetingEndTime.value.toLocaleDateString([], { day: "numeric", month: "long", year: "numeric" });
      const timePart = meetingEndTime.value.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
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

    // Header actions
    const logout = () => {
      authStore.logout();
      router.push({ name: "LoginRegister" });
    };
    const goHome = () => {
      router.push({ name: "Home" });
    };

    // Speech recognition
    const isListening = ref(false);
    let recognition = null;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognition = new SpeechRecognition();
      recognition.lang = "de-DE";
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;
      recognition.onresult = (event) => {
        if (event.results && event.results[0] && event.results[0][0]) {
          chatInput.value = event.results[0][0].transcript;
        }
      };
      recognition.onend = () => {
        isListening.value = false;
      };
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

    return {
      authStore,
      router,
      route,
      isLoginPage,
      chatOpen,
      chatInput,
      chatMessages,
      toggleChat,
      sendMessage,
      meetingStartFull,
      meetingEndFull,
      meetingActive,
      handleMeetingClick,
      isListening,
      toggleSpeechRecognition,
      logout,
      goHome,
    };
  },
};
</script>

<style scoped>
.app {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  color: #004c97;
  background-color: #ffffff;
}
header {
  background-color: #004c97;
  padding: 1rem;
  color: #ffffff;
  text-align: center;
  position: relative;
}
.header-buttons {
  position: absolute;
  left: 1rem;
  top: 1rem;
  display: flex;
  gap: 0.5rem;
}
.header-buttons button {
  background-color: #007700;
  border: none;
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}
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
.meeting-button:disabled:hover {
  cursor: not-allowed;
}
.meeting-emojis {
  font-size: 1.5rem;
  color: #ffb368;
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
  background-color: #004c97;
  color: #ffffff;
  font-size: 2rem;
  border: none;
  cursor: pointer;
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.2);
}
.chat-window {
  position: fixed;
  bottom: 90px;
  right: 1rem;
  width: 360px;
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
.mic-btn {
  padding: 0.5rem;
  background-color: #eeeeee;
  border: 1px solid #004c97;
  border-radius: 4px;
  cursor: pointer;
}
</style>