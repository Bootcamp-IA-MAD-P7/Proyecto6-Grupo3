document.addEventListener('DOMContentLoaded', () => {
  const analyzeBtn = document.getElementById('analyzeBtn');
  const inputText = document.getElementById('inputText');
  const resultDiv = document.getElementById('result');
  const resultText = document.getElementById('resultText');

  analyzeBtn.addEventListener('click', async () => {
    const text = inputText.value.trim();

    if (!text) {
      alert('Por favor, ingresa algún texto para analizar.');
      return;
    }

    resultDiv.classList.remove('hidden');
    resultText.textContent = 'Analizando...';

    try {
      // Modifica esta URL según el puerto y endpoint de tu servidor FastAPI/Flask
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: text })
      });

      if (!response.ok) {
        throw new Error('Error en el servidor backend');
      }

      const data = await response.json();
      // Ajusta 'data.category' o 'data.prediction' al formato que retorne tu API
      resultText.textContent = `Resultado: ${data.category || data.prediction || JSON.stringify(data)}`;
    } catch (error) {
      console.error(error);
      resultText.textContent = ' Error al conectar con el backend.';
    }
  });
});