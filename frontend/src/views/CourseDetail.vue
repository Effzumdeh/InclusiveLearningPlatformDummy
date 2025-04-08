<template>
  <div class="course-detail">
    <button class="back-button" @click="goBack">Zurück</button>
    <h2>{{ course.title }}</h2>
    <p>{{ course.description }}</p>
    <!-- Platzhalterinhalte -->
    <div class="placeholder-content">
      <p>Hier folgen weitere Informationen und Inhalte zum Kurs.</p>
      <p>Weitere Platzhaltertexte, die den Kurstext erweitern.</p>
    </div>
    <!-- Kommentarsektion -->
    <div class="comments-section">
      <h3>Kommentare</h3>
      <ul class="comment-list">
        <li v-for="comment in comments" :key="comment.id">
          <div class="comment-header">
            <span class="comment-timestamp">{{ formatTimestamp(comment.timestamp) }}</span>
          </div>
          <div class="comment-content">{{ comment.content }}</div>
        </li>
      </ul>
      <div class="comment-input">
        <input type="text" v-model="newComment" placeholder="Schreibe einen Kommentar..." @keyup.enter="postComment" />
        <button @click="postComment">Posten</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

export default {
  name: "CourseDetail",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const courseId = route.params.courseId;
    const course = ref({});
    const comments = ref([]);
    const newComment = ref("");

    const fetchCourse = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/courses/${courseId}`);
        course.value = await response.json();
      } catch (error) {
        console.error("Fehler beim Abrufen des Kurses:", error);
      }
    };

    const fetchComments = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/comments/${courseId}`);
        comments.value = await response.json();
      } catch (error) {
        console.error("Fehler beim Abrufen der Kommentare:", error);
      }
    };

    const postComment = async () => {
      if (!newComment.value.trim()) return;
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/comments/${courseId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content: newComment.value }),
        });
        const postedComment = await response.json();
        comments.value.push(postedComment);
        newComment.value = "";
      } catch (error) {
        console.error("Fehler beim Posten des Kommentars:", error);
      }
    };

    const goBack = () => {
      router.back();
    };

    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleString();
    };

    onMounted(() => {
      fetchCourse();
      fetchComments();
    });

    return {
      course,
      comments,
      newComment,
      postComment,
      goBack,
      formatTimestamp,
    };
  },
};
</script>

<style scoped>
.course-detail {
  padding: 2rem;
}
.back-button {
  margin-bottom: 1rem;
  padding: 0.5rem 1rem;
  background-color: #004c97;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.placeholder-content {
  margin: 2rem 0;
  padding: 1rem;
  border: 1px solid #004c97;
  border-radius: 4px;
  background-color: #f5f5f5;
}
.comments-section {
  margin-top: 2rem;
}
.comment-list {
  list-style: none;
  padding: 0;
}
.comment-list li {
  margin-bottom: 1rem;
  padding: 0.5rem;
  border-bottom: 1px solid #004c97;
}
.comment-header {
  font-size: 0.8rem;
  color: #555;
  margin-bottom: 0.25rem;
}
.comment-input {
  display: flex;
  margin-top: 1rem;
}
.comment-input input {
  flex-grow: 1;
  padding: 0.5rem;
  border: 1px solid #004c97;
  border-radius: 4px;
}
.comment-input button {
  margin-left: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #004c97;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>