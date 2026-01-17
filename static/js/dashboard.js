document.addEventListener("DOMContentLoaded", () => {
    loadSummary();
    loadCharts();
    loadCycles();
});

function loadSummary() {
    document.getElementById("current-shift").innerText = "Turno 01 (12h)";
    document.getElementById("total-aa").innerText = 24;
    document.getElementById("total-items").innerText = 18450;
    document.getElementById("total-cycles").innerText = 6;
}

function loadCharts() {
    const aaCtx = document.getElementById("aaChart");
    new Chart(aaCtx, {
        type: "bar",
        data: {
            labels: ["AA01", "AA02", "AA03", "AA04"],
            datasets: [{
                label: "Itens Processados",
                data: [4500, 3800, 2900, 2100]
            }]
        }
    });

    const statusCtx = document.getElementById("statusChart");
    new Chart(statusCtx, {
        type: "doughnut",
        data: {
            labels: ["Aberto", "Em Contagem", "Fechado"],
            datasets: [{
                data: [3, 2, 1]
            }]
        }
    });
}

function loadCycles() {
    const table = document.getElementById("cycles-table");

    table.innerHTML = `
        <tr>
            <td>Turno 01</td>
            <td>15/01/2026 07:00 → 19:00</td>
            <td><span class="badge bg-warning">Aberto</span></td>
            <td>
                <a href="/cycle/123" class="btn btn-sm btn-primary">Abrir</a>
            </td>
        </tr>
        <tr>
            <td>Turno 02</td>
            <td>14/01/2026 19:00 → 07:00</td>
            <td><span class="badge bg-success">Fechado</span></td>
            <td>
                <a href="/cycle/122" class="btn btn-sm btn-secondary">Visualizar</a>
            </td>
        </tr>
    `;
}
