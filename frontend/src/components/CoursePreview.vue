<template>
  <div class="course-preview">
    <h3>Live-Vorschau</h3>
    <h2>{{ title }}</h2>
    <h4>{{ shortDescription }}</h4>
    <div v-html="safeCourseContent"></div>
  </div>
</template>

<script>
export default {
  name: "CoursePreview",
  props: {
    title: String,
    shortDescription: String,
    courseContent: String,
  },
  computed: {
    safeCourseContent() {
      return this.courseContent || "";
    }
  }
};
</script>

<style scoped>
.course-preview {
  border: 1px solid #004c97;
  padding: 1rem;
  border-radius: 4px;
  background-color: #f9f9f9;
  margin-top: 2rem;
}
.course-preview h3 {
  margin-top: 0;
}
</style>