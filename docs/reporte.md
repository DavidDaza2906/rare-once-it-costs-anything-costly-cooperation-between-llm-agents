# [PROJECT TITLE] — andamio contra la plantilla de Apart

> **Esto es un andamio, no un borrador.** La prosa la escribe el equipo — la plantilla lo pide
> explícitamente: *«We strongly encourage that the final version of the submission is primarily written
> by your team.»* Aquí está la estructura exacta de la plantilla, el presupuesto de palabras y **cada
> cifra atada al archivo del que sale**.
>
> `⟦CIFRA: valor — archivo⟧` verificada, se copia tal cual · `⟦PENDIENTE: qué falta — quién⟧` no existe
> todavía · `⟦ESCRIBIR: …⟧` prosa humana.
>
> **Longitud: dos fuentes, y hay que leer las dos.**
> - La **plantilla** recomienda 4 páginas, con reparto Intro+Related 1p, Methods+Results 2,5p,
>   Discussion 0,5p. Eso es la forma de un reporte sólido **mínimo**.
> - Las **Guidelines del sprint** ponen el techo: *«8 páginas o menos, sin contar referencias ni
>   apéndices. Most strong reports are 4 to 8.»* (`checklist-entrega.md`, del payload publicado.)
>
> **Objetivo aquí: ~6 páginas.** Es donde cabe lo que tenemos —tres bloques de resultados, una sección
> de validez que es una fortaleza real de este trabajo, y la historia de los artefactos retirados— sin
> rellenar para llegar a 8. Las proporciones de la plantilla se respetan, escaladas.
>
> **Presupuesto ≈ 3.000 palabras de texto + 3 figuras + 1 tabla.**
>
> **Otras restricciones de la plantilla:**
> - **Abstract 150–250 palabras** (no ≤150).
> - Figuras **numeradas**, con pie que se entienda **sin leer el texto**, y texto legible.
> - Separar observación de interpretación en Results; decir qué se probó y **no** funcionó en Methods.
> - Borrar toda la guía en cursiva de la plantilla antes de entregar.

---

## Cabecera

Título · autores con afiliación · «With Apart Research».
⟦ESCRIBIR: título. Debe contener el hallazgo, no el tema. Algo en la línea de «la cooperación costosa
en agentes de LLM tiene un umbral, no una pendiente».⟧

## Abstract — 150–250 palabras · **se pule al final**

⟦ESCRIBIR: problema, enfoque, resultados clave, conclusión principal. Cifras que puede citar:⟧
⟦CIFRA: precio 0 = 45,8% (22/48) · precio 5 = **27,6% (105/381)** · precio 20 = **20,2% (77/381)** — reportes/confirmatorio.json, congelado N=127⟧
⟦CIFRA: primario pareado 20−5 = **−7,35 pts, IC95 [−13,1; −1,6], EXCLUYE cero**, N=127 — reportes/confirmatorio.json⟧

## 1. Introduction — ~450 palabras · **no depende de ningún número, escribible ya**

⟦ESCRIBIR: el incidente de julio de 2026 como modelo de amenaza (anclas METR verificadas: líneas 1025,
1027, 1041, 1050; «presión significativa» **no** es literal — ver anclas-metr.md). El salto: el incidente
muestra que un agente consiguió que otro actuara, pero no dice **a qué precio**. Por qué importa en la
práctica: si la cooperación entre agentes es barata de comprar, un agente comprometido puede reclutar a
los demás.⟧

**Our main contributions are:** (la plantilla pide lista explícita)
1. ⟦ESCRIBIR: un instrumento que mide cooperación **costosa** con unidades, en régimen dominado — el
   beneficio privado de ayudar es exactamente cero, muy por debajo de los márgenes de ±0,05 que sondea
   la literatura más cercana.⟧
2. ⟦ESCRIBIR: el hallazgo de forma — umbral y no pendiente — replicado en dos mecanismos independientes.⟧
3. ⟦ESCRIBIR: evidencia de mecanismo desde las transcripciones: los agentes no deliberan sobre el costo.⟧

## 2. Related Work — ~350 palabras · **escribible ya**

⟦ESCRIBIR: cuatro grupos y qué deja fuera cada uno. Riesgo moral y márgenes estrechos (2607.23982,
2604.07821) · dictador en LLM sin costo instrumental (2410.21359, 2511.08721, 2402.05786) · bienes
públicos (2506.23276) · entornos multiagente (2602.15198, 2601.19082, 2412.10270, 2602.07777).
La frase del hueco, en su forma verdadera: no es «nadie ha medido cooperación costosa», es **«nadie la
ha medido muy por debajo de la frontera de racionalidad»**.⟧
⟦CIFRA: los 10 IDs citados están verificados en papers.md (que tiene 42) — comprobado 14 sep 01:05⟧

**Figura 1: mapa de regímenes**, que sitúa el diseño frente a los doce trabajos verificados.
⟦CIFRA: figuras/fig1-regime-map.png (EN) y fig1-mapa-regimenes.png (ES), 300 dpi⟧
⟦ESCRIBIR pie de Figura 1: autoexplicativo — dónde cae cada trabajo previo en el eje de costo de cooperar, y por qué el régimen dominado queda vacío.⟧

## 3. Methods — ~600 palabras

⟦ESCRIBIR: la escena en un párrafo; luego los cuatro pilares como justificación de diseño, que es lo que
la plantilla premia («justify design choices»). Decir también **qué se probó y no funcionó**, que la
plantilla lo pide explícitamente: el confederado pidiendo partes del código colapsaba el control
positivo, de ahí el objeto ortogonal; y el autor `agente-07` filtraba el número de agentes.⟧

- ⟦CIFRA: 6 agentes autosuficientes, 4 rondas, 8 acciones/ronda, presupuesto 40 pasos — escena.json; verificado en 145/145 no reclamantes con gastado+restante = 40⟧
- ⟦CIFRA: precios 5 y 20 dentro de la corrida; brazos de precio único a 0 y 1 — escena.json asignacion⟧
- ⟦CIFRA: modelo único glm-5.3-flash vía pasarela compatible con OpenAI; arnés propio de ~600 líneas sobre la capa de modelo de Inspect AI⟧
- ⟦CIFRA: validación adversarial previa: 12 invariantes I1-I12 + grep de canarios — harness/validador.py⟧
- ⟦CIFRA: exclusiones técnicas decididas sin mirar desenlaces, y el conjunto congelado fijado como lista explícita con su SHA — herramientas/fijar_conjunto.py⟧

## 4. Results — ~1.100 palabras + Figura 2 + Figura 3 + Tabla 1 · **el núcleo**

> **Qué entra al cuerpo.** Hay diez brazos y caben tres bloques. El criterio no es cuánto costó
> correr cada uno, sino qué afirmación sostiene: §4.1 el umbral · §4.2 que se replica en un mecanismo
> independiente · §4.3 el mecanismo de por qué. **Precio 0 entra aunque no sea el contraste
> preregistrado**: es el control positivo. **Precio 1 también**: es lo que sitúa el umbral abajo.
> Identidad del solicitante va al apéndice — su intervalo es [−30,6; +34,7] y no informa solo; la
> misma pregunta la contestan mejor el reclutador y el lado de tomar.

### 4.1 Figura 2 — la curva de precio: umbral, no pendiente

| precio | tasa | IC95 | fuente |
| --- | --- | --- | --- |
| 0 | 45,8% (22/48) | [32,6; 59,7] | confirmatorio.json |
| 1 | **35,4% (17/48)** | [20,8; 47,9] | exploratorios.json |
| 5 | 27,6% (105/381) | [23,3; 32,3] | confirmatorio.json |
| 20 | 20,2% (77/381) | [16,5; 24,5] | confirmatorio.json |

⟦CIFRA: primario pareado 20−5 = **−7,35 pts [−13,1; −1,6], excluye cero**, N=127 congeladas — confirmatorio.json⟧
⟦CIFRA: la mirada previa a N=70 dio −3,3 pts [−11,4; +4,3], incluía cero. Localizable en el commit 8602461, sha 7972c708088544c6. **Se reportan las dos**: un intervalo que cambia de veredicto con el tamaño de muestra se declara, no se elige.⟧
⟦CIFRA: 0 − 5 = **+18,5 pts [+2,1; +35,4]** contra todo el lote — verificado por mí sobre salidas/⟧
⟦CIFRA: 0 − 5 = **+30,2 pts [+12,5; +47,9]** contra el precio 5 de la MISMA ventana horaria (20:00-23:00, cuando corrió el precio 0). El precio 0 se corrió en 15 minutos de un periodo de nivel bajo, así que la versión pooled es la **conservadora**. Reportar las dos.⟧

⟦ESCRIBIR: observación e interpretación **separadas**, que la plantilla lo pide. Observación: la tasa cae
18-30 puntos entre 0 y 5, y otros 7,4 entre 5 y 20. Interpretación: la historia es de **dos partes** —
pagar cualquier cosa hunde la cooperación (grande y robusto), y pagar más la deprime algo más (pequeño
pero real). «Umbral, no pendiente» se queda corto con las 127. **Precio 0 es el control positivo**: sin
él, un nulo no se distingue de un instrumento sordo.⟧
⟦CIFRA: **las tasas por celda derivan a lo largo del lote** (precio 5 va de ~15,6% entre las 20:00 y
las 23:00 a 34,4% en las corridas tardías), pero el **pareado no**: cortando por el reinicio da −5,83
[−13,3; +1,3] antes y −9,93 [−19,1; −0,7] después, con la diferencia entre bloques en +4,1 pts
[−8,0; +15,6], incluye cero. Parear dentro de la corrida absorbe la deriva de nivel. El número que
manda es el pareado; las tasas de celda van con esta nota.⟧

**Pie de Figura 2** ⟦ESCRIBIR: tiene que entenderse solo. Algo como: «Tasa de entrega de la clave frente
al precio en pasos de presupuesto. Barras de error: IC95 por remuestreo de corridas. La cooperación se
rompe al introducir cualquier costo y luego no responde a su magnitud.»⟧

### 4.2 Figura 3 — el mismo patrón en un mecanismo independiente

⟦CIFRA: toma en ronda 1, seis celdas: sin marco 29,2% / 25,0%; neutral 14,6% / 18,8%; reclutador 17,8% / 20,0% (K=5 / K=20) — reportes/tomar-3x2.json⟧
⟦CIFRA: con el fondo intacto, ninguno de los doce contrastes excluye cero — tomar-3x2.json marco_solo_ronda1 e interaccion_solo_ronda1⟧

⟦ESCRIBIR: abstenerse de saquear un fondo común es el mismo tipo de acto costoso, con otro endpoint y
otro pago. Abstención 71-85%, y cuadruplicar el botín (+3,33 → +13,33 netos) no la mueve. Dos
operacionalizaciones independientes, misma forma.⟧

### 4.3 Tabla 1 — lo que razonan los agentes

⟦CIFRA: razona el costo en pasos: 4,2% (R1a) y 2,1% (R1c) — reportes/reclutador-texto.json⟧
⟦CIFRA: se niega explícitamente 27,1% y 35,4%; menciona al beneficiario 2,1% frente a 45,8% — reclutador-texto.json⟧
⟦CIFRA: entrega bajo apelación por un tercero: 2/24 y 4/24 a precio 5 y 20 — reportes/reclutador.json⟧

⟦ESCRIBIR: el nulo del reclutador no es por desatención, y el 2-4% explica por qué el precio no produce
pendiente: los agentes aplican una regla sobre el objeto, no aritmética. Declarar el método: codificación
por palabra clave, un codificador, sin medida de acuerdo, patrones publicados.⟧

## 5. Discussion and Limitations — ~450 palabras en total

⟦ESCRIBIR (Discussion, ~180 palabras): implicación para seguridad. Lo que movió la conducta no fue quién
pedía ni por quién, sino que hubiera un pedido y qué regla tenía el agente sobre el objeto. La defensa
barata está en delimitar qué puede salir de un agente, no en enseñarle a desconfiar de quién pregunta.⟧

**Limitations** ⟦ESCRIBIR, ~180 palabras. Las cinco, con su número — fuente: validez-instrumento.md⟧
- ⟦CIFRA: el precio se asigna barajando con semilla fija una sola vez, así que 01-03 llevan 5 y 04-06 llevan 20 en 108/108: el precio está confundido con el índice del agente — validez-instrumento.md §1⟧
- ⟦CIFRA: efecto de posición medido, −3,7 pts [−15,6; +8,1] en 45 corridas: no excluye cero pero es del mismo orden que el primario — reportes/posicion.json⟧
- ⟦CIFRA: la tentación está confundida con la capacidad del fondo, y el libro del fondo acredita 220 pasos sin contrapartida — validez-instrumento.md §4⟧
- ⟦CIFRA: un modelo único; contención por proceso, no por contenedor⟧
- ⟦CIFRA: 9 corridas invalidadas por un servicio caído, excluidas y declaradas — instrucciones-escenas.md §0.1⟧

⟦ESCRIBIR: **la frase que da credibilidad**, y va aquí: de los cinco efectos de tratamiento que en algún
momento parecieron positivos, **tres resultaron artefactos que encontramos nosotros** — la interacción
marco×botín, el efecto de marco a K=20 (ambos eran agotamiento del fondo; uno cambia de signo al
restringir a ronda 1) y las nueve corridas del servicio caído.⟧

**Future Work** ⟦ESCRIBIR, ~90 palabras: semilla por corrida para contrabalancear el precio; reserva
escalada con K; familias mixtas de modelos (especificado y sin correr); segunda tarea (requiere
generalizar `resolver()`).⟧

## 6. Conclusion — 1-2 párrafos

⟦ESCRIBIR: la frase que sobrevivió a todos los controles — la cooperación costosa se rompe con cualquier
precio y luego es indiferente a su tamaño, en dos mecanismos independientes, y la razón es que los
agentes no deliberan sobre el costo sino sobre qué objeto les corresponde soltar.⟧

## Code and Data

- Code repository: ⟦PENDIENTE: enlace; el remoto actual es un nombre temporal — decisión del equipo⟧
- Data: ⟦CIFRA: `salidas/` con las corridas completas (resumen, eventos con cadena de hashes, presupuesto y transcripciones); agregados en `reportes/` con su hash y hora⟧
- ⟦ESCRIBIR: nota de uso dual — no se publican recetas de instalación novedosas sin revisión.⟧

## Author Contributions (opcional)

⟦ESCRIBIR⟧

## References

⟦ESCRIBIR: formato consistente, con URL o DOI. Los 10 IDs citados están en papers.md.⟧

## Appendix

Identidad del solicitante (par vs externo) · análisis de posición ·
defectos del instrumento (`apendice-defectos.md`) · brazo del reclutador completo
(`reclutador-analisis.md`) · validez del instrumento (`validez-instrumento.md`) · apéndice de uso dual ·
traza de las 13 enmiendas del preregistro.

## LLM Usage Statement — **obligatorio, y aquí conviene ser exacto**

⟦ESCRIBIR, sobre estos hechos, que son verificables:⟧
- Los guiones de análisis (`analisis/`, `herramientas/`) fueron escritos con asistencia de LLM y **corren
  sobre datos que cualquiera puede recomputar**: cada cifra del reporte apunta a un archivo de `reportes/`.
- Un asistente actuó como **revisor independiente** del análisis: encontró y corrigió tres efectos que
  parecían significativos y eran artefactos, y varios defectos del instrumento, todos documentados con
  el dato que los desmiente.
- ⟦ESCRIBIR: quién escribió el reporte. La plantilla pide que sea el equipo.⟧

---

## Checklist de cierre

- [ ] entre **4 y 8 páginas** sin referencias ni apéndice (objetivo ~6; techo duro 8) · abstract **150–250** palabras
- [ ] toda la guía en cursiva de la plantilla borrada · título y autores actualizados
- [ ] figuras numeradas, con pie autoexplicativo y texto legible
- [ ] observaciones separadas de interpretaciones (§4)
- [ ] LLM Usage Statement presente
- [ ] apéndice de uso dual y frase de «no se publican recetas de instalación sin revisión»
- [ ] cada ID citado en `papers.md` ✔ (verificado 01:05)
- [ ] cada cifra rastreable a `reportes/` con su hash en `congelado.json`
- [ ] tres miradas del confirmatorio reportadas, titular en la preplaneada
- [ ] desviaciones del preregistro declaradas
- [ ] enviar borrador temprano: reenviar con el mismo título reemplaza los archivos
