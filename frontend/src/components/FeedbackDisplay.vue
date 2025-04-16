<template>
  <div class="feedback-display">
    <h3>Didaktisches Feedback</h3>
    <ul>
      <!-- UDL (Universal Design for Learning) Feedback -->
      <li><strong>UDL:</strong> 
        Stellen Sie sicher, dass alle Lernenden die Möglichkeit haben, in ihrem eigenen Tempo zu lernen. Nutzen Sie visuelle Darstellungen, interaktive Übungen und praxisnahe Beispiele, um das Engagement zu steigern.
      </li>
      
      <!-- ARCS Feedback -->
      <li><strong>ARCS:</strong> 
        <ul>
          <li><strong>Aufmerksamkeit (Attention):</strong> Das Beispiel ist ansprechend und weckt das Interesse der Lernenden durch praktische, leicht verständliche Codebeispiele.</li>
          <li><strong>Relevanz (Relevance):</strong> Das Thema ist besonders relevant für alle, die in Bereichen wie Webentwicklung oder Datenanalyse arbeiten, wo Multithreading häufig zum Einsatz kommt.</li>
          <li><strong>Erfolgszuversicht (Confidence):</strong> Der Code ist einfach und gibt den Lernenden schnelle Erfolgserlebnisse. Zur Steigerung der Erfolgszuversicht sollten mögliche Probleme und Fehlerquellen aufgezeigt werden.</li>
          <li><strong>Zufriedenheit (Satisfaction):</strong> Das Erstellen eines funktionierenden Programms vermittelt ein Gefühl der Zufriedenheit. Weitere Übungen oder Herausforderungen könnten jedoch das Gefühl der Erfüllung verstärken.</li>
        </ul>
      </li>
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