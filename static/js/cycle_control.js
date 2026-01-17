let selectedFileId = null;

/* =========================
   INIT
========================= */
document.addEventListener("DOMContentLoaded", () => {
    loadActiveCycle();
    bindStartCycleButton();
});

/* =========================
   CICLO ATIVO
========================= */
async function loadActiveCycle() {
    const container = document.getElementById("cycle-list");
    container.innerHTML = `
        <div class="col-12 text-center text-muted">
            Carregando ciclo ativo...
        </div>
    `;

    const res = await fetch("/api/cycles/active");

    if (!res.ok) {
        showError("Erro ao buscar ciclo ativo");
        return;
    }

    const cycle = await res.json();

    if (!cycle) {
        container.innerHTML = `
            <div class="col-12 text-center text-muted">
                Nenhum ciclo ativo no momento.
            </div>
        `;
        return;
    }

    loadCycleFiles(cycle.id);
}

/* =========================
   FILES DO CICLO
========================= */
async function loadCycleFiles(cycleId) {
    const container = document.getElementById("cycle-list");
    container.innerHTML = "";

    const res = await fetch(`/api/cycle-files/${cycleId}`);

    if (!res.ok) {
        showError("Erro ao carregar arquivos do ciclo");
        return;
    }

    const files = await res.json();

    if (!files.length) {
        container.innerHTML = `
            <div class="col-12 text-center text-muted">
                Nenhum arquivo disponível neste ciclo.
            </div>
        `;
        return;
    }

    files.forEach(file => {
        container.appendChild(renderFileCard(file));
    });
}

/* =========================
   CARD
========================= */
function renderFileCard(file) {
    const col = document.createElement("div");

    // 🔴 SECOND COUNT = CARD VERMELHO
    const isSecond = file.countLevel === 2;
    const cardClass = isSecond ? "border-danger" : "border-secondary";

    col.className = "col-md-4 mb-4";

    col.innerHTML = `
        <div class="card shadow-sm h-100 ${cardClass}">
            <div class="card-body">

                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h5 class="card-title mb-0">
                        👤 ${file.aaLogin}
                    </h5>

                    ${
                        isSecond
                        ? `<span class="badge bg-danger">SECOND COUNT</span>`
                        : `<span class="badge bg-secondary">FIRST COUNT</span>`
                    }
                </div>

                <p class="mb-1">📦 Endereços: <strong>${file.totalAddresses}</strong></p>
                <p class="mb-1">🧾 SKUs: <strong>${file.totalSkus}</strong></p>

                <p class="mb-1">
                    🆔 FAAST ID:
                    <strong>${file.faastCountId || "--"}</strong>
                </p>

                ${
                    file.firstCounter
                    ? `<p class="mb-1">👨‍💼 1º Contador: <strong>${file.firstCounter}</strong></p>`
                    : ""
                }

                ${
                    file.countLevel === 2
                    ? `
                        <p class="mb-1 text-danger">
                            ❌ Erros (1ª contagem): <strong>${file.errorsFound}</strong>
                        </p>
                    `
                    : ""
                }

                <p class="mb-2">
                    📌 Status:
                    <span class="badge bg-${statusColor(file.status)}">
                        ${file.status}
                    </span>
                </p>

                <div class="d-grid gap-2 mt-3">

                    <button
                        class="btn btn-outline-primary"
                        onclick="downloadCsv('${file.id}')">
                        ⬇️ Download CSV
                    </button>

                    <button
                        class="btn btn-outline-secondary"
                        onclick="openAssignModal('${file.id}')"
                        ${file.status !== "PENDENTE" && file.status !== "SECOND_COUNT" ? "disabled" : ""}
                    >
                        👤 Atribuir Contador
                    </button>

                    <button
                        class="btn btn-outline-success"
                        onclick="openFinishModal('${file.id}')"
                        ${file.status !== "EM_CONTAGEM" ? "disabled" : ""}
                    >
                        ✅ Finalizar Contagem
                    </button>

                </div>

            </div>
        </div>
    `;

    return col;
}


/* =========================
   STATUS
========================= */
function statusColor(status) {
    switch (status) {
        case "PENDENTE": return "secondary";
        case "EM_CONTAGEM": return "warning";
        case "FECHADO": return "success";
        default: return "dark";
    }
}

/* =========================
   MODAIS
========================= */
function openAssignModal(fileId) {
    selectedFileId = fileId;

    // limpa campos
    document.getElementById("counterLogin").value = "";
    document.getElementById("faastCountId").value = "";

    new bootstrap.Modal(
        document.getElementById("assignModal")
    ).show();
}


function openFinishModal(fileId) {
    selectedFileId = fileId;
    new bootstrap.Modal(
        document.getElementById("finishModal")
    ).show();
}

/* =========================
   AÇÕES
========================= */
async function confirmAssign() {
    const counter = document.getElementById("counterLogin").value.trim();
    const faastId = document.getElementById("faastCountId").value.trim();

    if (!counter || !faastId) {
        alert("⚠️ Informe o login do contador e o ID do FAAST.");
        return;
    }

    const res = await fetch(
        `/api/cycle-files/${selectedFileId}/assign`,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                counterUid: counter,
                faastCountId: faastId
            })
        }
    );

    if (!res.ok) {
        const err = await res.json();
        alert("❌ " + (err.error || "Erro ao atribuir contador"));
        return;
    }

    alert("✅ Contador atribuído com sucesso");
    location.reload();
}


async function confirmFinish() {
    const errors = document.getElementById("errorCount").value;

    await fetch(`/api/cycle-files/${selectedFileId}/finish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ errorsFound: Number(errors) })
    });

    location.reload();
}

/* =========================
   START CYCLE
========================= */
function bindStartCycleButton() {
    const btn = document.getElementById("btnStartCycle");
    if (!btn) return;

    btn.addEventListener("click", async () => {
        if (!confirm("Isso abrirá o FAAST para gerar um novo cycle. Deseja continuar?")) {
            return;
        }

        alert(
            "O FAAST será aberto.\n\n" +
            "1️⃣ Selecione a data\n" +
            "2️⃣ Clique em Search\n" +
            "3️⃣ Clique em Download\n\n" +
            "Após o download, o sistema continuará automaticamente."
        );

        const res = await fetch("/api/cycle-control/start", {
            method: "POST"
        });

        const data = await res.json();

        alert(
            `Cycle criado com sucesso!\n\n` +
            `ID: ${data.cycleId}\n` +
            `Arquivos gerados: ${data.files}`
        );

        location.reload();
    });
}

/* =========================
   DOWNLOAD (placeholder)
========================= */
function downloadCsv(fileId) {
    alert("Endpoint de download será conectado no próximo passo.");
}

/* =========================
   ERROR
========================= */
function showError(message) {
    document.getElementById("cycle-list").innerHTML = `
        <div class="col-12 text-center text-danger">
            ${message}
        </div>
    `;
}


function downloadCsv(fileId) {
    fetch(`/api/cycle-files/${fileId}/download`)
        .then(res => res.json())
        .then(data => {
            if (!data.url) {
                alert("Erro ao gerar link de download");
                return;
            }

            // Abre download em nova aba
            window.open(data.url, "_blank");
        })
        .catch(err => {
            console.error(err);
            alert("Erro ao baixar arquivo");
        });
}
