"""
Módulo encargado de realizar la inferencia del modelo de Machine Learning.

Este archivo actúa como puente entre la API y el modelo entrenado. Su función
es cargar el vectorizador TF-IDF y el modelo previamente entrenados, transformar
los fragmentos de texto recibidos en características numéricas y obtener las
probabilidades de predicción para cada categoría.

Responsabilidades:
- Cargar el vectorizador almacenado en la carpeta artifacts.
- Cargar el modelo entrenado una única vez al iniciar la aplicación.
- Vectorizar los fragmentos de texto recibidos.
- Ejecutar la inferencia mediante el modelo.
- Devolver las probabilidades que serán utilizadas por analyze.py para
  construir la respuesta de la API.

Este módulo no realiza entrenamiento, ajuste de hiperparámetros ni cálculo de
métricas. Su única responsabilidad es ejecutar predicciones utilizando un
modelo previamente entrenado, permitiendo además sustituir el modelo en el
futuro sin modificar el resto del backend.
"""