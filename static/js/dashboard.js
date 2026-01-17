document.addEventListener("DOMContentLoaded", () => {
    loadSummary();
    loadCharts();
    loadCycles();
});

/* ================= SUMMARY ================= */
async function loadSummary() {
    const res = await fetch("/api/dashboard/summary");
    const data = await res.json();

    document.getElementById("current-shift").innerText = data.currentShift;
    document.getElementById("total-aa").innerText = data.aaAudited;
    document.getElementById("total-items").innerText = data.itemsProcessed;
    document.getElementById("total-cycles").innerText = data.totalCycles;

    if (document.getElementById("cycle-lost")) {
        document.getElementById("cycle-lost").innerText = data.cycleLost;
    }
}

/* ================= CHARTS ================= */
async function loadCharts() {
    try {
        const res = await fetch("/api/dashboard/charts");
        if (!res.ok) throw new Error("Erro charts");

        const data = await res.json();

        if (data.aaLabels.length) {
            new Chart(document.getElementById("aaChart"), {
                type: "bar",
                data: {
                    labels: data.aaLabels,
                    datasets: [{
                        label: "Itens Processados",
                        data: data.aaValues,
                        backgroundColor: "#0d6efd"
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } }
                }
            });
        }

        if (data.statusLabels.length) {
            new Chart(document.getElementById("statusChart"), {
                type: "doughnut",
                data: {
                    labels: data.statusLabels,
                    datasets: [{
                        data: data.statusValues,
                        backgroundColor: [
                            "#6c757d",
                            "#ffc107",
                            "#198754",
                            "#dc3545"
                        ]
                    }]
                }
            });
        }

    } catch (err) {
        console.error("Erro gráficos:", err);
    }
}

/* ================= CYCLES ================= */
async function loadCycles() {
    const res = await fetch("/api/cycles/recent");
    const cycles = await res.json();

    const table = document.getElementById("cycles-table");
    table.innerHTML = "";

    if (!cycles.length) {
        table.innerHTML = `
          <tr>
            <td colspan="5" class="text-center text-muted">
              Nenhum ciclo encontrado
            </td>
          </tr>
        `;
        return;
    }

    cycles.forEach(cycle => {
        table.innerHTML += `
          <tr>
            <td>--</td>
            <td>${formatPeriod(cycle.createdAt, cycle.expiresAt)}</td>
            <td>
              <span class="badge bg-${statusColor(cycle.status)}">
                ${cycle.status}
              </span>
            </td>
            <td>
              ${
                cycle.status === "LOST"
                  ? `<span class="text-danger fw-bold">Expirado</span>`
                  : `<span class="fw-bold">${formatSeconds(cycle.timeLeft)}</span>`
              }
            </td>
            <td>
              <a href="/cycle-control?cycleId=${cycle.id}" class="btn btn-sm btn-primary">
                Visualizar
              </a>
              <button class="btn btn-sm btn-danger"
                onclick="deleteCycle('${cycle.id}')">
                Deletar
              </button>
            </td>
          </tr>
        `;
    });
}

/* ================= HELPERS ================= */
function statusColor(status) {
    switch (status) {
        case "ABERTO": return "warning";
        case "FECHADO": return "success";
        case "LOST": return "danger";
        default: return "secondary";
    }
}

function formatPeriod(start, end) {
    if (!start || !end) return "--";

    const s = new Date(start);
    const e = new Date(end);

    return `
      ${s.toLocaleDateString()} ${s.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
      →
      ${e.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
    `;
}

function formatSeconds(seconds) {
    if (seconds === null || seconds === undefined) return "--";
    if (seconds <= 0) return "Expirado";

    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;

    return `${h}h ${m}m ${s}s`;
}

/* ================= DELETE ================= */
async function deleteCycle(cycleId) {
    const password = prompt(
        "⚠️ AÇÃO CRÍTICA\n\nDigite a senha para deletar este ciclo:"
    );

    if (!password) return;

    const res = await fetch(`/api/cycles/${cycleId}/delete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password })
    });

    if (!res.ok) {
        alert("❌ Senha incorreta ou erro ao deletar");
        return;
    }

    alert("✅ Ciclo deletado com sucesso");
    location.reload();
}
