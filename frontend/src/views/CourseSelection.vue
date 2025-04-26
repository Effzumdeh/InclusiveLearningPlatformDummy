<template>
  <div class="course-selection">
    <h2>Alle Kurse</h2>
    <table class="selection-table">
      <thead>
        <tr>
          <th>Titel</th>
          <th>Beschreibung</th>
          <th>Aktion</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in courses" :key="c.id">
          <td>{{ c.title }}</td>
          <td>{{ c.short_description }}</td>
          <td>
            <button v-if="c.enrolled" @click="unenroll(c.id)">Abmelden</button>
            <button v-else @click="enroll(c.id)">Kurs belegen</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../store/auth";

export default {
  name: "CourseSelection",
  setup() {
    const courses = ref([]);
    const authStore = useAuthStore();

    const load = async () => {
      const res = await fetch("http://127.0.0.1:8000/api/courses", {
        headers: { Authorization: "Bearer " + authStore.token },
      });
      courses.value = await res.json();
    };

    const enroll = async (id) => {
      await fetch(`http://127.0.0.1:8000/api/user/courses/${id}`, {
        method: "POST",
        headers: { Authorization: "Bearer " + authStore.token },
      });
      await load();
    };

    const unenroll = async (id) => {
      await fetch(`http://127.0.0.1:8000/api/user/courses/${id}`, {
        method: "DELETE",
        headers: { Authorization: "Bearer " + authStore.token },
      });
      await load();
    };

    onMounted(load);

    return { courses, enroll, unenroll };
  },
};
</script>

<style scoped>
.course-selection {
  padding: 2rem;
}
.selection-table {
  width: 100%;
  border-collapse: collapse;
}
.selection-table th,
.selection-table td {
  border: 1px solid #004c97;
  padding: 0.5rem;
  text-align: left;
}
.selection-table button {
  padding: 0.5rem 1rem;
  background-color: #004c97;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>