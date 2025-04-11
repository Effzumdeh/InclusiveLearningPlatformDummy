<template>
  <div class="quiz-component" v-if="loading === false">
    <div v-if="currentQuestion">
      <h3>Quizfrage:</h3>
      <p>{{ currentQuestion.question_text }}</p>
      <div class="options">
        <button
          v-for="option in options"
          :key="option.number"
          :class="{'correct': selected === option.number && answered && isCorrect, 'incorrect': selected === option.number && answered && !isCorrect}"
          @click="submitAnswer(option.number)"
          :disabled="answered"
        >
          {{ option.text }}
        </button>
      </div>
    </div>
    <div v-else>
      <div v-if="allCorrect">
        <p>Herzlichen Glückwunsch, Sie haben alle Quizfragen korrekt beantwortet!</p>
        <button @click="downloadCertificate">Zertifikat herunterladen</button>
      </div>
      <div v-else>
        <p>Falsche Quizfragen – möchten Sie es erneut versuchen?</p>
        <button @click="resetQuizAttempt">Quiz wiederholen</button>
      </div>
    </div>
  </div>
  <div v-else>
    <p>Quiz wird geladen...</p>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
export default {
  name: "QuizComponent",
  props: {
    courseId: {
      type: [String, Number],
      required: true
    }
  },
  setup(props) {
    const loading = ref(true);
    const questions = ref([]);
    const currentIndex = ref(0);
    const currentQuestion = ref(null);
    const selected = ref(null);
    const answered = ref(false);
    const isCorrect = ref(false);
    const options = ref([]);
    const allCorrect = ref(true); // = true, solange noch keine falsche Antwort

    const fetchQuestions = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/courses/${props.courseId}/quiz-questions`, {
          headers: {
            "Authorization": "Bearer " + localStorage.getItem("token")
          }
        });
        questions.value = await response.json();
        if (questions.value.length > 0) {
          currentIndex.value = 0;
          allCorrect.value = true;
          currentQuestion.value = questions.value[currentIndex.value];
          prepareOptions();
        }
      } catch (error) {
        console.error("Fehler beim Laden der Quizfragen:", error);
      } finally {
        loading.value = false;
      }
    };

    const prepareOptions = () => {
      if (currentQuestion.value) {
        options.value = [
          { number: 1, text: currentQuestion.value.option1 },
          { number: 2, text: currentQuestion.value.option2 },
          { number: 3, text: currentQuestion.value.option3 },
          { number: 4, text: currentQuestion.value.option4 }
        ];
      }
    };

    const submitAnswer = async (optionNumber) => {
      if (answered.value) return;
      selected.value = optionNumber;
      answered.value = true;
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/courses/${props.courseId}/quiz/${currentQuestion.value.id}/response`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + localStorage.getItem("token")
          },
          body: JSON.stringify({ selected_option: optionNumber })
        });
        const data = await response.json();
        isCorrect.value = data.correct;
        if (!data.correct) {
          allCorrect.value = false;
        }
      } catch (error) {
        console.error("Fehler beim Absenden der Antwort:", error);
      }
      setTimeout(() => {
        currentIndex.value++;
        if (currentIndex.value < questions.value.length) {
          currentQuestion.value = questions.value[currentIndex.value];
          prepareOptions();
          selected.value = null;
          answered.value = false;
          isCorrect.value = false;
        } else {
          currentQuestion.value = null;
        }
      }, 1500);
    };

    const resetQuizAttempt = async () => {
      loading.value = true;
      await fetchQuestions();
    };

    const downloadCertificate = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/courses/${props.courseId}/certificate`, {
          headers: { "Authorization": "Bearer " + localStorage.getItem("token") }
        });
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "Zertifikat.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();
      } catch (error) {
        console.error("Fehler beim Herunterladen des Zertifikats:", error);
      }
    };

    onMounted(async () => {
      await fetchQuestions();
    });

    return {
      loading,
      currentQuestion,
      options,
      submitAnswer,
      selected,
      answered,
      isCorrect,
      downloadCertificate,
      allCorrect,
      resetQuizAttempt
    };
  }
};
</script>

<style scoped>
.quiz-component {
  margin: 2rem 0;
  padding: 1rem;
  border: 1px solid #004c97;
  border-radius: 4px;
}
.options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.options button {
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #004c97;
  color: white;
  transition: background-color 0.3s;
}
.options button.correct {
  background-color: green;
}
.options button.incorrect {
  background-color: red;
}
</style>