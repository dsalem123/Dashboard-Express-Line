# Instrucciones — Procesamiento Macro Show Hedgeye

## Tarea
Leé `hedgeye_raw.json`, procesá el contenido y escribí el resultado en `hedgeye_data.json`.

## Reglas de transformación
1. Traducí todo al español profesional institucional (wealth management)
2. Eliminá toda atribución de sujeto sin excepción: "Keith said X" → "X" / "McCullough noted Y" → "Y" / "Señaló que Z" → "Z"
3. Títulos de sección: 4-7 palabras, MAYÚSCULAS, analíticos, sin nombres propios
4. Preservá siempre: tickers (TLT, SPX, NVDA...), "Quad N", números, ETFs
5. Campo `resumen` por sección: 1-2 oraciones que sinteticen los puntos clave con su implicación práctica
6. Campo `resumen_ejecutivo` del episodio completo:
   - `tesis`: mensaje macro central del episodio, 1-2 oraciones
   - `contexto`: condiciones de mercado actuales que enmarcan la tesis, 1 oración
   - `insights`: lista de exactamente 3 puntos accionables para el portfolio
   - `conclusion`: implicación concreta para gestión de portfolios, 1 oración

## Estructura de hedgeye_data.json
Copiar del raw sin cambios: `updated`, `bullish`, `bearish`, `macro_show.bullish`, `macro_show.bearish`, `macro_show.date`, `macro_show.notas_pendientes`
Traducir y completar: `macro_show.title`, `macro_show.secciones` (cada una con `titulo`, `puntos`, `resumen`)
Generar: `macro_show.resumen_ejecutivo`
Campos fijos: `macro_show.bullets = []`, `macro_show.resumen_ai = null`, `error = null`

## Ejemplo de estructura final
```json
{
  "updated": "YYYY-MM-DD HH:MM",
  "bullish": [...],
  "bearish": [...],
  "macro_show": {
    "title": "Título traducido del episodio",
    "date": "...",
    "bullets": [],
    "secciones": [
      {
        "titulo": "TITULO EN MAYUSCULAS",
        "puntos": ["punto traducido 1", "punto traducido 2"],
        "resumen": "Síntesis de 1-2 oraciones con implicación práctica."
      }
    ],
    "bullish": ["TICKER1", "TICKER2"],
    "bearish": ["TICKER3"],
    "resumen_ejecutivo": {
      "tesis": "Mensaje macro central del episodio.",
      "contexto": "Condiciones de mercado actuales.",
      "insights": ["Punto accionable 1", "Punto accionable 2", "Punto accionable 3"],
      "conclusion": "Implicación concreta para portfolios."
    },
    "resumen_ai": null,
    "notas_pendientes": false
  },
  "error": null
}
```

## IMPORTANTE
- Escribí SÓLO el archivo `hedgeye_data.json`
- No ejecutes ningún otro comando
- No hagas git push
