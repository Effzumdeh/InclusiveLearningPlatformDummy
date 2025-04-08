<template>
  <div class="course-editor">
    <h2>Kurseditor</h2>
    <form @submit.prevent="saveCourse(false)">
      <label for="title">Kurstitel*</label>
      <input id="title" type="text" v-model="store.title" @input="updateStore" required />

      <label for="shortDesc">Kurzbeschreibung*</label>
      <input id="shortDesc" type="text" v-model="store.shortDescription" @input="updateStore" required />

      <label for="courseContent">Kursinhalt*</label>
      <div ref="quillEditor" class="quill-editor"></div>

      <div class="error" v-if="errorMessage">{{ errorMessage }}</div>

      <div class="button-group">
        <button type="button" @click="saveCourse(false)">Kurs speichern</button>
        <button type="button" @click="saveCourse(true)">Didaktische Prüfung</button>
      </div>
    </form>

    <CoursePreview 
      :title="store.title" 
      :shortDescription="store.shortDescription" 
      :courseContent="store.courseContent" 
    />

    <FeedbackDisplay v-if="feedback" :feedback="feedback" />

    <h3>Bestehende Kurse</h3>
    <table class="courses-table">
      <thead>
        <tr>
          <th>Kurstitel</th>
          <th>Kurzbeschreibung</th>
          <th>Aktionen</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="course in courses" :key="course.id">
          <td>{{ course.title }}</td>
          <td>{{ course.short_description }}</td>
          <td>
            <button @click="editCourse(course)">Bearbeiten 🖊️</button>
            <button @click="deleteCourse(course.id)">Löschen 🚮</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { ref, onMounted, watch } from "vue";
import { useCourseEditorStore } from "../store/courseEditor";
import CoursePreview from "../components/CoursePreview.vue";
import FeedbackDisplay from "../components/FeedbackDisplay.vue";
import Quill from "quill";
import "quill/dist/quill.snow.css";

export default {
  name: "CourseEditor",
  components: {
    CoursePreview,
    FeedbackDisplay,
  },
  setup() {
    const store = useCourseEditorStore();
    store.loadFromLocal();

    const quillEditor = ref(null);
    let quillInstance = null;
    const errorMessage = ref("");
    const feedback = ref(null);
    const courses = ref([]);

    const fetchCourses = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/courses");
        courses.value = await response.json();
      } catch (error) {
        console.error("Fehler beim Abrufen der Kurse:", error);
      }
    };

    onMounted(() => {
      quillInstance = new Quill(quillEditor.value, {
        theme: "snow",
        modules: {
          toolbar: [
            ["bold", "italic", "underline"],
            [{ list: "ordered" }, { list: "bullet" }],
            ["link", "image"],
          ],
        },
      });
      quillInstance.root.innerHTML = store.courseContent || "";
      quillInstance.on("text-change", () => {
        store.courseContent = quillInstance.root.innerHTML;
        store.saveToLocal();
      });
      fetchCourses();
    });

    watch(() => store.title, store.saveToLocal);
    watch(() => store.shortDescription, store.saveToLocal);
    watch(() => store.courseContent, store.saveToLocal);

    const updateStore = () => {
      store.saveToLocal();
    };

    const saveCourse = async (simulate) => {
      errorMessage.value = "";
      if (!store.title || !store.shortDescription || !store.courseContent?.trim()) {
        errorMessage.value = "Bitte füllen Sie alle Pflichtfelder aus.";
        return;
      }
      const payload = {
        title: store.title,
        short_description: store.shortDescription,
        course_content: store.courseContent,
        didactic_simulation: simulate,
      };

      try {
        let response;
        if (store.editingCourseId) {
          response = await fetch(`http://127.0.0.1:8000/api/courses/${store.editingCourseId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
        } else {
          response = await fetch("http://127.0.0.1:8000/api/courses", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
        }
        const result = await response.json();
        if (!response.ok) {
          errorMessage.value = result.detail || "Fehler beim Speichern des Kurses.";
        } else {
          if (simulate) {
            feedback.value = result.didactic_feedback;
          } else {
            feedback.value = null;
          }
          store.reset();
          quillInstance.root.innerHTML = "";
          fetchCourses();
        }
      } catch (error) {
        errorMessage.value = "Fehler beim Speichern des Kurses.";
      }
    };

    const editCourse = async (course) => {
      store.title = course.title;
      store.shortDescription = course.short_description;
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/courses/${course.id}`);
        const data = await response.json();
        store.courseContent = data.course_content;
        quillInstance.root.innerHTML = data.course_content;
        store.editingCourseId = course.id;
      } catch (error) {
        console.error("Fehler beim Laden des Kurses:", error);
      }
    };

    const deleteCourse = async (courseId) => {
      if (!confirm("Möchten Sie diesen Kurs wirklich löschen?")) return;
      try {
        await fetch(`http://127.0.0.1:8000/api/courses/${courseId}`, {
          method: "DELETE",
        });
        fetchCourses();
        if (store.editingCourseId === courseId) {
          store.reset();
          quillInstance.root.innerHTML = "";
        }
      } catch (error) {
        console.error("Fehler beim Löschen des Kurses:", error);
      }
    };

    return {
      store,
      quillEditor,
      errorMessage,
      saveCourse,
      feedback,
      updateStore,
      courses,
      editCourse,
      deleteCourse,
    };
  },
};
</script>

<style scoped>
.course-editor {
  padding: 2rem;
}
.course-editor form {
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
}
.course-editor label {
  margin-top: 1rem;
}
.course-editor input[type="text"] {
  padding: 0.5rem;
  border: 1px solid #004c97;
  border-radius: 4px;
}
.quill-editor {
  height: 200px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-top: 0.5rem;
}
.error {
  color: red;
  margin-top: 1rem;
}
.button-group {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}
.course-editor button {
  padding: 0.75rem;
  background-color: #004c97;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.courses-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 2rem;
}
.courses-table th,
.courses-table td {
  border: 1px solid #004c97;
  padding: 0.5rem;
  text-align: left;
}
</style>