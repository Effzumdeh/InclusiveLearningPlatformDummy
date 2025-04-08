<template>
  <div class="feedback-display">
    <h3>Didaktisches Feedback</h3>
    <ul>
      <li><strong>UDL:</strong> {{ feedback.UDL }}</li>
      <li>
        <strong>Learning First Principles:</strong>
        {{ feedback.LearningFirstPrinciples }}
      </li>
      <li><strong>ARCS:</strong> {{ feedback.ARCS }}</li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "FeedbackDisplay",
  props: {
    feedback: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style scoped>
.feedback-display {
  border: 1px solid #004c97;
  padding: 1rem;
  margin-top: 1rem;
  border-radius: 4px;
  background-color: #e6f0ff;
}
.feedback-display h3 {
  margin-top: 0;
}
</style>