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
        <button type="button" @click="simulateDidactic()">Didaktische Prüfung</button>
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

    <!-- Neuer Abschnitt: Quizfragenverwaltung -->
    <h3>Quizfragen Verwaltung</h3>
    <div v-if="store.editingCourseId">
      <div class="quiz-form">
        <label for="quizQuestion">Frage:</label>
        <input id="quizQuestion" type="text" v-model="newQuizQuestion.question_text" />

        <label for="option1">Option 1:</label>
        <input id="option1" type="text" v-model="newQuizQuestion.option1" />

        <label for="option2">Option 2:</label>
        <input id="option2" type="text" v-model="newQuizQuestion.option2" />

        <label for="option3">Option 3:</label>
        <input id="option3" type="text" v-model="newQuizQuestion.option3" />

        <label for="option4">Option 4:</label>
        <input id="option4" type="text" v-model="newQuizQuestion.option4" />

        <label for="correct_option">Korrekte Option (1-4):</label>
        <input id="correct_option" type="number" min="1" max="4" v-model.number="newQuizQuestion.correct_option" />

        <div class="button-group">
          <button type="button" @click="addQuizQuestion" v-if="!newQuizQuestion.id">Quizfrage hinzufügen</button>
          <button type="button" @click="updateQuizQuestion" v-else>Quizfrage aktualisieren</button>
          <button type="button" @click="resetQuizForm">Formular zurücksetzen</button>
        </div>
      </div>
      <div class="quiz-list">
        <h4>Bestehende Quizfragen</h4>
        <table>
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
                <button @click="editQuizQuestion(q)">Bearbeiten</button>
                <button @click="deleteQuizQuestion(q.id)">Löschen</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from "vue";
import { useCourseEditorStore } from "../store/courseEditor";
import CoursePreview from "../components/CoursePreview.vue";
import FeedbackDisplay from "../components/FeedbackDisplay.vue";
import { useRouter } from "vue-router";
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
    const router = useRouter();
    const quillEditor = ref(null);
    let quillInstance = null;
    const errorMessage = ref("");
    const feedback = ref(null);
    const courses = ref([]);
    const originalState = ref({
      title: "",
      shortDescription: "",
      courseContent: "",
    });

    // Quizfragenverwaltung
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
        const response = await fetch("http://127.0.0.1:8000/api/courses");
        courses.value = await response.json();
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

    onMounted(() => {
      quillInstance = new Quill(quillEditor.value, {
        theme: "snow",
        modules: {
          toolbar: [
            ["bold", "italic", "underline"],
            [{ list: "ordered" }, { list: "bullet" }],
            ["link", "image", "video"], // Erweiterung: Video-Button hinzugefügt
          ],
        },
      });
      quillInstance.root.innerHTML = store.courseContent || "";
      quillInstance.on("text-change", () => {
        store.courseContent = quillInstance.root.innerHTML;
        store.saveToLocal();
      });
      fetchCourses();
      fetchQuizQuestions();
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
            feedback.value = null;
            store.reset();
            quillInstance.root.innerHTML = "";
            fetchCourses();
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
        const response = await fetch(`http://127.0.0.1:8000/api/courses/${course.id}`);
        const data = await response.json();
        store.courseContent = data.course_content;
        quillInstance.root.innerHTML = data.course_content;
        store.editingCourseId = course.id;
        originalState.value = {
          title: store.title,
          shortDescription: store.shortDescription,
          courseContent: store.courseContent,
        };
        fetchQuizQuestions();
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

    const unsavedChangesExist = () => {
      return (
        store.title !== originalState.value.title ||
        store.shortDescription !== originalState.value.shortDescription ||
        store.courseContent !== originalState.value.courseContent
      );
    };

    return {
      store,
      quillEditor,
      errorMessage,
      saveCourse,
      simulateDidactic,
      feedback,
      updateStore,
      courses,
      editCourse,
      deleteCourse,
      unsavedChangesExist,
      // Quizfunktionen
      quizQuestions,
      newQuizQuestion,
      addQuizQuestion,
      deleteQuizQuestion,
      editQuizQuestion,
      updateQuizQuestion,
      resetQuizForm,
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
/* Quizfragenverwaltung */
.quiz-form {
  margin-top: 2rem;
  padding: 1rem;
  border: 1px solid #004c97;
  border-radius: 4px;
  background-color: #f9f9f9;
}
.quiz-form label {
  margin-top: 0.5rem;
}
.quiz-form input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #004c97;
  border-radius: 4px;
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
</style>
