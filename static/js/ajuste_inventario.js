document.addEventListener("DOMContentLoaded", () => {
    loadInventoryAdjustments();
});

/* =========================
   BUSCAR AJUSTES
========================= */
async function loadInventoryAdjustments() {
    const container = document.getElementById("adjustments-list");
    container.innerHTML = "";

    try {
        const res = await fetch("/api/inventory-adjustments");
        const adjustments = await res.json();

        if (!adjustments.length) {
            container.innerHTML = `
                <div class="col-12 text-center text-muted">
                    Nenhum ajuste de inventário pendente.
                </div>
            `;
            return;
        }

        adjustments.forEach(adj => {
            container.appendChild(renderAdjustmentCard(adj));
        });

    } catch (err) {
        console.error(err);
        container.innerHTML = `
            <div class="col-12 text-center text-danger">
                Erro ao carregar ajustes de inventário
            </div>
        `;
    }
}

/* =========================
   CARD DO AJUSTE
========================= */
function renderAdjustmentCard(adj) {
    const col = document.createElement("div");
    col.className = "col-md-4 mb-4";

    const statusBadge =
        adj.status === "FINALIZADO"
            ? `<span class="badge bg-success">Finalizado</span>`
            : `<span class="badge bg-danger">Pendente</span>`;

    col.innerHTML = `
        <div class="card shadow-sm h-100 border-danger">
            <div class="card-body">

                <h5 class="card-title">
                    📦 Ajuste de Inventário
                </h5>

                <p class="mb-1">
                    <strong>AA:</strong> ${adj.aaLogin}
                </p>

                <p class="mb-1">
                    <strong>1º Contador:</strong> ${adj.firstCounter || "--"}
                </p>

                <p class="mb-1">
                    <strong>2º Contador:</strong> ${adj.secondCounter || "--"}
                </p>

                <p class="mb-1">
                    <strong>Erros (1ª):</strong> ${adj.firstErrors}
                </p>

                <p class="mb-3">
                    <strong>Erros (2ª):</strong> ${adj.secondErrors}
                </p>

                ${statusBadge}

                ${
                    adj.status !== "FINALIZADO"
                        ? `
                        <div class="d-grid mt-3">
                            <button
                                class="btn btn-outline-success"
                                onclick="finishAdjustment('${adj.id}')"
                            >
                                ✅ Finalizar Ajuste
                            </button>
                        </div>
                        `
                        : ""
                }

            </div>
        </div>
    `;

    return col;
}

/* =========================
   FINALIZAR AJUSTE
========================= */
async function finishAdjustment(adjustmentId) {
    if (!confirm("Deseja realmente finalizar este ajuste de inventário?")) {
        return;
    }

    const res = await fetch(
        `/api/inventory-adjustments/${adjustmentId}/finish`,
        { method: "POST" }
    );

    if (!res.ok) {
        alert("❌ Erro ao finalizar ajuste");
        return;
    }

    alert("✅ Ajuste finalizado com sucesso");
    loadInventoryAdjustments();
}
