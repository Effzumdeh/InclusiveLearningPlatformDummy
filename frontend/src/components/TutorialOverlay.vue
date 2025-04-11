<template>
  <div class="tutorial-overlay">
    <div class="tutorial-content">
      <p>{{ currentStep.message }}</p>
      <button @click="nextStep">Weiter</button>
    </div>
  </div>
</template>

<script>
import { computed, watch, onMounted } from "vue";
import { useTutorialStore } from "../store/tutorial";
export default {
  name: "TutorialOverlay",
  emits: ["finish"],
  setup(props, { emit }) {
    const tutorialStore = useTutorialStore();
    const currentStep = computed(() => tutorialStore.steps[tutorialStore.currentStep] || {});
    
    const highlightElement = () => {
      document.querySelectorAll('.tutorial-highlight').forEach(el => {
        el.classList.remove('tutorial-highlight');
      });
      if (currentStep.value.selector) {
        const target = document.querySelector(currentStep.value.selector);
        if (target) {
          target.classList.add('tutorial-highlight');
        }
      }
    };

    const nextStep = () => {
      if (tutorialStore.currentStep < tutorialStore.steps.length - 1) {
        tutorialStore.nextStep();
        highlightElement();
      } else {
        document.querySelectorAll('.tutorial-highlight').forEach(el => {
          el.classList.remove('tutorial-highlight');
        });
        emit("finish");
      }
    };

    onMounted(() => {
      highlightElement();
    });

    watch(() => tutorialStore.currentStep, () => {
      highlightElement();
    });

    return { currentStep, nextStep };
  },
};
</script>

<style scoped>
.tutorial-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.tutorial-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  text-align: center;
}
.tutorial-content button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #004c97;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>