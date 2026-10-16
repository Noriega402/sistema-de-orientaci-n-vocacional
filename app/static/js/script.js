console.log("🔥 SCRIPT NUEVO DE VOCARE CARGADO - PRUEBA 2026 🔥");
const API_URL = window.location.origin;
let avancePendiente = null;
let enviandoTest = false;

let preguntas = [];
let respuestasDisponibles = [];
let respuestasUsuario = [];
let preguntaActual = 0;

function $(id) {
  return document.getElementById(id);
}

function navigateTo(targetId) {
  const target = $(targetId);
  if (!target || !target.classList.contains("screen")) return;

  document.querySelectorAll(".screen").forEach((screen) => {
    screen.classList.toggle("active", screen === target);
  });
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.classList.toggle("active", link.dataset.target === targetId);
  });
  if (window.location.hash !== `#${targetId}`) {
    history.pushState(null, "", `#${targetId}`);
  }

  const menu = $("navMenu");
  const hamburger = $("hamburger");
  if (menu) {
    menu.classList.remove("open");
    menu.style.right = "";
  }
  if (hamburger) hamburger.classList.remove("active");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function configurarInterfaz() {
  window.addEventListener("hashchange", () => {
    const targetId = window.location.hash.slice(1);
    if (targetId) navigateTo(targetId);
  });
  const themeToggle = $("themeToggle");
  const savedTheme = localStorage.getItem("theme") === "dark";
  document.documentElement.classList.toggle("dark", savedTheme);
  if (themeToggle) {
    themeToggle.checked = savedTheme;
    themeToggle.addEventListener("change", () => {
      document.documentElement.classList.toggle("dark", themeToggle.checked);
      localStorage.setItem("theme", themeToggle.checked ? "dark" : "light");
    });
  }

  document.querySelectorAll(".nav-link[data-target]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      navigateTo(link.dataset.target);
    });
  });

  const hamburger = $("hamburger");
  const menu = $("navMenu");
  if (hamburger && menu) {
    hamburger.addEventListener("click", () => {
      const open = menu.classList.toggle("open");
      hamburger.classList.toggle("active", open);
      menu.style.right = open ? "0" : "";
    });
  }
  const initialTarget = window.location.hash.slice(1);
  if (initialTarget) navigateTo(initialTarget);
}

function obtenerSesion() {
  const session = localStorage.getItem("vocare_session");

  if (!session) {
    return null;
  }

  try {
    return JSON.parse(session);
  } catch (error) {
    console.error("Error leyendo sesión:", error);
    localStorage.removeItem("vocare_session");
    return null;
  }
}

function validarSesion() {
  const usuario = obtenerSesion();

  if (!usuario) {
    window.location.href = "/login";
    return null;
  }

  if (!usuario.id_usuario) {
    console.error("La sesión no contiene id_usuario.");
    localStorage.removeItem("vocare_session");
    window.location.href = "/login";
    return null;
  }

  return usuario;
}

function mostrarUsuario() {
  const usuario = obtenerSesion();

  if (!usuario) {
    return;
  }

  const elementosNombre = ["userName", "nombreUsuario", "user-name"];
  elementosNombre.forEach((id) => {
    const elemento = $(id);

    if (elemento) {
      elemento.textContent = usuario.nombre || "Usuario";
    }
  });

  const elementosCorreo = ["userEmail", "correoUsuario", "user-email"];
  elementosCorreo.forEach((id) => {
    const elemento = $(id);

    if (elemento) {
      elemento.textContent = usuario.correo || "";
    }
  });
}

function cerrarSesion() {
  localStorage.removeItem("vocare_session");
  sessionStorage.removeItem("vocare_ultimo_resultado");

  window.location.href = "/login";
}

async function cargarPreguntas() {
  try {
    const response = await fetch(`${API_URL}/preguntas`);

    if (!response.ok) {
      throw new Error(`Error HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log("Preguntas recibidas:", data);
    preguntas = data.preguntas || [];
    respuestasDisponibles = data.respuestas || [];

    if (preguntas.length === 0) {
      console.error("No se encontraron preguntas.");
      mostrarErrorTest("No hay preguntas registradas en la base de datos.");
      return;
    }

    if (respuestasDisponibles.length === 0) {
      console.error("No se encontraron respuestas.");
      mostrarErrorTest(
        "No hay opciones de respuesta registradas en la base de datos.",
      );
      return;
    }

    console.log(`Preguntas cargadas: ${preguntas.length}`);
    console.log(`Respuestas disponibles: ${respuestasDisponibles.length}`);

    preguntas.sort(
      (a, b) => (a.orden || a.id_pregunta) - (b.orden || b.id_pregunta),
    );

    respuestasDisponibles.sort((a, b) => a.valor - b.valor);
    preguntaActual = 0;
    respuestasUsuario = [];
    ocultarErrorTest();
    mostrarPregunta();
  } catch (error) {
    console.error("Error cargando preguntas:", error);

    mostrarErrorTest("No fue posible cargar las preguntas.");
  }
}

function mostrarPregunta() {
  clearTimeout(avancePendiente);
  avancePendiente = null;
  const contenedor = $("questionsContainer");
  if (!contenedor || !preguntas.length) return;
  const pregunta = preguntas[preguntaActual];
  const seleccion = respuestasUsuario.find(
    (r) => r.id_pregunta === Number(pregunta.id_pregunta),
  );
  contenedor.replaceChildren();
  const bloque = document.createElement("fieldset");
  bloque.className = "bloque-pregunta pregunta-slide";
  bloque.id = `pregunta-${pregunta.id_pregunta}`;
  const titulo = document.createElement("legend");
  titulo.className = "pregunta-titulo";
  titulo.tabIndex = -1;
  titulo.textContent = pregunta.pregunta;
  bloque.append(titulo);
  const opciones = document.createElement("div");
  opciones.className = "opciones-respuesta";
  respuestasDisponibles.forEach((respuesta) => {
    const opcion = document.createElement("label");
    opcion.className = "option-label opcion-respuesta";
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = `pregunta_${pregunta.id_pregunta}`;
    radio.value = respuesta.id_respuesta;
    radio.checked = seleccion?.id_respuesta === Number(respuesta.id_respuesta);
    opcion.classList.toggle("seleccionada", radio.checked);
    const texto = document.createElement("span");
    texto.textContent = respuesta.texto;
    opcion.append(radio, texto);
    radio.addEventListener("change", () => {
      seleccionarRespuesta(
        Number(pregunta.id_pregunta),
        Number(respuesta.id_respuesta),
      );
      opciones
        .querySelectorAll("label")
        .forEach((el) => el.classList.toggle("seleccionada", el === opcion));
      // Dar tiempo para ver la selección antes de avanzar. No enviar automáticamente.
      clearTimeout(avancePendiente);
      if (preguntaActual < preguntas.length - 1) {
        avancePendiente = setTimeout(() => {
          preguntaActual++;
          mostrarPregunta();
        }, 350);
      }
    });
    opciones.append(opcion);
  });
  bloque.append(opciones);
  contenedor.append(bloque);
  $("contadorPregunta").textContent =
    `Pregunta ${preguntaActual + 1} de ${preguntas.length} · ${respuestasUsuario.length} respondidas`;
  $("btnAnteriorPregunta").disabled = preguntaActual === 0 || enviandoTest;
  $("btnContinuarPregunta").hidden = preguntaActual === preguntas.length - 1;
  $("btnContinuarPregunta").disabled = !seleccion || enviandoTest;
  $("btnFinalizarTest").hidden = respuestasUsuario.length !== preguntas.length;
  $("btnFinalizarTest").disabled = enviandoTest;
  if (document.getElementById("test")?.classList.contains("active"))
    titulo.focus({ preventScroll: true });
  actualizarProgreso();
}

function moverPregunta(paso) {
  if (enviandoTest || (paso > 0 && !preguntaRespondida())) return;
  preguntaActual = Math.max(
    0,
    Math.min(preguntas.length - 1, preguntaActual + paso),
  );
  mostrarPregunta();
}

function seleccionarRespuesta(idPregunta, idRespuesta) {
  const indice = respuestasUsuario.findIndex(
    (respuesta) => respuesta.id_pregunta === idPregunta,
  );

  const nuevaRespuesta = {
    id_pregunta: Number(idPregunta),

    id_respuesta: Number(idRespuesta),
  };

  if (indice >= 0) {
    respuestasUsuario[indice] = nuevaRespuesta;
  } else {
    respuestasUsuario.push(nuevaRespuesta);
  }

  console.log("Respuestas actuales:", respuestasUsuario);

  actualizarProgreso();
  $("btnContinuarPregunta").disabled = false;
  $("btnFinalizarTest").hidden = respuestasUsuario.length !== preguntas.length;
}

function preguntaRespondida() {
  if (preguntaActual < 0 || preguntaActual >= preguntas.length) {
    return false;
  }

  const pregunta = preguntas[preguntaActual];

  return respuestasUsuario.some(
    (respuesta) => respuesta.id_pregunta === pregunta.id_pregunta,
  );
}

function actualizarProgreso() {
  const progreso = preguntas.length
    ? (respuestasUsuario.length / preguntas.length) * 100
    : 0;

  const barra = $("barraProgreso");

  if (barra) {
    barra.style.width = `${progreso}%`;
  }

  const porcentaje = $("porcentajeProgreso");

  if (porcentaje) {
    porcentaje.textContent = `${Math.round(progreso)}%`;
  }
}

async function finalizarTest() {
  if (enviandoTest || !preguntas.length) return;
  clearTimeout(avancePendiente);
  ocultarErrorTest();

  const usuario = obtenerSesion();

  if (!usuario || !usuario.id_usuario) {
    mostrarErrorTest("Tu sesión no es válida. Inicia sesión nuevamente.");

    return;
  }

  if (respuestasUsuario.length !== preguntas.length) {
    mostrarErrorTest(
      `Te faltan ${preguntas.length - respuestasUsuario.length} preguntas por responder.`,
    );

    const pendiente = preguntas.find(
      (pregunta) =>
        !respuestasUsuario.some(
          (respuesta) => respuesta.id_pregunta === pregunta.id_pregunta,
        ),
    );
    if (pendiente)
      $(`pregunta-${pendiente.id_pregunta}`)?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    return;
  }

  respuestasUsuario.sort((a, b) => a.id_pregunta - b.id_pregunta);

  const payload = {
    id_usuario: usuario.id_usuario,
    respuestas: respuestasUsuario,
  };

  console.log("Enviando test:", payload);

  const btnSiguiente = $("btnFinalizarTest");

  if (btnSiguiente) {
    btnSiguiente.disabled = true;
    btnSiguiente.textContent = "Analizando respuestas...";
  }

  enviandoTest = true;
  $("btnAnteriorPregunta").disabled = true;
  $("btnContinuarPregunta").disabled = true;
  try {
    const response = await fetch(`${API_URL}/guardar-test`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    console.log("Resultado del test:", data);

    if (!response.ok) {
      let mensaje = "No fue posible procesar el test.";

      if (typeof data.detail === "string") {
        mensaje = data.detail;
      } else if (Array.isArray(data.detail)) {
        mensaje = data.detail.map((error) => error.msg).join(", ");
      }

      throw new Error(mensaje);
    }

    sessionStorage.setItem(
      "vocare_ultimo_resultado",
      JSON.stringify({ ...data, id_usuario: usuario.id_usuario }),
    );

    mostrarResultados(data.top3);
    habilitarDescargaPDF();
  } catch (error) {
    console.error("Error procesando test:", error);
    mostrarErrorTest(error.message || "Ocurrió un error al procesar el test.");

    if (btnSiguiente) {
      btnSiguiente.disabled = false;
      btnSiguiente.textContent = "Obtener resultados";
    }
  } finally {
    enviandoTest = false;
    mostrarPregunta();
  }
}

function mostrarResultados(top3, navegar = true) {
  if (!Array.isArray(top3) || top3.length === 0) {
    console.error("No se recibieron resultados válidos:", top3);

    return;
  }

  console.log("Resultados recibidos:", top3);
  const summary = document.getElementById("results-summary");
  const chart = document.getElementById("results-chart");
  const container = document.getElementById("results-container");

  if (!summary || !chart || !container) {
    console.error("No se encontraron los contenedores de resultados.");

    return;
  }

  const resultados = top3.map((item, index) => {
    return {
      posicion: item.posicion || index + 1,
      nombre: item.nombre || item.carrera || "Carrera",
      probabilidad: Number(item.probabilidad || 0),
      descripcion: item.descripcion || "",
      area: item.area || "Área no especificada",
      duracion: item.duracion || "No especificada",
      modalidad: item.modalidad || "No especificada",
    };
  });

  const mejor = resultados[0];

  summary.innerHTML = `

    <div
      class="
        absolute
        -top-20
        -right-20
        w-64
        h-64
        bg-brand/10
        rounded-full
        blur-3xl
        pointer-events-none
      "
    ></div>


    <div
      class="
        relative
        z-10
        text-center
        max-w-3xl
        mx-auto
      "
    >

      <!-- Badge -->

      <div
        class="
          inline-flex
          items-center
          gap-2
          px-4
          py-2
          bg-brand/10
          text-brand
          rounded-full
          text-xs
          font-bold
          uppercase
          tracking-wider
          mb-6
        "
      >

        <span>
          ★
        </span>

        Mayor afinidad

      </div>


      <!-- Título -->

      <p
        class="
          text-[#5a6278]
          dark:text-[#a8b2c1]
          font-semibold
          mb-2
        "
      >
        Tu carrera con mayor afinidad es
      </p>


      <h2
        class="
          font-playfair
          text-4xl
          md:text-5xl
          font-black
          text-brand
          mb-5
        "
      >
        ${mejor.nombre}
      </h2>


      <!-- Porcentaje -->

      <div
        class="
          inline-flex
          items-baseline
          gap-2
          mb-6
        "
      >

        <span
          class="
            font-playfair
            text-5xl
            md:text-6xl
            font-black
            text-navy
            dark:text-[#e8e9ed]
          "
        >
          ${mejor.probabilidad.toFixed(2)}%
        </span>

        <span
          class="
            text-sm
            font-semibold
            text-slate-400
          "
        >
          de afinidad
        </span>

      </div>


      ${
        mejor.descripcion
          ? `

          <p
            class="
              text-[#5a6278]
              dark:text-[#a8b2c1]
              leading-relaxed
              max-w-2xl
              mx-auto
              mb-7
            "
          >
            ${mejor.descripcion}
          </p>

          `
          : ""
      }


      <!-- Información -->

      <div
        class="
          flex
          flex-wrap
          justify-center
          gap-3
          mt-4
        "
      >

        <span
          class="
            px-4
            py-2
            bg-slate-100
            dark:bg-[#1a1f2e]
            rounded-full
            text-xs
            font-semibold
            text-[#5a6278]
            dark:text-[#a8b2c1]
          "
        >
          Área: ${mejor.area}
        </span>


        <span
          class="
            px-4
            py-2
            bg-slate-100
            dark:bg-[#1a1f2e]
            rounded-full
            text-xs
            font-semibold
            text-[#5a6278]
            dark:text-[#a8b2c1]
          "
        >
          Modalidad: ${mejor.modalidad}
        </span>


        <span
          class="
            px-4
            py-2
            bg-slate-100
            dark:bg-[#1a1f2e]
            rounded-full
            text-xs
            font-semibold
            text-[#5a6278]
            dark:text-[#a8b2c1]
          "
        >
          Duración: ${mejor.duracion}
        </span>

      </div>

    </div>
  `;

  /* GRÁFICA COMPARATIVA TOP 3 */
  dibujarResultadosInteractivos(chart, resultados);

  container.innerHTML = resultados
    .map((resultado, index) => {
      const esPrimero = index === 0;

      return `

            <article
              class="
                relative
                bg-white
                dark:bg-[#242938]
                rounded-[1.7rem]
                p-7
                border
                ${
                  esPrimero
                    ? "border-brand"
                    : "border-bluegray/20 dark:border-bluegray/10"
                }
                shadow-md
                hover:-translate-y-2
                hover:shadow-xl
                transition-all
                duration-300
                overflow-hidden
              "
            >


              ${
                esPrimero
                  ? `

                  <div
                    class="
                      absolute
                      top-0
                      right-0
                      bg-brand
                      text-white
                      text-[10px]
                      font-bold
                      uppercase
                      tracking-wider
                      px-4
                      py-2
                      rounded-bl-xl
                    "
                  >
                    Mayor afinidad
                  </div>

                  `
                  : ""
              }


              <!-- POSICIÓN -->

              <div
                class="
                  text-xs
                  font-bold
                  text-brand
                  uppercase
                  tracking-[0.15em]
                  mb-3
                "
              >
                Opción ${index + 1}
              </div>


              <!-- CARRERA -->

              <h3
                class="
                  font-playfair
                  text-2xl
                  font-black
                  text-navy
                  dark:text-[#e8e9ed]
                  leading-tight
                  mb-5
                  pr-5
                "
              >
                ${resultado.nombre}
              </h3>


              <!-- PORCENTAJE -->

              <div
                class="
                  flex
                  items-end
                  gap-2
                  mb-6
                "
              >

                <span
                  class="
                    font-playfair
                    text-4xl
                    font-black
                    text-brand
                  "
                >
                  ${resultado.probabilidad.toFixed(2)}%
                </span>


                <span
                  class="
                    text-xs
                    text-slate-400
                    font-semibold
                    mb-1
                  "
                >
                  afinidad
                </span>

              </div>


              <!-- INFORMACIÓN -->

              <div
                class="
                  space-y-3
                  text-sm
                  mb-6
                "
              >

                <div
                  class="
                    flex
                    justify-between
                    gap-3
                  "
                >

                  <span
                    class="
                      font-semibold
                      text-navy
                      dark:text-[#e8e9ed]
                    "
                  >
                    Área
                  </span>

                  <span
                    class="
                      text-[#5a6278]
                      dark:text-[#a8b2c1]
                      text-right
                    "
                  >
                    ${resultado.area}
                  </span>

                </div>


                <div
                  class="
                    flex
                    justify-between
                    gap-3
                  "
                >

                  <span
                    class="
                      font-semibold
                      text-navy
                      dark:text-[#e8e9ed]
                    "
                  >
                    Modalidad
                  </span>

                  <span
                    class="
                      text-[#5a6278]
                      dark:text-[#a8b2c1]
                    "
                  >
                    ${resultado.modalidad}
                  </span>

                </div>


                <div
                  class="
                    flex
                    justify-between
                    gap-3
                  "
                >

                  <span
                    class="
                      font-semibold
                      text-navy
                      dark:text-[#e8e9ed]
                    "
                  >
                    Duración
                  </span>

                  <span
                    class="
                      text-[#5a6278]
                      dark:text-[#a8b2c1]
                    "
                  >
                    ${resultado.duracion}
                  </span>

                </div>

              </div>


              ${
                resultado.descripcion
                  ? `

                  <button
                    type="button"

                    onclick="
                      toggleCareerDetails(
                        'career-details-${index}',
                        this
                      )
                    "

                    class="
                      w-full
                      py-3
                      px-4
                      rounded-xl
                      bg-brand/10
                      text-brand
                      font-bold
                      text-sm
                      hover:bg-brand
                      hover:text-white
                      transition-all
                      duration-300
                    "
                  >
                    Ver detalles
                  </button>


                  <div
                    id="career-details-${index}"

                    class="
                      hidden
                      mt-5
                      pt-5
                      border-t
                      border-slate-200
                      dark:border-bluegray/10
                    "
                  >

                    <p
                      class="
                        text-sm
                        text-[#5a6278]
                        dark:text-[#a8b2c1]
                        leading-relaxed
                      "
                    >
                      ${resultado.descripcion}
                    </p>

                  </div>

                  `
                  : ""
              }

            </article>
          `;
    })
    .join("");

  if (typeof navigateTo === "function") {
    if (navegar) navigateTo("resultados");
  }
}

function toggleCareerDetails(id, button) {
  const details = document.getElementById(id);

  if (!details) {
    return;
  }

  const abierto = !details.classList.contains("hidden");

  if (abierto) {
    details.classList.add("hidden");
    button.textContent = "Ver detalles";
  } else {
    details.classList.remove("hidden");
    button.textContent = "Ocultar detalles";
  }
}

function escapeHtml(texto) {
  if (texto === null || texto === undefined) {
    return "";
  }

  return String(texto)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function mostrarErrorTest(mensaje) {
  const error = $("testError");

  if (error) {
    error.textContent = mensaje;
    error.classList.remove("hidden");
    error.style.display = "block";
    return;
  }

  console.error(mensaje);

  alert(mensaje);
}

function ocultarErrorTest() {
  const error = $("testError");

  if (error) {
    error.classList.add("hidden");
    error.style.display = "none";
    error.textContent = "";
  }
}

function iniciarNuevoTest() {
  clearTimeout(avancePendiente);
  $("btnFinalizarTest").textContent = "Obtener resultados";
  navigateTo("test");
  respuestasUsuario = [];
  preguntaActual = 0;
  const resultsSection = $("resultsSection");

  if (resultsSection) {
    resultsSection.style.display = "none";
  }

  const testSection = $("testSection");

  if (testSection) {
    testSection.style.display = "block";
  }

  cargarPreguntas();
}

async function cargarHistorial() {
  const usuario = obtenerSesion();

  if (!usuario || !usuario.id_usuario) {
    return;
  }

  const contenedor = $("historialContainer");

  if (!contenedor) {
    return;
  }

  try {
    const response = await fetch(`${API_URL}/historial/${usuario.id_usuario}`);

    if (!response.ok) {
      throw new Error(`Error HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log("Historial:", data);
    mostrarHistorial(data);
  } catch (error) {
    console.error("Error cargando historial:", error);
  }
}

function mostrarHistorial(data) {
  const contenedor = $("historialContainer");

  if (!contenedor) {
    return;
  }

  const historial = Array.isArray(data)
    ? data
    : data.historial || data.resultados || [];

  if (historial.length === 0) {
    contenedor.innerHTML = `
            <p>
                Aún no tienes resultados
                registrados.
            </p>
        `;

    return;
  }

  contenedor.innerHTML = "";

  historial.forEach((resultado) => {
    const elemento = document.createElement("div");
    elemento.className = "historial-item";
    elemento.innerHTML = `
                <strong>
                    Resultado #${escapeHtml(resultado.id_resultado || "")}
                </strong>

                ${
                  resultado.fecha ||
                  resultado.fecha_resultado ||
                  resultado.fecha_registro
                    ? `
                    <p>
                        ${escapeHtml(
                          resultado.fecha ||
                            resultado.fecha_resultado ||
                            resultado.fecha_registro,
                        )}
                    </p>
                    `
                    : ""
                }
            `;

    contenedor.appendChild(elemento);
  });
}

function configurarEventos() {
  $("btnDescargarPDF")?.addEventListener("click", descargarResultadosPDF);
  $("btnAnteriorPregunta")?.addEventListener("click", () => moverPregunta(-1));
  $("btnContinuarPregunta")?.addEventListener("click", () => moverPregunta(1));
  const formulario = $("vocationalForm");
  if (formulario) {
    formulario.addEventListener("submit", (event) => {
      event.preventDefault();
      finalizarTest();
    });
  }

  const logoutIds = ["logoutBtn", "btnLogout", "cerrarSesion"];

  logoutIds.forEach((id) => {
    const boton = $(id);

    if (boton) {
      boton.addEventListener("click", function (event) {
        event.preventDefault();

        cerrarSesion();
      });
    }
  });

  const nuevoTestIds = ["nuevoTestBtn", "btnNuevoTest", "repetirTest"];

  nuevoTestIds.forEach((id) => {
    const boton = $(id);

    if (boton) {
      boton.addEventListener("click", function (event) {
        event.preventDefault();
        iniciarNuevoTest();
      });
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  console.log("Vocare iniciado.");
  configurarInterfaz();
  const usuario = validarSesion();

  if (!usuario) {
    return;
  }

  console.log("Usuario autenticado:", usuario);
  mostrarUsuario();
  configurarEventos();

  if ($("questionsContainer")) {
    cargarPreguntas();
  }

  if ($("historialContainer")) {
    cargarHistorial();
  }
  try {
    const previo = JSON.parse(
      sessionStorage.getItem("vocare_ultimo_resultado"),
    );
    if (previo?.top3 && previo.id_usuario === usuario.id_usuario)
      mostrarResultados(previo.top3, false);
      habilitarDescargaPDF();
  } catch (_) {
    sessionStorage.removeItem("vocare_ultimo_resultado");
  }
});

function dibujarResultadosInteractivos(chart, resultados) {
  const colores = ["#3c817c", "#6366f1", "#d97706"];
  let modo = "barras",
    activo = 0;
  const porcentaje = (r) =>
    Math.max(0, Math.min(100, Number(r.probabilidad) || 0));
  function render() {
    const r = resultados[activo],
      p = porcentaje(r);
    chart.innerHTML = `<div class="grafica-controles" role="group" aria-label="Tipo de gráfica">
      <button type="button" data-modo="barras" aria-pressed="${modo === "barras"}">Comparar carreras</button>
      <button type="button" data-modo="circular" aria-pressed="${modo === "circular"}">Explorar afinidad</button></div>
      <div class="grafica-selector" role="group" aria-label="Seleccionar carrera">${resultados.map((c, i) => `<button type="button" data-carrera="${i}" aria-pressed="${i === activo}">${i + 1}. ${escapeHtml(c.nombre)}</button>`).join("")}</div>
      <div class="grafica-vista">${modo === "barras" ? resultados.map((c, i) => `<button type="button" class="barra-interactiva" data-carrera="${i}" aria-pressed="${i === activo}"><span>${escapeHtml(c.nombre)} <strong>${porcentaje(c).toFixed(2)}%</strong></span><span class="grafica-pista"><span style="width:${porcentaje(c)}%;background:${colores[i % 3]}"></span></span></button>`).join("") + '<div class="grafica-escala"><span>0%</span><span>50%</span><span>100%</span></div>' : `<svg class="grafica-circular" viewBox="0 0 200 200" role="img" aria-label="${escapeHtml(r.nombre)}: ${p.toFixed(2)} por ciento de afinidad estimada"><circle cx="100" cy="100" r="78" fill="none" stroke="currentColor" opacity=".12" stroke-width="18"/><circle cx="100" cy="100" r="78" fill="none" stroke="${colores[activo % 3]}" stroke-width="18" pathLength="100" stroke-dasharray="${p} 100" transform="rotate(-90 100 100)"/><text x="100" y="98" text-anchor="middle" fill="currentColor" font-size="27" font-weight="700">${p.toFixed(2)}%</text><text x="100" y="122" text-anchor="middle" fill="currentColor" font-size="12">afinidad estimada</text></svg>`}</div>
      <div class="detalle-grafica" aria-live="polite"><h3>${escapeHtml(r.nombre)}</h3><p>${escapeHtml(r.descripcion || "Explora esta carrera y contrasta sus materias con tus intereses.")}</p><p><strong>Área:</strong> ${escapeHtml(r.area)} · <strong>Duración:</strong> ${escapeHtml(r.duracion)} · <strong>Modalidad:</strong> ${escapeHtml(r.modalidad)}</p></div>
      <p class="nota-modelo">La afinidad es una estimación del modelo, no una garantía de éxito ni una evaluación de tus capacidades. Las tres recomendaciones no tienen que sumar 100%.</p>`;
    chart.querySelectorAll("[data-modo]").forEach((b) =>
      b.addEventListener("click", () => {
        modo = b.dataset.modo;
        render();
        chart.querySelector(`[data-modo="${modo}"]`).focus();
      }),
    );
    chart.querySelectorAll("[data-carrera]").forEach((b) =>
      b.addEventListener("click", () => {
        activo = Number(b.dataset.carrera);
        render();
        chart.querySelector(`[data-carrera="${activo}"]`).focus();
      }),
    );
  }
  render();
}

function habilitarDescargaPDF() {
  const boton = $("btnDescargarPDF");
  if (boton) boton.disabled = false;
}

async function descargarResultadosPDF() {
  const boton = $("btnDescargarPDF"), estado = $("pdfEstado");
  const usuario = obtenerSesion();
  try {
    const resultado = JSON.parse(sessionStorage.getItem("vocare_ultimo_resultado"));
    if (!usuario || resultado?.id_usuario !== usuario.id_usuario || !resultado?.id_resultado) {
      throw new Error("Realiza un test para descargar tus resultados.");
    }
    boton.disabled = true;
    estado.textContent = "Preparando tu PDF…";
    const response = await fetch(`${API_URL}/resultados/${resultado.id_resultado}/pdf?id_usuario=${encodeURIComponent(usuario.id_usuario)}`);
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || "No se pudo descargar el PDF. Inténtalo nuevamente.");
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = `Vocare-resultados-${resultado.id_resultado}.pdf`;
    document.body.appendChild(enlace);
    enlace.click();
    enlace.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    estado.textContent = "PDF descargado. Incluye los porcentajes de todas las carreras evaluadas.";
  } catch (error) {
    estado.textContent = error.message;
  } finally {
    boton.disabled = false;
  }
}
