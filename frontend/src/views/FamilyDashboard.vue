<template>
  <div class="family-dashboard">
    <h2>Für Angehörige/Lehrkräfte</h2>

    <!-- Kind-Konto anlegen -->
    <section>
      <h3>Kind-Konto anlegen</h3>
      <form @submit.prevent="createChild">
        <input v-model="newChild.username" placeholder="Nutzername" required />
        <input v-model="newChild.password" placeholder="Passwort" type="password" required />
        <button type="submit">Anlegen</button>
      </form>
    </section>

    <!-- Liste der Kind-Konten -->
    <section>
      <h3>Verwaltete Kind-Konten</h3>
      <table>
        <thead>
          <tr>
            <th>Nutzername</th>
            <th>Heute (Minuten)</th>
            <th>Ø 7 Tage</th>
            <th>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ch in children" :key="ch.id">
            <td>{{ ch.username }}</td>
            <td>{{ ch.minutes_today }}</td>
            <td>{{ ch.average_last_7_days }}</td>
            <td>
              <button @click="openCourses(ch)">Kurse verwalten</button>
              <button @click="openSettings(ch)">Einstellungen</button>
              <button @click="convert(ch.id)">In reguläres Konto umwandeln</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Kurse verwalten für ausgewähltes Kind -->
    <section v-if="selectedChild" class="manage-courses">
      <h3>Kurse verwalten für {{ selectedChild.username }}</h3>
      <table>
        <thead>
          <tr>
            <th>Titel</th>
            <th>Beschreibung</th>
            <th>Aktion</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in allCourses" :key="c.id">
            <td>{{ c.title }}</td>
            <td>{{ c.short_description }}</td>
            <td>
              <button
                v-if="childEnrolledIds.has(c.id)"
                @click="unenrollChild(c.id)"
              >
                Abmelden
              </button>
              <button
                v-else
                @click="enrollChild(c.id)"
              >
                Belegen
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <button @click="closeCourses">Schließen</button>
    </section>

    <!-- Einstellungen bearbeiten Modal -->
    <div v-if="settingsOpen" class="modal">
      <div class="modal-content">
        <h3>Einstellungen für {{ settingsChild.username }}</h3>
        <div class="checkbox-group">
          <input type="checkbox" id="chat" v-model="childSettings.show_chat" />
          <label for="chat">KI-Chat anzeigen</label>
        </div>
        <div class="checkbox-group">
          <input type="checkbox" id="stats" v-model="childSettings.show_stats" />
          <label for="stats">Lernstatistiken anzeigen</label>
        </div>
        <div class="checkbox-group">
          <input type="checkbox" id="comments" v-model="childSettings.show_comments" />
          <label for="comments">Kommentare anzeigen</label>
        </div>
        <button @click="saveSettings">Speichern</button>
        <button @click="closeSettings">Abbrechen</button>
      </div>
    </div>

    <!-- Hilfreiche Materialien -->
    <section>
      <h3>Hilfreiche Materialien</h3>
      <button @click="showTips = true">Tipps & Empfehlungen</button>
      <div v-if="showTips" class="modal">
        <div class="modal-content">
          <h4>Empfehlungen für Angehörige</h4>
          <p>
            (Dummy-Text) Studien zeigen, dass regelmäßige Reflexionsgespräche über
            Lernerfolge und kleine Belohnungen die Motivation der Lernenden deutlich
            steigern. Achten Sie auf Pausen und abwechslungsreiche Aufgabenformate.
          </p>
          <button @click="showTips = false">Schließen</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../store/auth";

export default {
  name: "FamilyDashboard",
  setup() {
    const authStore = useAuthStore();
    const children = ref([]);
    const newChild = ref({ username: "", password: "" });
    const showTips = ref(false);

    const selectedChild = ref(null);
    const allCourses = ref([]);
    const childEnrolledIds = ref(new Set());

    const settingsOpen = ref(false);
    const settingsChild = ref(null);
    const childSettings = ref({
      show_chat: true,
      show_stats: true,
      show_comments: true
    });

    // Load managed children
    const loadChildren = async () => {
      const res = await fetch("http://127.0.0.1:8000/api/guardian/children", {
        headers: { Authorization: "Bearer " + authStore.token }
      });
      children.value = await res.json();
    };

    // Create a new child account
    const createChild = async () => {
      await fetch("http://127.0.0.1:8000/api/guardian/children", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + authStore.token
        },
        body: JSON.stringify(newChild.value)
      });
      newChild.value.username = "";
      newChild.value.password = "";
      await loadChildren();
    };

    // Convert child to regular account
    const convert = async (id) => {
      await fetch(`http://127.0.0.1:8000/api/guardian/children/${id}/convert`, {
        method: "POST",
        headers: { Authorization: "Bearer " + authStore.token }
      });
      await loadChildren();
    };

    // Open course management for a child
    const openCourses = async (child) => {
      selectedChild.value = child;
      await loadAllCourses();
      await loadChildEnrolled();
    };
    const closeCourses = () => {
      selectedChild.value = null;
      childEnrolledIds.value.clear();
    };

    // Fetch all courses
    const loadAllCourses = async () => {
      const res = await fetch("http://127.0.0.1:8000/api/courses", {
        headers: { Authorization: "Bearer " + authStore.token }
      });
      allCourses.value = await res.json();
    };

    // Fetch child's enrolled courses
    const loadChildEnrolled = async () => {
      const cid = selectedChild.value.id;
      const res = await fetch(
        `http://127.0.0.1:8000/api/guardian/children/${cid}/courses`,
        { headers: { Authorization: "Bearer " + authStore.token } }
      );
      const list = await res.json();
      childEnrolledIds.value = new Set(list.map((e) => e.course_id));
    };

    // Enroll child in a course
    const enrollChild = async (courseId) => {
      const cid = selectedChild.value.id;
      await fetch(
        `http://127.0.0.1:8000/api/guardian/children/${cid}/courses/${courseId}`,
        {
          method: "POST",
          headers: { Authorization: "Bearer " + authStore.token }
        }
      );
      await loadChildEnrolled();
    };

    // Unenroll child from a course
    const unenrollChild = async (courseId) => {
      const cid = selectedChild.value.id;
      await fetch(
        `http://127.0.0.1:8000/api/guardian/children/${cid}/courses/${courseId}`,
        {
          method: "DELETE",
          headers: { Authorization: "Bearer " + authStore.token }
        }
      );
      await loadChildEnrolled();
    };

    // Open settings modal for child
    const openSettings = async (child) => {
      settingsChild.value = child;
      const res = await fetch(
        `http://127.0.0.1:8000/api/guardian/children/${child.id}/settings`,
        { headers: { Authorization: "Bearer " + authStore.token } }
      );
      const data = await res.json();
      childSettings.value = {
        show_chat: data.show_chat,
        show_stats: data.show_stats,
        show_comments: data.show_comments
      };
      settingsOpen.value = true;
    };

    // Save child settings
    const saveSettings = async () => {
      const cid = settingsChild.value.id;
      await fetch(
        `http://127.0.0.1:8000/api/guardian/children/${cid}/settings`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + authStore.token
          },
          body: JSON.stringify(childSettings.value)
        }
      );
      settingsOpen.value = false;
      await loadChildren();
    };

    const closeSettings = () => {
      settingsOpen.value = false;
    };

    onMounted(loadChildren);

    return {
      children,
      newChild,
      showTips,
      createChild,
      convert,
      selectedChild,
      allCourses,
      childEnrolledIds,
      openCourses,
      closeCourses,
      enrollChild,
      unenrollChild,
      settingsOpen,
      settingsChild,
      childSettings,
      openSettings,
      saveSettings,
      closeSettings
    };
  }
};
</script>

<style scoped>
.family-dashboard {
  padding: 2rem;
}
.family-dashboard table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
.family-dashboard th,
td {
  border: 1px solid #004c97;
  padding: 0.5rem;
  text-align: left;
}
.family-dashboard button {
  margin: 0 0.25rem;
  padding: 0.5rem;
  background-color: #004c97;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.manage-courses {
  margin-top: 2rem;
}
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.modal-content {
  background: white;
  padding: 1rem;
  border-radius: 4px;
  max-width: 400px;
  width: 100%;
}
.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
</style>