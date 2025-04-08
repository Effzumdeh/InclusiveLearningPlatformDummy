import { defineStore } from "pinia";

export const useCourseEditorStore = defineStore("courseEditor", {
  state: () => ({
    title: "",
    shortDescription: "",
    courseContent: "",
    editingCourseId: null,
  }),
  actions: {
    saveToLocal() {
      try {
        localStorage.setItem("courseEditor", JSON.stringify(this.$state));
      } catch (e) {
        console.warn("Couldn't save course editor state", e);
      }
    },
    loadFromLocal() {
      const savedState = localStorage.getItem("courseEditor");
      if (savedState) {
        Object.assign(this.$state, JSON.parse(savedState));
      }
    },
    reset() {
      this.title = "";
      this.shortDescription = "";
      this.courseContent = "";
      this.editingCourseId = null;
      this.saveToLocal();
    },
  },
});