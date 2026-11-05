document.addEventListener("DOMContentLoaded", function() {

    // Agrupa a data local de criação por semana, mês ou ano selecionado.
    function setupClientSideTemporalChart(canvasId, selectId, rawDataId, datasetLabel) {
        const canvas = document.getElementById(canvasId);
        const select = document.getElementById(selectId);
        const dataElem = document.getElementById(rawDataId);

        if (!canvas || !dataElem) return;

        const rawItems = JSON.parse(dataElem.textContent || '[]');

        // Agrupa os itens brutos do JSON nas faixas temporais correspondentes (Semana, Mês e Ano)
        function processData() {
            const now = new Date(`${canvas.dataset.today}T00:00:00`);

            const labelsWeek = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];
            const labelsMonth = ["Dias 1-7", "Dias 8-14", "Dias 15-21", "Dias 22-fim"];
            const labelsYear = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

            const weekTotal = new Array(7).fill(0);
            const monthTotal = new Array(4).fill(0);
            const yearTotal = new Array(12).fill(0);

            // Converte o índice padrão de dias do JS para o formato baseado em segunda-feira (0 = Segunda ... 6 = Domingo)
            function getMondayBasedDay(d) {
                let day = d.getDay();
                return day === 0 ? 6 : day - 1;
            }

            // Valida se uma determinada data cai dentro da semana atual
            function isCurrentWeek(d) {
                const curr = new Date(now);
                const firstday = new Date(curr.setDate(curr.getDate() - curr.getDay() + (curr.getDay() === 0 ? -6 : 1)));
                firstday.setHours(0,0,0,0);
                const lastday = new Date(firstday);
                lastday.setDate(lastday.getDate() + 6);
                lastday.setHours(23,59,59,999);
                return d >= firstday && d <= lastday;
            }

            // As datas vêm como YYYY-MM-DD no fuso da aplicação, sem conversão de fuso no navegador.
            rawItems.forEach(item => {
                const [year, month, day] = item.created_at.split('-').map(Number);
                const d = new Date(year, month - 1, day);

                // Processa e contabiliza os dados referentes ao período semanal
                if (isCurrentWeek(d)) {
                    let w = getMondayBasedDay(d);
                    weekTotal[w]++;
                }

                // Processa e contabiliza os dados referentes ao período mensal atual
                if (d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth()) {
                    const day = d.getDate();
                    const idx = Math.floor((day - 1) / 7);
                    monthTotal[idx]++;
                }

                // Processa e contabiliza os dados referentes ao período anual atual
                if (d.getFullYear() === now.getFullYear()) {
                    const m = d.getMonth();
                    yearTotal[m]++;
                }
            });

            // Retorna um objeto estruturado contendo os rótulos e os valores mapeados para cada período
            return {
                dates: { week: labelsWeek, month: labelsMonth, year: labelsYear },
                values: { week: weekTotal, month: monthTotal, year: yearTotal }
            };
        }

        const processed = processData();

        // Instancia o objeto Chart.js do tipo linha para a exibição visual dos dados
        let chart = new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: { labels: [], datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } }
            }
        });

        // Atualiza dinamicamente os datasets e rótulos do gráfico conforme o período temporal selecionado
        function updateChart(period) {
            chart.data.labels = processed.dates[period] || [];
            const val = processed.values[period] || [];

            chart.data.datasets = [
                { label: datasetLabel, data: val,
                    borderColor: '#007bff', backgroundColor: 'rgba(0,123,255,0.1)', fill: true }
            ];
            chart.update();
        }

        // Define o estado inicial do gráfico utilizando o ano como padrão
        updateChart(select ? select.value : 'year');

        // Adiciona um listener no elemento select para atualizar o gráfico sempre que o filtro de período mudar
        if (select) {
            select.addEventListener('change', (e) => updateChart(e.target.value));
        }
    }

    // Inicializa os gráficos temporais na página para Usuários, Grupos e Despesas
    setupClientSideTemporalChart('usersTemporalChart', 'usersTemporalSelect', 'users-json-data', 'Usuários cadastrados');
    setupClientSideTemporalChart('groupsChart', 'groupsSelect', 'groups-json-data', 'Grupos criados');
    setupClientSideTemporalChart('expenseChart', 'expenseSelect', 'expenses-json-data', 'Despesas cadastradas');

    // Constrói e renderiza o gráfico de barras para exibição de membros aceitos e pendentes
    const membershipCanvas = document.getElementById('membershipChart');
    if (membershipCanvas) {
        const accepted = parseInt(membershipCanvas.dataset.accepted || 0);
        const pending = parseInt(membershipCanvas.dataset.pending || 0);
        new Chart(membershipCanvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Membros Aceitos', 'Pendentes'],
                datasets: [{ label: 'Quantidade', data: [accepted, pending], 
                            backgroundColor: ['#007bff', '#ffc107'] }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
        });
    }

    // Constrói e renderiza o gráfico em rosca para exibição de faturas quitados e pendentes
    const splitCanvas = document.getElementById('splitsChart');
    if (splitCanvas) {
        const paid = parseInt(splitCanvas.dataset.paid || 0);
        const unpaid = parseInt(splitCanvas.dataset.unpaid || 0);
        new Chart(splitCanvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Quitadas', 'Pendentes'],
                datasets: [{ data: [paid, unpaid], backgroundColor: ['#17a2b8', '#ffc107'] }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // Configura o comportamento de redirecionamento e filtros na tela de divisão de despesas
    const expenseFilterSelect = document.getElementById('expenseFilterSelect');
    if (expenseFilterSelect) {
        expenseFilterSelect.addEventListener('change', function() {
            let url = new URL(window.location.href);
            if (this.value) {
                url.searchParams.set('expense_id', this.value);
            } else {
                url.searchParams.delete('expense_id');
            }
            window.location.href = url.toString();
        });
    }

    // Configura o comportamento de redirecionamento e filtros na tela de membros de grupos
    const groupFilterSelect = document.getElementById('groupFilterSelect');
    if (groupFilterSelect) {
        groupFilterSelect.addEventListener('change', function() {
            let url = new URL(window.location.href);
            if (this.value) {
                url.searchParams.set('group_id', this.value);
            } else {
                url.searchParams.delete('group_id');
            }
            window.location.href = url.toString();
        });
    }
});
