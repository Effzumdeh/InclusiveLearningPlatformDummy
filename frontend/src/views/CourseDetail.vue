<template>
  <div class="course-detail">
    <button class="back-button" @click="goBack">Zurück</button>
    <h2>{{ course.title }}</h2>
    <p>{{ course.short_description }}</p>
    <div class="course-content" v-html="course.course_content"></div>

    <QuizComponent v-if="course && course.id" :courseId="course.id" />

    <div class="comments-section" v-if="authStore.user && authStore.user.show_comments">
      <h3>Kommentare</h3>
      <ul class="comment-list">
        <li v-for="comment in comments" :key="comment.id">
          <div class="comment-header">
            <span class="comment-timestamp">{{ formatTimestamp(comment.timestamp) }}</span>
            <router-link
              :to="{ name: 'ProfileView', params: { user_id: comment.user_id } }"
              class="comment-author"
            >
              {{ comment.username }}
            </router-link>
          </div>
          <div class="comment-content">{{ comment.content }}</div>
          <ul class="replies" v-if="comment.replies && comment.replies.length">
            <li v-for="reply in comment.replies" :key="reply.id">
              <div class="comment-header">
                <span class="comment-timestamp">{{ formatTimestamp(reply.timestamp) }}</span>
                <router-link
                  :to="{ name: 'ProfileView', params: { user_id: reply.user_id } }"
                  class="comment-author"
                >
                  {{ reply.username }}
                </router-link>
              </div>
              <div class="comment-content">{{ reply.content }}</div>
            </li>
          </ul>
        </li>
      </ul>
      <div class="comment-input">
        <input
          type="text"
          v-model="newComment"
          placeholder="Schreibe einen Kommentar..."
          @keyup.enter="postComment"
          aria-label="Kommentar eingeben"
        />
        <button @click="postComment">Posten</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import QuizComponent from "../components/QuizComponent.vue";

export default {
  name: "CourseDetail",
  components: { QuizComponent },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const authStore = useAuthStore();
    const courseId = route.params.courseId;
    const course = ref({});
    const comments = ref([]);
    const newComment = ref("");

    const fetchCourse = async () => {
      try {
        const headers = {};
        if (authStore.token) {
          headers["Authorization"] = "Bearer " + authStore.token;
        }
        const res = await fetch(
          `http://127.0.0.1:8000/api/courses/${courseId}`,
          { headers }
        );
        course.value = await res.json();
      } catch (err) {
        console.error("Fehler beim Abrufen des Kurses:", err);
      }
    };

    const fetchComments = async () => {
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/api/comments/${courseId}`
        );
        comments.value = await res.json();
      } catch (err) {
        console.error("Fehler beim Abrufen der Kommentare:", err);
      }
    };

    const postComment = async () => {
      if (!newComment.value.trim()) return;
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/api/comments/${courseId}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: "Bearer " + authStore.token,
            },
            body: JSON.stringify({ content: newComment.value }),
          }
        );
        if (!res.ok) throw new Error("Kommentar konnte nicht gepostet werden.");
        const posted = await res.json();
        comments.value.push(posted);
        newComment.value = "";
      } catch (err) {
        console.error("Fehler beim Posten des Kommentars:", err);
      }
    };

    const goBack = () => router.back();

    const formatTimestamp = (ts) => {
      const d = new Date(ts);
      return isNaN(d.getTime()) ? "" : d.toLocaleString();
    };

    onMounted(() => {
      fetchCourse();
      fetchComments();
    });

    return {
      authStore,
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
.course-content {
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
  padding-left: 0;
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
  display: flex;
  gap: 0.5rem;
}
.comment-author {
  font-weight: bold;
  color: #004c97;
  text-decoration: none;
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
.replies {
  list-style: none;
  margin-left: 1rem;
  padding-left: 0.5rem;
  border-left: 1px solid #004c97;
}
</style>