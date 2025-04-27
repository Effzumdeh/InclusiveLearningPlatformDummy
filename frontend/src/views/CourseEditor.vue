<template>
  <div class="course-editor">
    <h2>Kurseditor</h2>
    <form @submit.prevent="saveCourse(false)">
      <label for="title">Kurstitel*</label>
      <input id="title" type="text" v-model="store.title" @input="updateStore" required :class="themeClass" />

      <label for="shortDesc">Kurzbeschreibung*</label>
      <input id="shortDesc" type="text" v-model="store.shortDescription" @input="updateStore" required :class="themeClass" />

      <label for="courseContent">Kursinhalt*</label>
      <div ref="quillEditor" class="quill-editor" :class="themeClass"></div>

      <div class="error" v-if="errorMessage">{{ errorMessage }}</div>

      <div class="button-group">
        <button type="submit" :class="themeClass">{{ store.editingCourseId ? "Kurs aktualisieren" : "Neuen Kurs speichern" }}</button>
        <button type="button" @click="simulateDidactic" :class="themeClass">Didaktische Prüfung</button>
        <button type="button" v-if="store.editingCourseId" @click="cancelEdit" :class="themeClass">Bearbeitung abbrechen</button>
      </div>
    </form>

    <CoursePreview
      :title="store.title"
      :shortDescription="store.shortDescription"
      :courseContent="store.courseContent || ''"
    />

    <FeedbackDisplay v-if="feedback" :feedback="feedback" />

    <h3>Bestehende Kurse</h3>
    <table class="courses-table" :class="themeClass">
      <thead>
        <tr>
          <th>Kurstitel</th>
          <th>Kurzbeschreibung</th>
          <th>Aktionen</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="course in filteredCourses" :key="course.id">
          <td>{{ course.title }}</td>
          <td>{{ course.short_description }}</td>
          <td>
            <button @click="editCourse(course)" :class="themeClass">Bearbeiten 🖊️</button>
            <button @click="deleteCourse(course.id)" :class="themeClass">Löschen 🚮</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Nutzungs-Statistiken -->
    <h3 v-if="store.editingCourseId">Nutzungsstatistiken</h3>
    <div v-if="analytics && store.editingCourseId" :class="themeClass">
      <p>Einzigartige Öffnungen: {{ analytics.unique_openers }}</p>
      <p>Quiz-Teilnehmer: {{ analytics.unique_quiz_participants }}</p>
      <p>Ø beantwortete Fragen: {{ formatNumber(analytics.avg_questions_answered) }}</p>
      <p>Abgeschlossen (%): {{ formatNumber(analytics.percent_completed) }}%</p>
    </div>

    <!-- Quizfragenverwaltung -->
    <h3 v-if="store.editingCourseId">Quizfragen Verwaltung</h3>
    <div v-if="store.editingCourseId" :class="themeClass">
      <div class="quiz-form">
        <label for="quizQuestion">Frage:</label>
        <input id="quizQuestion" type="text" v-model="newQuizQuestion.question_text" :class="themeClass" />

        <label for="option1">Option 1:</label>
        <input id="option1" type="text" v-model="newQuizQuestion.option1" :class="themeClass" />

        <label for="option2">Option 2:</label>
        <input id="option2" type="text" v-model="newQuizQuestion.option2" :class="themeClass" />

        <label for="option3">Option 3:</label>
        <input id="option3" type="text" v-model="newQuizQuestion.option3" :class="themeClass" />

        <label for="option4">Option 4:</label>
        <input id="option4" type="text" v-model="newQuizQuestion.option4" :class="themeClass" />

        <label for="correct_option">Korrekte Option (1-4):</label>
        <input id="correct_option" type="number" min="1" max="4" v-model.number="newQuizQuestion.correct_option" :class="themeClass" />

        <div class="button-group">
          <button type="button" @click="addQuizQuestion" v-if="!newQuizQuestion.id" :class="themeClass">Quizfrage hinzufügen</button>
          <button type="button" @click="updateQuizQuestion" v-else :class="themeClass">Quizfrage aktualisieren</button>
          <button type="button" @click="resetQuizForm" :class="themeClass">Formular zurücksetzen</button>
        </div>
      </div>
      <div class="quiz-list">
        <h4>Bestehende Quizfragen</h4>
        <table :class="themeClass">
          <thead>
            <tr>
              <th>Frage</th>
              <th>Option 1</th>
              <th>Option 2</th>
              <th>Option 3</th>
              <th>Option 4</th>
              <th>Korrekte Option</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in quizQuestions" :key="q.id">
              <td>{{ q.question_text }}</td>
              <td>{{ q.option1 }}</td>
              <td>{{ q.option2 }}</td>
              <td>{{ q.option3 }}</td>
              <td>{{ q.option4 }}</td>
              <td>{{ q.correct_option }}</td>
              <td>
                <button @click="editQuizQuestion(q)" :class="themeClass">Bearbeiten</button>
                <button @click="deleteQuizQuestion(q.id)" :class="themeClass">Löschen</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from "vue";
import { useCourseEditorStore } from "../store/courseEditor";
import { useAuthStore } from "../store/auth";
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
    const authStore = useAuthStore();
    store.loadFromLocal();
    const quillEditor = ref(null);
    let quillInstance = null;
    const errorMessage = ref("");
    const feedback = ref(null);
    const courses = ref([]);
    const analytics = ref(null);
    const originalState = ref({
      title: "",
      shortDescription: "",
      courseContent: "",
    });

    const quizQuestions = ref([]);
    const newQuizQuestion = ref({
      question_text: "",
      option1: "",
      option2: "",
      option3: "",
      option4: "",
      correct_option: 1,
    });

    const fetchCourses = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/courses", {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });
        const allCourses = await response.json();
        const userRole = JSON.parse(atob(localStorage.getItem("token").split('.')[1])).role;
        if (userRole === "Admin") {
          courses.value = allCourses;
        } else if (userRole === "Teacher") {
          courses.value = allCourses;
        } else {
          courses.value = [];
        }
      } catch (error) {
        console.error("Fehler beim Abrufen der Kurse:", error);
      }
    };

    const fetchQuizQuestions = async () => {
      if (store.editingCourseId) {
        try {
          const response = await fetch(`http://127.0.0.1:8000/api/courses/${store.editingCourseId}/quiz-questions/all`, {
            headers: {
              Authorization: "Bearer " + localStorage.getItem("token"),
            },
          });
          quizQuestions.value = await response.json();
        } catch (error) {
          console.error("Fehler beim Laden der Quizfragen:", error);
        }
      } else {
        quizQuestions.value = [];
      }
    };

    const fetchAnalytics = async () => {
      if (!store.editingCourseId) {
        analytics.value = null;
        return;
      }
      try {
        const r = await fetch(`http://127.0.0.1:8000/api/courses/${store.editingCourseId}/analytics`, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });
        analytics.value = await r.json();
      } catch (e) {
        console.error("Analytics-Laden fehlgeschlagen:", e);
      }
    };

    const addQuizQuestion = async () => {
      if (!store.editingCourseId) return;
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/courses/${store.editingCourseId}/quiz-questions`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify(newQuizQuestion.value),
        });
        const result = await response.json();
        if (!response.ok) {
          alert(result.detail || "Fehler beim Hinzufügen der Quizfrage.");
        } else {
          await fetchQuizQuestions();
          resetQuizForm();
        }
      } catch (error) {
        console.error("Fehler beim Hinzufügen der Quizfrage:", error);
      }
    };

    const deleteQuizQuestion = async (questionId) => {
      if (!confirm("Möchten Sie diese Quizfrage wirklich löschen?")) return;
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/quiz-questions/${questionId}`, {
          method: "DELETE",
          headers: { Authorization: "Bearer " + localStorage.getItem("token") },
        });
        if (response.ok) {
          await fetchQuizQuestions();
        } else {
          const errorData = await response.json();
          alert(errorData.detail || "Fehler beim Löschen der Quizfrage.");
        }
      } catch (error) {
        console.error("Fehler beim Löschen der Quizfrage:", error);
      }
    };

    const editQuizQuestion = (question) => {
      newQuizQuestion.value = { ...question };
    };

    const updateQuizQuestion = async () => {
      if (!newQuizQuestion.value.id) return;
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/quiz-questions/${newQuizQuestion.value.id}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify(newQuizQuestion.value),
        });
        if (response.ok) {
          await fetchQuizQuestions();
          resetQuizForm();
        } else {
          const errorData = await response.json();
          alert(errorData.detail || "Fehler beim Aktualisieren der Quizfrage.");
        }
      } catch (error) {
        console.error("Fehler beim Aktualisieren der Quizfrage:", error);
      }
    };

    const resetQuizForm = () => {
      newQuizQuestion.value = {
        question_text: "",
        option1: "",
        option2: "",
        option3: "",
        option4: "",
        correct_option: 1,
      };
    };

    onMounted(async () => {
      quillInstance = new Quill(quillEditor.value, {
        theme: "snow",
        modules: {
          toolbar: [
            ["bold", "italic", "underline"],
            [{ list: "ordered" }, { list: "bullet" }],
            ["link", "image", "video"],
          ],
        },
      });
      quillInstance.root.innerHTML = store.courseContent || "";
      quillInstance.on("text-change", () => {
        store.courseContent = quillInstance.root.innerHTML;
        store.saveToLocal();
      });
      await fetchCourses();
      await fetchQuizQuestions();
      await fetchAnalytics();
      originalState.value = {
        title: store.title,
        shortDescription: store.shortDescription,
        courseContent: store.courseContent,
      };
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
      if (!simulate) {
        const payload = {
          title: store.title,
          short_description: store.shortDescription,
          course_content: store.courseContent,
          didactic_simulation: false,
        };
        try {
          let response;
          if (store.editingCourseId) {
            response = await fetch(`http://127.0.0.1:8000/api/courses/${store.editingCourseId}`, {
              method: "PUT",
              headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + localStorage.getItem("token"),
              },
              body: JSON.stringify(payload),
            });
          } else {
            response = await fetch("http://127.0.0.1:8000/api/courses", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + localStorage.getItem("token"),
              },
              body: JSON.stringify(payload),
            });
          }
          const result = await response.json();
          if (!response.ok) {
            errorMessage.value = result.detail || "Fehler beim Speichern des Kurses.";
          } else {
            feedback.value = null;
            store.reset();
            quillInstance.root.innerHTML = "";
            await fetchCourses();
            originalState.value = { title: "", shortDescription: "", courseContent: "" };
          }
        } catch (error) {
          errorMessage.value = "Fehler beim Speichern des Kurses.";
        }
      }
    };

    const simulateDidactic = () => {
      feedback.value = {
        UDL: "Die Inhalte sollten in alternativen Formaten vorliegen.",
        LearningFirstPrinciples: "Die Grundlagen sollten stärker strukturiert sein.",
        ARCS: "Mehr interaktive Elemente zur Steigerung der Aufmerksamkeit einfügen.",
      };
    };

const editCourse = async (course) => {
  store.title = course.title;
  store.shortDescription = course.short_description;
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/courses/${course.id}`, {
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    });
    const data = await response.json();
    store.courseContent = data.course_content || "";
    quillInstance.root.innerHTML = data.course_content || "";
    store.editingCourseId = course.id;
    originalState.value = {
      title: store.title,
      shortDescription: store.shortDescription,
      courseContent: store.courseContent,
    };
    await fetchQuizQuestions();
    await fetchAnalytics();
  } catch (error) {
    console.error("Fehler beim Laden des Kurses:", error);
  }
};

    const cancelEdit = () => {
      store.reset();
      quillInstance.root.innerHTML = "";
      feedback.value = null;
      analytics.value = null;
      quizQuestions.value = [];
    };

    const deleteCourse = async (courseId) => {
      if (!confirm("Möchten Sie diesen Kurs wirklich löschen?")) return;
      try {
        await fetch(`http://127.0.0.1:8000/api/courses/${courseId}`, {
          method: "DELETE",
          headers: { Authorization: "Bearer " + localStorage.getItem("token") },
        });
        await fetchCourses();
        if (store.editingCourseId === courseId) {
          cancelEdit();
        }
      } catch (error) {
        console.error("Fehler beim Löschen des Kurses:", error);
      }
    };

    const unsavedChangesExist = () => {
      return (
        store.title !== originalState.value.title ||
        store.shortDescription !== originalState.value.shortDescription ||
        store.courseContent !== originalState.value.courseContent
      );
    };

    const filteredCourses = courses;

    const themeClass = computed(() => {
      const pref = authStore.user?.theme_preference || "system";
      let theme = pref === "system" ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light") : pref;
      return `theme-${theme}`;
    });

    const formatNumber = (num) => {
      if (num === undefined || num === null) return "0.00";
      return Number(num).toFixed(2);
    };

    return {
      store,
      authStore,
      quillEditor,
      errorMessage,
      saveCourse,
      simulateDidactic,
      feedback,
      updateStore,
      courses,
      filteredCourses,
      analytics,
      editCourse,
      deleteCourse,
      unsavedChangesExist,
      quizQuestions,
      newQuizQuestion,
      addQuizQuestion,
      deleteQuizQuestion,
      editQuizQuestion,
      updateQuizQuestion,
      resetQuizForm,
      cancelEdit,
      themeClass,
      formatNumber,
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
.course-editor input[type="text"],
.course-editor input[type="number"],
.course-editor textarea,
.quill-editor,
button {
  border-radius: 4px;
  border: 1px solid #004c97;
  padding: 0.5rem;
}
.quill-editor {
  height: 200px;
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
/* Quizfragenverwaltung */
.quiz-form {
  margin-top: 2rem;
  padding: 1rem;
  border: 1px solid #004c97;
  background-color: #f9f9f9;
}
.quiz-form label {
  margin-top: 0.5rem;
}
.quiz-form input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #004c97;
  margin-bottom: 0.5rem;
}
.quiz-list {
  margin-top: 1rem;
}
.quiz-list table {
  width: 100%;
  border-collapse: collapse;
}
.quiz-list th,
.quiz-list td {
  border: 1px solid #004c97;
  padding: 0.5rem;
  text-align: left;
}

/* Theme dark */
.theme-dark input,
.theme-dark select,
.theme-dark textarea,
.theme-dark button,
.theme-dark .quill-editor,
.theme-dark .courses-table {
  background-color: #121212;
  color: #e0e0e0;
  border-color: #bb86fc;
}
.theme-dark button {
  background-color: #bb86fc;
  color: #000;
}

/* Theme high-contrast */
.theme-high-contrast input,
.theme-high-contrast select,
.theme-high-contrast textarea,
.theme-high-contrast button,
.theme-high-contrast .quill-editor,
.theme-high-contrast .courses-table {
  background-color: #000;
  color: #ffff00;
  border-color: #ffff00;
}
.theme-high-contrast button {
  background-color: #ffff00;
  color: #000;
}
</style>